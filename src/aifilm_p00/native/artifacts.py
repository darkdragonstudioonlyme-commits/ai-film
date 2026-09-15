"""Protected, create-only native evidence snapshots under the fixed owner root.

Writes are part of the admitted operation's budget/intent. Object indices are
committed to the durable journal only after all referenced bytes are read back.
No self-pinning authority, source-plan overwrite, public raw dump or upload.
"""
from pathlib import PureWindowsPath
from datetime import datetime,timezone
from uuid import uuid4
from copy import deepcopy
from ..codec import canonical,loads,digest,sha256,relative,token
from ..errors import require,P00Error
from ..evidence_catalog import PROTECTED_PATHS
from ..evidence import record_check,COLLECTOR_CAP,BUNDLE_CAP
from .observations import file_presence


def owned_directory(paths,path,identity,coordinator):
    raw=canonical(identity);marker=str(PureWindowsPath(path)/'ownership.json')
    if file_presence(paths,path):
        with paths.pin(path,directory=True,protected=True):
            require(paths.read_blob(marker,cap=65536,expected=sha256(raw))==raw,16,'ARTIFACT_DIRECTORY_COLLISION')
        return False
    coordinator.storage.append_event({'kind':'OUTPUT_DIRECTORY_INTENT','path':path,'identity_digest':digest(identity),
                                       'plan_digest':coordinator.admission.plan_digest})
    paths.create_directory(path)
    paths.write_new(marker,raw)
    coordinator.storage.append_event({'kind':'OUTPUT_DIRECTORY_OBSERVED','path':path,'identity_digest':digest(identity),
                                      'plan_digest':coordinator.admission.plan_digest})
    return True


def output_scope(coordinator,paths):
    require(coordinator.held and coordinator.admission is not None and coordinator.fence is not None,12,'EVIDENCE_WRITE_ADMISSION')
    # RECONCILIATION_ONLY may write only explicit safe diagnostics in the original
    # approved output scope, never mutate/replace the original source or fence.
    require(coordinator.admission.purpose in ('PASSIVE','DISCOVERY','ENGINE','CREATE','ADOPT',
        'RESTORE_EXPORT','RESTORE_IMPORT','SITE_VERIFY','TARGET_LIFECYCLE','HOST_RESTART','RESTORE_VERIFY',
        'SUPPORT_BUNDLE','RECONCILIATION_ONLY'),12,'EVIDENCE_WRITE_SCOPE')
    parent=str(PureWindowsPath(paths.root)/'records')
    with paths.pin(parent,directory=True,protected=True):pass
    return parent


class SnapshotWriter:
    def __init__(self,paths,coordinator):self.paths=paths;self.c=coordinator
    def seal(self,plan,stage,groups,envelopes):
        from ..evidence_stage import encode_stage
        stage_context=encode_stage(stage)
        c=self.c;s=plan['semantic'];parent=output_scope(c,self.paths)
        require(set(groups)==set(envelopes) and set(groups)<={f'E00-{i:02d}' for i in range(1,16)},15,'SNAPSHOT_GROUP_SET')
        capture='capture-'+uuid4().hex;root=str(PureWindowsPath(parent)/capture)
        identity={'schema_version':1,'run_id':s['run_id'],'plan_digest':plan['plan_digest'],
                  'host_id':s['host_id'],'capture_id':capture,'contract_digest':s['contract_digest']}
        owned_directory(self.paths,root,identity,c)
        rows=[];total=0
        for folder in sorted({'envelopes',*(str(PureWindowsPath(PROTECTED_PATHS[e]).parent) for e in groups)}):
            owned_directory(self.paths,str(PureWindowsPath(root)/folder),{'capture':capture,'folder':folder},c)
        for eid,body in sorted(groups.items()):
            record=deepcopy(envelopes[eid]);rid=record['record_id'];token(rid)
            blob=canonical({'record_id':rid,'body':body});require(len(blob)<=COLLECTOR_CAP,22,'ACTUAL_RECORD_CAP')
            logical=PROTECTED_PATHS[eid]
            record['protected_ref']=s['run_id']+'/'+logical+'#'+rid
            record['protected_digest']=sha256(blob)
            record['actual_ref']=record['protected_ref'] if record['status'] in ('OBSERVED','PASS','ABSENT','FAIL') else None
            record_check(record)
            envelope=canonical(record);require(len(envelope)<=COLLECTOR_CAP,22,'ENVELOPE_CAP')
            total+=len(blob)+len(envelope);require(total<=BUNDLE_CAP,13,'SNAPSHOT_BUDGET_CAP')
            self.paths.write_new(str(PureWindowsPath(root)/logical),blob)
            require(self.paths.read_blob(str(PureWindowsPath(root)/logical),expected=sha256(blob))==blob,15,'ACTUAL_READBACK')
            meta='envelopes/'+eid+'.json'
            self.paths.write_new(str(PureWindowsPath(root)/meta),envelope)
            require(self.paths.read_blob(str(PureWindowsPath(root)/meta),expected=sha256(envelope))==envelope,15,'ENVELOPE_READBACK')
            rows.append({'evidence_id':eid,'relative_path':meta,'record_id':rid,'bytes':len(envelope),'sha256':sha256(envelope)})
        index={'schema_version':1,'run_id':s['run_id'],'records':rows,'stage_context':stage_context};encoded=canonical(index)
        self.paths.write_new(str(PureWindowsPath(root)/'index.json'),encoded)
        require(self.paths.read_blob(str(PureWindowsPath(root)/'index.json'),expected=sha256(encoded))==encoded,15,'INDEX_READBACK')
        with self.paths.pin(root,directory=True,protected=True) as actual_root:
            root_identity={'file_id':actual_root.identity['file_id'],'volume_serial':actual_root.identity['volume_serial']}
        result={'kind':'SNAPSHOT_COMMITTED','root_identity':root_identity,'host_id':s['host_id'],'plan_digest':plan['plan_digest'],
                'run_id':s['run_id'],'stage':stage.name,'stage_context':stage_context,'stage_digest':digest(stage_context),'source_kind':s['execution_class'],
                'root':root,'index_digest':sha256(encoded),'bytes':total+len(encoded),
                'captured_at':datetime.now(timezone.utc).isoformat(),'record_count':len(rows)}
        c.storage.append_event(result)
        return result


def committed_snapshot(paths,coordinator,selector):
    require(coordinator.held and type(selector) is dict and set(selector)=={'plan_digest','index_digest'},12,'SNAPSHOT_SELECTOR')
    selected=[r['event'] for r in coordinator.storage.read_events() if r['event'].get('kind')=='SNAPSHOT_COMMITTED'
              and r['event'].get('plan_digest')==selector['plan_digest'] and r['event'].get('index_digest')==selector['index_digest']]
    require(len(selected)==1,15,'SNAPSHOT_COMMIT_NOT_UNIQUE');row=selected[0]
    root=PureWindowsPath(row['root']);expected=PureWindowsPath(paths.root)/'records'
    require(root.parent==expected and root.name.startswith('capture-'),12,'SNAPSHOT_ROOT_SCOPE')
    with paths.pin(str(root),directory=True,protected=True) as pinned:
        require(row.get('root_identity')=={'file_id':pinned.identity['file_id'],'volume_serial':pinned.identity['volume_serial']},16,'SNAPSHOT_ROOT_REPLACED')
        index=loads(paths.read_blob(str(root/'index.json'),expected=row['index_digest']))
    require(index['run_id']==row['run_id'],15,'SNAPSHOT_RUN_MISMATCH')
    return row,index
