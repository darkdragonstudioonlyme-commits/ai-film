#!/usr/bin/env python3
import hashlib,json,os,stat,sys
from pathlib import Path
ROOT=Path('/home/dragon/ai-film-dev/artifacts/lab')
SEAL=ROOT/'LAB_ARTIFACT_SEAL_V1.json'
EXPECTED_CANDIDATE='336b12af-cada-4968-8083-8a5b41e479a2'
EXPECTED_SOURCE='934659f535d81d9a4a07389531acc2b9c304fa6d'
EXPECTED_BUNDLE='fa38540df54df9ebb87929c43e9fe8fbcd09e290e93d8c5d53d7af991df8f615'

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
    if seal.get('pending_bundle_index_sha256')!=EXPECTED_BUNDLE: fail('BUNDLE_DRIFT')
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
