"""Support bundle core. Filesystem/native snapshot IO belongs in the native adapter.
MemorySnapshot is a workspace test double only.
"""
from dataclasses import dataclass
from io import BytesIO
from pathlib import PurePosixPath
import hashlib,json,re,zipfile
from .codec import canonical,digest,hash_value,relpath
from .errors import require,P00Error

SECRET_KEY=re.compile(r'(?i)(secret|token|password|credential|api[_-]?key|private[_-]?key|cookie|authorization|bearer)')
URI_SECRET=re.compile(r'(?i)([?&](?:token|key|secret|password)=|://[^/@\s:]+:[^/@\s]+@)')
ENTROPY=re.compile(r'(?<![A-Za-z0-9_])(?:gh[pousr]_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|[A-Za-z0-9+/]{48,}={0,2})(?![A-Za-z0-9_])')
ALLOWED_VALUE_TYPES=(str,int,bool,type(None))

@dataclass(frozen=True)
class EvidenceRecord:
    evidence_id:str; instance_id:str; required:bool; public_value:object; protected_ref:str|None; source_kind:str

class MemorySnapshot:
    def __init__(self,records): self.records=list(records)
    def read(self): return list(self.records)


def _sanitize(value,path='root'):
    if isinstance(value,dict):
        out={}
        for k,v in value.items():
            require(isinstance(k,str),23,'REDACTION_UNPROVEN')
            if SECRET_KEY.search(k): continue
            out[k]=_sanitize(v,path+'.'+k)
        return out
    if isinstance(value,list): return [_sanitize(v,path+'[]') for v in value]
    require(isinstance(value,ALLOWED_VALUE_TYPES),23,'REDACTION_UNPROVEN')
    if isinstance(value,str):
        require('\x00' not in value and len(value)<=4096,23,'REDACTION_UNPROVEN')
        require(URI_SECRET.search(value) is None and ENTROPY.search(value) is None,23,'REDACTION_UNPROVEN')
    return value


def collect(snapshot,scope,required_ids,optional_ids,collector_outcomes,*,cap_bytes=4*1024*1024):
    require(scope in ('INVENTORY','FAILED_RUN','GATE_HANDOFF'),10,'BUNDLE_SCOPE')
    require(not (set(required_ids)&set(optional_ids)),10,'EVIDENCE_REQUIREDNESS_OVERLAP')
    require(set(collector_outcomes)<=set(required_ids)|set(optional_ids),10,'COLLECTOR_OUTCOME_UNKNOWN')
    records=snapshot.read(); seen=set(); public=[]; missing=[]; optional_failed=[]
    for item in records:
        require(isinstance(item,EvidenceRecord),15,'SNAPSHOT_RECORD_SCHEMA')
        key=(item.evidence_id,item.instance_id);require(key not in seen,15,'DUPLICATE_EVIDENCE_RECORD');seen.add(key)
        require(item.source_kind in ('SITE','LAB','DOCUMENT'),15,'EVIDENCE_SOURCE_KIND')
        relpath(item.evidence_id);relpath(item.instance_id)
        if item.evidence_id in required_ids|optional_ids:
            try: safe=_sanitize(item.public_value)
            except P00Error: raise
            public.append({'evidence_id':item.evidence_id,'instance_id':item.instance_id,'source_kind':item.source_kind,'value':safe,'protected_ref':item.protected_ref})
    for eid in required_ids:
        if not any(r['evidence_id']==eid for r in public) or collector_outcomes.get(eid)!='PASS': missing.append(eid)
    for eid in optional_ids:
        if collector_outcomes.get(eid) not in (None,'PASS'): optional_failed.append(eid)
    public.sort(key=lambda r:(r['evidence_id'],r['instance_id']))
    body={'schema_version':1,'scope':scope,'records':public,'collector_outcomes':collector_outcomes,'missing_mandatory':sorted(missing),'optional_failed':sorted(optional_failed),'host_ready':False}
    blob=canonical(body)
    if missing: return {'exit':22,'status':'INCOMPLETE_MANDATORY','completeness':'MANDATORY_MISSING','gate_eligible':False,'bundle':body}
    require(len(blob)<=cap_bytes,22,'MANDATORY_OUTPUT_CAP')
    status='PARTIAL_OPTIONAL' if optional_failed else 'COMPLETE'; exit_code=2 if optional_failed else 0
    return {'exit':exit_code,'status':status,'completeness':'OPTIONAL_PARTIAL' if optional_failed else 'COMPLETE','gate_eligible':False,'bundle':body}


def zip_bundle(result):
    """Deterministic in-memory archive. Publisher is a separate create-only adapter."""
    report=result['bundle']; data=canonical(report)
    manifest={'schema_version':1,'members':[{'path':'collection-report.json','sha256':hashlib.sha256(data).hexdigest(),'size':len(data)}],'bundle_digest':digest(report)}
    manifest_data=canonical(manifest)
    out=BytesIO()
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for path,payload in [('collection-report.json',data),('manifest.json',manifest_data)]:
            info=zipfile.ZipInfo(path,date_time=(1980,1,1,0,0,0));info.external_attr=0o600<<16;info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,payload)
    blob=out.getvalue()
    return blob,hashlib.sha256(blob).hexdigest()
