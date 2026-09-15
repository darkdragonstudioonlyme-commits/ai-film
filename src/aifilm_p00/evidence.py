"""D00-14 evidence schemas and in-memory safe bundle assembly.
Scope completeness is separate from phase readiness. The native snapshot reader,
ACL-aware publisher and MASTER assessment integration are NOT implemented yet.
"""
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from zipfile import ZipFile,ZIP_DEFLATED
from .codec import canonical,sha256,fields,hash_value,token,integer,instant,digest
from .errors import P00Error,require

COLLECTOR_CAP=10*1024**2
BUNDLE_CAP=100*1024**2
PATHS={
 'E00-01':'host','E00-02':'runtime','E00-03':'distros','E00-04':'guest',
 'E00-05':'resources','E00-06':'storage','E00-07':'config','E00-08':'network',
 'E00-09':'source_manifest','E00-10':'execution_binding','E00-11':'admission',
 'E00-12':'c3_protection','E00-13':'qualification','E00-14':'terminal','E00-15':'restore',
}
STATUSES={'PASS','FAIL','BLOCKED','NOT_RUN','NOT_YET_CREATED','REQUIRES_ACTIVE_PROBE','UNKNOWN','UNAVAILABLE','NOT_APPLICABLE','OBSERVED','ABSENT'}
ROLES={'DOCUMENT','LAB','SITE'}
RECORD_FIELDS={'schema_version','evidence_id','record_id','status','source_kind','work_item','run_id','step_id','operation','host_alias','target_alias','collector_digest','build_digest','contract_digest','timestamp_utc','stage','route','expected_ref','actual_ref','native_exit','normalized_exit','epoch_ref','protected_ref','protected_digest','safe_summary','sensitivity'}

@dataclass(frozen=True)
class Collected:
    evidence_id:str
    record:dict|None
    expected_bytes_digest:str|None
    duration_ms:int=0
    bytes_seen:int=0
    eof:bool=True
    status:str='COMPLETE'
    protected_access:bool=False
    protected_integrity:bool=False

@dataclass(frozen=True)
class Bundle:
    exit:int
    outcome:str
    mandatory_complete:bool
    component_eligible:bool
    archive:bytes|None
    report:dict

def record_check(record:dict):
    fields(record,RECORD_FIELDS)
    require(record['schema_version']==1 and record['evidence_id'] in PATHS,10,'EVIDENCE_SCHEMA')
    require(record['status'] in STATUSES and record['source_kind'] in ROLES,10,'EVIDENCE_STATUS')
    for key in ('record_id','work_item','run_id','step_id','operation','host_alias','target_alias','stage','route'): token(record[key])
    for key in ('collector_digest','build_digest','contract_digest','protected_digest'): hash_value(record[key])
    instant(record['timestamp_utc'])
    for key in ('expected_ref','actual_ref','epoch_ref','protected_ref'):
        require(record[key] is None or type(record[key]) is str,10,'EVIDENCE_REFERENCE')
    require(record['sensitivity'] in ('SAFE','PROTECTED'),10,'SENSITIVITY_REQUIRED')
    require(type(record['safe_summary']) is dict,10,'SUMMARY_OBJECT_REQUIRED')
    require(record['native_exit'] is None or type(record['native_exit']) is int,10,'NATIVE_EXIT_INVALID')
    integer(record['normalized_exit'],0,255)

# Narrow allowlist: unknown strings or keys are never forwarded as diagnostics.
# Known raw diagnostics are suppressed wholesale instead of regex-scrubbing stderr.
REDACT_KEYS={'password','token','secret','credential','private_key','stderr','message','error_message','raw','environment','query','userinfo','command_line'}
ALIAS_KEYS={'path','sid','url','endpoint','owner','name','host','target','record_id','resource_id'}
HASH_KEYS={'digest','sha256','checkpoint_digest','config_digest','evidence_digest','epoch_digest','build_digest','contract_digest','plan_digest','manifest_digest'}
BOOL_KEYS={'passed','eligible','complete','owner_match','home_writable','admin_ready','startup_known','no_pending_writer','retained','scan_pass','trusted','witnesses_valid','eof'}
INT_KEYS={'count','bytes','free_bytes','peak_bytes','reserve_bytes','duration_ms','logical_cpu','installed_ram_bytes','available_ram_bytes','mem_total_bytes','mem_available_bytes','fs_available_bytes','uid','gid','mode','normalized_exit','native_exit'}
STRUCT_KEYS={'assertions','results','volumes','errors','items','measurements','network','resource','details','values'}
ENUM_KEYS={'status','source_kind','class','kind','context','purpose','code','category'}
ENUM_VALUES=STATUSES|ROLES|{'C0','C1','C2','C3','WINDOWS','GUEST','DOCUMENT','SAFE','PROTECTED','SITE_VERIFY','RESTORE','DISCOVERY','ENGINE','CREATE','ADOPT','RESTORE_EXPORT','RESTORE_IMPORT','COMPLETE','INCOMPLETE','TIMEOUT','TRUNCATED','NETWORK','RESOURCE','INPUT','PERMISSION','INTEGRITY','IO','REDACTED','MISSING','NATIVE','NOT_GATE','NOT_ISOLATION_SANDBOX'}

class Sanitizer:
    def __init__(self,salt:bytes):
        require(type(salt) is bytes and len(salt)>=16,10,'ALIAS_SALT_REQUIRED')
        self.salt=salt; self.alias_map={}
    def alias(self,value):
        opaque='a_'+sha256(self.salt+canonical(value))[:24]
        self.alias_map[opaque]=value
        return opaque
    def summary(self,obj,depth=0):
        require(depth<=20,23,'REDACTION_DEPTH')
        require(type(obj) is dict,23,'UNSAFE_SUMMARY_STRUCTURE')
        safe={}
        for key,value in obj.items():
            if key in REDACT_KEYS:
                safe[key]='[REDACTED]'
            elif key in ALIAS_KEYS:
                safe[key]=self.alias(value)
            elif key in HASH_KEYS:
                try: hash_value(value)
                except P00Error: raise P00Error(23,'UNSAFE_HASH_FIELD') from None
                safe[key]=value
            elif key in BOOL_KEYS:
                require(type(value) is bool,23,'UNSAFE_BOOLEAN_FIELD'); safe[key]=value
            elif key in INT_KEYS:
                require(type(value) is int and -2**31<=value<=2**63-1,23,'UNSAFE_NUMBER_FIELD'); safe[key]=value
            elif key in ENUM_KEYS:
                require(type(value) is str and value in ENUM_VALUES,23,'UNSAFE_ENUM_FIELD'); safe[key]=value
            elif key in STRUCT_KEYS:
                if isinstance(value,list):
                    require(len(value)<=10000,23,'REDACTION_ITEMS')
                    safe[key]=[self.summary(x,depth+1) for x in value]
                else: safe[key]=self.summary(value,depth+1)
            else:
                raise P00Error(23,'UNALLOWLISTED_FIELD')
        return safe
    def record(self,record):
        # No protected raw reference, source SID, path, or alias map goes into the archive.
        return {'schema_version':1,'evidence_id':record['evidence_id'],
                'record_alias':self.alias(record['record_id']), 'host_alias':self.alias(record['host_alias']),
                'target_alias':self.alias(record['target_alias']), 'status':record['status'],
                'source_kind':record['source_kind'],'timestamp_utc':record['timestamp_utc'],
                'build_digest':record['build_digest'],'contract_digest':record['contract_digest'],
                'protected_artifact_alias':self.alias(record['protected_ref']),
                'protected_digest':record['protected_digest'],
                'summary':self.summary(record['safe_summary'])}

def requiredness(scope:str,*,persistent_output=True,mutation_attempted=False,c3_attempted=False,restore_attempted=False):
    require(scope in ('INVENTORY','FAILED_RUN','GATE_HANDOFF'),10,'BUNDLE_SCOPE_REQUIRED')
    if scope=='GATE_HANDOFF': return set(PATHS)
    if scope=='INVENTORY': return {f'E00-{n:02d}' for n in range(1,11)}|({'E00-11'} if persistent_output else set())
    needed={'E00-10'}
    if mutation_attempted: needed.add('E00-11')
    if c3_attempted: needed.add('E00-12')
    if restore_attempted: needed.add('E00-15')
    return needed

def complete_for_scope(record,scope):
    status=record['status']; eid=record['evidence_id']
    if scope=='GATE_HANDOFF':
        # Conditional subfields are handled in the substantive host catalog integration;
        # this core requires PASS per group and does not invent group-wide N/A waivers.
        allowed={'SITE'} if eid not in {'E00-10','E00-13','E00-15'} else ({'LAB','DOCUMENT'} if eid=='E00-13' else {'SITE','LAB','DOCUMENT'})
        return status=='PASS' and record['actual_ref'] is not None and record['source_kind'] in allowed
    if scope=='INVENTORY':
        if eid in {'E00-04','E00-08','E00-09'}:
            return status in STATUSES-{'FAIL','NOT_RUN'}
        return status in {'OBSERVED','PASS','ABSENT'}
    return status in STATUSES-{'NOT_RUN'}


def assemble(scope:str,records:list[Collected],sanitizer:Sanitizer,*,context:dict,optional_ids:frozenset[str]=frozenset(),scanner=None,bundle_cap=BUNDLE_CAP)->Bundle:
    """Pure bytes-in/bytes-out. No filesystem access, collector side effect or upload.
    The caller must have authorized/locked native snapshot I/O before using this core.
    """
    needed=requiredness(scope,**context)
    require(not needed&set(optional_ids),10,'MANDATORY_CANNOT_BECOME_OPTIONAL')
    require(type(bundle_cap) is int and 1024<=bundle_cap<=BUNDLE_CAP,10,'BUNDLE_CAP_INVALID')
    byid={}; bad_integrity=False; privacy=False; missing=[]; optional_fail=[]; reasons=[]; members={}
    for c in records:
        require(c.evidence_id in PATHS and c.evidence_id not in byid,10,'EVIDENCE_ID_DUPLICATE_OR_INVALID')
        byid[c.evidence_id]=c
    require(set(byid)<=needed|set(optional_ids),10,'UNDECLARED_COLLECTOR')
    for eid in sorted(needed|set(optional_ids)):
        c=byid.get(eid); failure=None
        if c is not None and c.status=='INTEGRITY_FAILURE':bad_integrity=True
        if c is not None and c.status=='PRIVACY_FAILURE':privacy=True
        if c is None or c.record is None: failure='MISSING'
        else:
            integer(c.duration_ms); integer(c.bytes_seen)
            if c.duration_ms>30000: failure='TIMEOUT'
            if c.status!='COMPLETE': failure='INCOMPLETE'
            if c.bytes_seen>COLLECTOR_CAP or not c.eof: failure='TRUNCATED'
            raw=canonical(c.record)
            if len(raw)>COLLECTOR_CAP: failure='TRUNCATED'
            if c.expected_bytes_digest!=sha256(raw) or not c.protected_integrity: bad_integrity=True
            try:
                record_check(c.record)
                require(c.record['evidence_id']==eid,15,'EVIDENCE_ID_MISMATCH')
                safe=sanitizer.record(c.record)
                encoded=canonical(safe)
                try:
                    if scanner is None or scanner(encoded) is not True: privacy=True
                except Exception:
                    privacy=True
                if not privacy: members['summaries/'+PATHS[eid]+'.json']=encoded
            except P00Error as error:
                if error.code==23: privacy=True
                else: bad_integrity=True
            if not c.protected_access: failure='PROTECTED_UNAVAILABLE'
            if not complete_for_scope(c.record,scope): failure='SEMANTIC_INCOMPLETE'
        if failure:
            (missing if eid in needed else optional_fail).append(eid)
            reasons.append({'evidence_id':eid,'reason':failure})
    report={'scope':scope,'mandatory_complete':not missing,'component_eligible':scope=='GATE_HANDOFF' and not missing,
            'inventory_complete':scope=='INVENTORY' and not missing,'missing':missing,'optional_failures':optional_fail,
            'collector_reasons':reasons,'host_ready':False,'master_acceptance':False}
    if privacy: return Bundle(23,'BLOCKED_REDACTION',False,False,None,{'outcome':'BLOCKED_REDACTION','host_ready':False})
    if bad_integrity: return Bundle(15,'FAILED_INTEGRITY',False,False,None,{'outcome':'FAILED_INTEGRITY','host_ready':False})
    code=22 if missing else 2 if optional_fail else 0
    outcome={0:'COMPLETE',2:'PARTIAL_OPTIONAL',22:'INCOMPLETE_MANDATORY'}[code]
    report.update({'exit':code,'outcome':outcome,'scan':'PASS','scanner_contract':'STRICT_SAFE_SCHEMA_PLUS_CALLER_SCAN'})
    members['support/collection_report.json']=canonical(report)
    member_manifest={'schema_version':1,'members':[{'path':p,'bytes':len(b),'sha256':sha256(b)} for p,b in sorted(members.items())]}
    members['member_manifest.json']=canonical(member_manifest)
    if sum(len(b) for b in members.values())>bundle_cap:
        return Bundle(22,'INCOMPLETE_MANDATORY',False,False,None,{'outcome':'INCOMPLETE_MANDATORY','reason':'AGGREGATE_CAP','host_ready':False})
    out=BytesIO()
    with ZipFile(out,'w',ZIP_DEFLATED) as z:
        for name,data in sorted(members.items()): z.writestr(name,data)
    if len(out.getvalue())>bundle_cap:
        return Bundle(22,'INCOMPLETE_MANDATORY',False,False,None,{'outcome':'INCOMPLETE_MANDATORY','reason':'AGGREGATE_CAP','host_ready':False})
    return Bundle(code,outcome,not missing,report['component_eligible'],out.getvalue(),report)


def _bundle_integrity(archive:bytes):
    from .codec import loads,relative
    with ZipFile(BytesIO(archive)) as z:
        names=z.namelist()
        require(len(names)==len(set(names)) and 'member_manifest.json' in names,15,'BUNDLE_MEMBERS_INVALID')
        require(sum(i.file_size for i in z.infolist())<=BUNDLE_CAP and len(names)<=100,15,'BUNDLE_SIZE_LIMIT')
        manifest=loads(z.read('member_manifest.json'))
        listed={r['path'] for r in manifest['members']}
        require(listed==set(names)-{'member_manifest.json'} and len(listed)==len(manifest['members']),15,'BUNDLE_MEMBER_SET')
        for row in manifest['members']:
            relative(row['path']); data=z.read(row['path'])
            require(len(data)==row['bytes'] and sha256(data)==row['sha256'],15,'BUNDLE_MEMBER_HASH')
        require(all('gate_assessment' not in name for name in names),15,'GATE_SELF_REFERENCE')
        return {'sha256':sha256(archive),'members':len(listed),'integrity':True,'host_ready':False}


def bundle_integrity(archive:bytes):
    from zipfile import BadZipFile
    from zlib import error as ZlibError
    try:
        return _bundle_integrity(archive)
    except P00Error: raise
    except (BadZipFile,ZlibError,KeyError,TypeError,ValueError,RuntimeError):
        raise P00Error(15,'BUNDLE_INVALID') from None
