#!/usr/bin/env python3
"""Verify a candidate-bound LAB artifact seal without native execution."""
from __future__ import annotations
import argparse,hashlib,json,stat
from pathlib import Path
from v02_candidate_profile import ProfileError,load_profile

class SealError(RuntimeError):pass
def require(c,r):
    if not c: raise SealError(r)
def h(path):
    d=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(4*1024*1024),b''):d.update(chunk)
    return d.hexdigest()

def verify(binding,binding_sha256,root,seal_name='LAB_ARTIFACT_SEAL_V1.json'):
    profile,profile_sha=load_profile(binding,binding_sha256);root=Path(root);seal=root/seal_name
    require(seal.is_file() and not seal.is_symlink(),'SEAL_UNREADABLE')
    v=json.loads(seal.read_text())
    require(v.get('candidate_id')==profile['candidate_id'],'CANDIDATE_DRIFT')
    require(v.get('source_commit')==profile['source_commit'],'SOURCE_DRIFT')
    require(v.get('candidate_binding_sha256')==profile_sha,'CANDIDATE_BINDING_DRIFT')
    require(v.get('pristine_restore_probe')=='PASS','RESTORE_PROBE_NOT_PASS')
    rows=v.get('artifacts');require(isinstance(rows,list) and rows,'ARTIFACT_ROWS_INVALID');seen=set()
    for row in rows:
        name=row.get('name');require(isinstance(name,str) and name and name not in seen,'ARTIFACT_DUPLICATE')
        require('/' not in name and '\\' not in name and name not in ('.','..'),'ARTIFACT_NAME');seen.add(name)
        p=root/name;require(p.is_file() and not p.is_symlink(),'ARTIFACT_MISSING')
        st=p.stat();mode=stat.S_IMODE(st.st_mode);require(not(mode&0o222),'ARTIFACT_WRITABLE')
        require(st.st_size==row.get('bytes'),'ARTIFACT_SIZE_DRIFT');require(h(p)==row.get('sha256'),'ARTIFACT_HASH_DRIFT')
    require(not(stat.S_IMODE(seal.stat().st_mode)&0o222),'SEAL_WRITABLE')
    return {'kind':'P00_LAB_ARTIFACT_SEAL_VERIFY_V2','status':'PASS','artifact_count':len(rows),
            'candidate_id':profile['candidate_id'],'candidate_profile_sha256':profile_sha,
            'source_commit':profile['source_commit'],'seal_sha256':h(seal),'native_execution_started':False}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--binding',required=True);ap.add_argument('--binding-sha256',required=True)
    ap.add_argument('--root',required=True);ap.add_argument('--seal-name',default='LAB_ARTIFACT_SEAL_V1.json');a=ap.parse_args()
    try:o=verify(a.binding,a.binding_sha256,a.root,a.seal_name);rc=0
    except (ProfileError,SealError,OSError,ValueError,json.JSONDecodeError) as e:
        o={'kind':'P00_LAB_ARTIFACT_SEAL_VERIFY_V2','status':'FAIL','reason':str(e),'native_execution_started':False};rc=1
    print(json.dumps(o,sort_keys=True,separators=(',',':')));return rc
if __name__=='__main__':raise SystemExit(main())
