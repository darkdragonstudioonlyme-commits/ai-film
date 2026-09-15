"""ACL-aware immutable snapshot reader and write-through safe bundle publisher.

No live collector is launched here. Expected digests and approved roots come from
an authenticated snapshot binding; this is not a facility to archive arbitrary
paths. Final gate evaluation remains separate from bundle assembly.
"""
from __future__ import annotations
from pathlib import PureWindowsPath
import re
import time
from ..codec import loads,canonical,sha256,relative,hash_value,token,instant,digest
from ..errors import require,P00Error
from ..evidence import (Collected,Sanitizer,assemble,bundle_integrity,PATHS,COLLECTOR_CAP,
    REDACT_KEYS,ALIAS_KEYS,HASH_KEYS,BOOL_KEYS,INT_KEYS,STRUCT_KEYS,ENUM_KEYS,ENUM_VALUES)
from ..policy import budget_check


def logical_ref(value):
    require(type(value) is str and value.count('#')==1,15,'LOGICAL_REFERENCE')
    filepart,record_id=value.split('#')
    require('/' in filepart,15,'LOGICAL_REFERENCE')
    run_id,path=filepart.split('/',1);token(run_id);relative(path);token(record_id)
    return run_id,path,record_id


def extract_record(blob,record_id):
    data=loads(blob)
    if type(data) is dict and data.get('record_id')==record_id:return data
    require(type(data) is dict and set(data)=={'records'} and type(data['records']) is list,15,'RECORD_CONTAINER')
    matches=[r for r in data['records'] if type(r) is dict and r.get('record_id')==record_id]
    require(len(matches)==1,15,'RECORD_SELECTION')
    return matches[0]


class SnapshotReader:
    def __init__(self,paths,guard,approved_root):
        self.paths=paths;self.guard=guard;self.root=approved_root
    def read(self,index,expected_index_digest,*,run_id):
        require(self.guard.held,18,'GUARD_NOT_HELD')
        require(sha256(canonical(index))==expected_index_digest,15,'SNAPSHOT_INDEX_HASH')
        require(type(index) is dict and set(index)=={'schema_version','run_id','records'} and index['schema_version']==1
                and index['run_id']==run_id and type(index['records']) is list,15,'SNAPSHOT_INDEX_SCHEMA')
        require(len(index['records'])<=15,15,'SNAPSHOT_RECORD_CAP')
        collected=[];seen=set()
        with self.paths.pin(self.root,directory=True,protected=True):
            for row in index['records']:
                start=time.monotonic()
                require(type(row) is dict and set(row)=={'evidence_id','relative_path','record_id','bytes','sha256'},15,'SNAPSHOT_ROW')
                eid=row['evidence_id'];require(eid in PATHS and eid not in seen,15,'SNAPSHOT_DUPLICATE');seen.add(eid)
                relative(row['relative_path']);token(row['record_id']);hash_value(row['sha256'])
                require(type(row['bytes']) is int and 0<row['bytes']<=COLLECTOR_CAP,22,'SNAPSHOT_MEMBER_CAP')
                path=str(PureWindowsPath(self.root)/row['relative_path'])
                blob=self.paths.read_blob(path,cap=COLLECTOR_CAP,expected=row['sha256'])
                require(len(blob)==row['bytes'],15,'SNAPSHOT_MEMBER_SIZE')
                record=extract_record(blob,row['record_id'])
                require(record.get('run_id')==run_id and record.get('evidence_id')==eid,15,'SNAPSHOT_RECORD_SCOPE')
                rr,actual_path,actual_id=logical_ref(record['protected_ref'])
                require(rr==run_id,15,'SNAPSHOT_PROTECTED_RUN')
                # A successful path read + actual hash check is what earns the
                # access/integrity flags. They are never copied from input JSON.
                actual_blob=self.paths.read_blob(str(PureWindowsPath(self.root)/actual_path),
                                                 cap=COLLECTOR_CAP,expected=record['protected_digest'])
                extract_record(actual_blob,actual_id)
                elapsed=int((time.monotonic()-start)*1000)
                encoded=canonical(record)
                collected.append(Collected(eid,record,sha256(encoded),elapsed,len(blob),True,
                                           'COMPLETE' if elapsed<=30000 else 'TIMEOUT',True,True))
        return collected


def _summary_safe(value,depth=0):
    if type(value) is not dict or depth>20:return False
    for k,v in value.items():
        if k in REDACT_KEYS:
            if v!='[REDACTED]':return False
        elif k in ALIAS_KEYS:
            if type(v) is not str or re.fullmatch(r'a_[0-9a-f]{24}',v) is None:return False
        elif k in HASH_KEYS:
            if type(v) is not str or re.fullmatch(r'[0-9a-f]{64}',v) is None:return False
        elif k in BOOL_KEYS:
            if type(v) is not bool:return False
        elif k in INT_KEYS:
            if type(v) is not int or not -2**31<=v<=2**63-1:return False
        elif k in ENUM_KEYS:
            if type(v) is not str or v not in ENUM_VALUES:return False
        elif k in STRUCT_KEYS:
            if type(v) is list:
                if len(v)>10000 or not all(_summary_safe(x,depth+1) for x in v):return False
            elif not _summary_safe(v,depth+1):return False
        else:return False
    return True


def strict_safe_scan(raw):
    """Independent structure checks; no claim of detecting arbitrary novel secrets."""
    try:
        value=loads(raw)
        required={'schema_version','evidence_id','record_alias','host_alias','target_alias','status',
                  'source_kind','timestamp_utc','build_digest','contract_digest','protected_artifact_alias',
                  'protected_digest','summary'}
        if type(value) is not dict or set(value)!=required or value['schema_version']!=1:return False
        if value['evidence_id'] not in PATHS or value['status'] not in ENUM_VALUES or value['source_kind'] not in {'SITE','LAB','DOCUMENT'}:return False
        instant(value['timestamp_utc'])
        for k in ('build_digest','contract_digest','protected_digest'):hash_value(value[k])
        for k in ('record_alias','host_alias','target_alias','protected_artifact_alias'):
            if type(value[k]) is not str or re.fullmatch(r'a_[0-9a-f]{24}',value[k]) is None:return False
        return _summary_safe(value['summary'])
    except (P00Error,TypeError,KeyError):return False


class NativeBundlePublisher:
    def __init__(self,paths,coordinator):self.paths=paths;self.coordinator=coordinator
    def publish(self,bundle,*,approved_path,budgets,free_by_volume):
        c=self.coordinator
        require(c.held and c.admission is not None and c.admission.purpose=='SUPPORT_BUNDLE'
                and c.fence is not None and c.fence['action']=='PUBLISH_SAFE_BUNDLE',12,'PUBLISH_ADMISSION_REQUIRED')
        budget_check(budgets,free_by_volume)
        if bundle.archive is None:
            require(bundle.exit in (15,22,23),15,'BUNDLE_NO_ARCHIVE_OUTCOME')
            require(not self.paths.file_exists(approved_path),16,'PUBLISH_UNEXPECTED_FINAL')
            publication={'path':approved_path,'temp_path':None,'sha256':None,'bytes':0,
                         'exit':bundle.exit,'outcome':bundle.outcome,'archive_expected':False,
                         'component_eligible':False}
            c.storage.append_event({'kind':'BUNDLE_PUBLISH_INTENT',
                'plan_digest':c.admission.plan_digest,'publication':publication,
                'publication_digest':digest(publication)})
            return {'exit':bundle.exit,'outcome':bundle.outcome,'published':False,
                    'archive_expected':False,'component_eligible':False,'host_ready':False}
        require(bundle.exit in (0,2,22),23,'BUNDLE_NOT_PUBLISHABLE')
        require(approved_path.endswith('.incomplete.zip') if bundle.exit==22 else approved_path.endswith('.zip') and not approved_path.endswith('.incomplete.zip'),10,'BUNDLE_OUTPUT_SUFFIX')
        checked=bundle_integrity(bundle.archive)
        from .publication_recovery import staged_output_path
        temp_path=staged_output_path(approved_path,c.admission.plan_digest,checked['sha256'],'bundle')
        publication={'path':approved_path,'temp_path':temp_path,'sha256':checked['sha256'],'bytes':len(bundle.archive),
                     'exit':bundle.exit,'outcome':bundle.outcome,'archive_expected':True,
                     'component_eligible':bundle.component_eligible}
        c.storage.append_event({'kind':'BUNDLE_PUBLISH_INTENT',
            'plan_digest':c.admission.plan_digest,'publication':publication,
            'publication_digest':digest(publication)})
        try:self.paths.publish_new(approved_path,bundle.archive,pending_path=temp_path)
        except P00Error as e:
            if e.code in (12,15,16):raise
            return {'exit':18,'outcome':'FAILED_OUTPUT','published':False,'host_ready':False}
        return {'exit':bundle.exit,'outcome':bundle.outcome,'published':True,'bundle_digest':checked['sha256'],
                'component_eligible':bundle.component_eligible,'host_ready':False}
