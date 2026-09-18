#!/usr/bin/env python3
import hashlib,json,os,stat,sys
from pathlib import Path
ROOT=Path('/home/dragon/ai-film-dev/artifacts/lab')
SEAL=ROOT/'LAB_ARTIFACT_SEAL_V1.json'
EXPECTED_CANDIDATE='6f895394-e0b4-5434-bebc-79ee4e576282'
EXPECTED_SOURCE='86bb64938a136e3f8d6cfd0266685a01cb832b77'
EXPECTED_BINDING='4aaf09ec2ef8618a5680e147cd2eeac695f940d45ae5cb0446c7b7e5c2483384'

def h(path):
    d=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(4*1024*1024),b''): d.update(chunk)
    return d.hexdigest()

def fail(reason,**extra):
    print(json.dumps({'kind':'P00_LAB_ARTIFACT_SEAL_VERIFY','status':'FAIL','reason':reason,**extra},sort_keys=True,separators=(',',':')))
    raise SystemExit(1)

def main():
    try: seal=json.loads(SEAL.read_text())
    except Exception: fail('SEAL_UNREADABLE')
    if seal.get('candidate_id')!=EXPECTED_CANDIDATE: fail('CANDIDATE_DRIFT')
    if seal.get('source_commit')!=EXPECTED_SOURCE: fail('SOURCE_DRIFT')
    if seal.get('candidate_binding_sha256')!=EXPECTED_BINDING: fail('CANDIDATE_BINDING_DRIFT')
    if seal.get('pristine_restore_probe')!='PASS': fail('RESTORE_PROBE_NOT_PASS')
    rows=seal.get('artifacts')
    if not isinstance(rows,list) or not rows: fail('ARTIFACT_ROWS_INVALID')
    seen=set()
    for row in rows:
        name=row.get('name'); path=ROOT/name if isinstance(name,str) else None
        if not name or name in seen or not path.is_file(): fail('ARTIFACT_MISSING_OR_DUPLICATE',name=name)
        seen.add(name)
        st=path.stat(); mode=stat.S_IMODE(st.st_mode)
        if mode & 0o222: fail('ARTIFACT_WRITABLE',name=name,mode=oct(mode))
        if st.st_size!=row.get('bytes'): fail('ARTIFACT_SIZE_DRIFT',name=name)
        if h(path)!=row.get('sha256'): fail('ARTIFACT_HASH_DRIFT',name=name)
    seal_mode=stat.S_IMODE(SEAL.stat().st_mode)
    if seal_mode & 0o222: fail('SEAL_WRITABLE',mode=oct(seal_mode))
    print(json.dumps({'kind':'P00_LAB_ARTIFACT_SEAL_VERIFY','status':'PASS',
        'artifact_count':len(rows),'candidate_id':EXPECTED_CANDIDATE,
        'seal_sha256':h(SEAL),'native_execution_started':False},
        sort_keys=True,separators=(',',':')))

if __name__=='__main__': main()
