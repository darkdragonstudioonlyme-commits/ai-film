#!/usr/bin/env python3
"""Read-only candidate-generic V02 preflight. No implicit candidate/inbox selection."""
from __future__ import annotations
import argparse,hashlib,json,os,stat,subprocess
from pathlib import Path
from v02_candidate_profile import ProfileError,load_profile

TOOL=Path(__file__).resolve().parent
VALIDATOR=TOOL/'v02-authority-intake-v2.py'

def file_sha256(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def snapshot(root):
    out={}
    if not root.exists(): return out
    for p in sorted(root.rglob('*')):
        rel=p.relative_to(root).as_posix()
        try:
            st=p.lstat();mode=stat.S_IFMT(st.st_mode)
            if p.is_symlink(): out[rel]=('symlink',os.readlink(p),mode,st.st_size,st.st_mtime_ns)
            elif p.is_dir(): out[rel]=('dir',mode,st.st_mtime_ns)
            elif p.is_file(): out[rel]=('file',mode,st.st_size,st.st_mtime_ns,file_sha256(p))
            else: out[rel]=('other',mode,st.st_size,st.st_mtime_ns)
        except OSError: out[rel]=('unreadable',)
    return out

def preflight(binding,binding_sha256,inbox,validator=VALIDATOR):
    profile,profile_sha=load_profile(binding,binding_sha256)
    root=Path(inbox); before=snapshot(root)
    env={'HOME':os.environ.get('HOME','/home/dragon'),'USER':os.environ.get('USER','dragon'),
         'LOGNAME':os.environ.get('LOGNAME','dragon'),'LANG':'C.UTF-8','LC_ALL':'C.UTF-8',
         'PATH':'/usr/bin:/bin','PYTHONNOUSERSITE':'1','PYTHONDONTWRITEBYTECODE':'1'}
    p=subprocess.run(['/usr/bin/python3',str(validator),'--binding',str(binding),
                      '--binding-sha256',profile_sha,'--inbox',str(root)],
                     text=True,capture_output=True,env=env)
    after=snapshot(root)
    if before!=after:
        return {'kind':'V02_AUTHORITY_PREFLIGHT_V2','status':'FAIL','reason':'PREFLIGHT_MUTATED_STAGING',
                'ready_for_intake':False,'staging_unchanged':False,'native_execution_started':False},3
    try:v=json.loads((p.stdout.strip().splitlines() or ['{}'])[-1])
    except Exception:
        return {'kind':'V02_AUTHORITY_PREFLIGHT_V2','status':'FAIL','reason':'VALIDATOR_OUTPUT_UNREADABLE',
                'ready_for_intake':False,'staging_unchanged':True,'native_execution_started':False},4
    ready=p.returncode==0 and v.get('status')=='READY_TO_ADVANCE' and v.get('ready_to_advance') is True
    if ready: status='READY_FOR_INTAKE'; reason=None; rc=0
    elif v.get('reason')=='APPROVAL_ENVELOPE_MISSING': status='MISSING';reason=v.get('reason');rc=10
    else: status='INVALID';reason=v.get('reason');rc=11
    return {'kind':'V02_AUTHORITY_PREFLIGHT_V2','status':status,'reason':reason,'ready_for_intake':ready,
            'candidate_id':profile['candidate_id'],'candidate_profile_sha256':profile_sha,
            'source_commit':profile['source_commit'],'case_count':v.get('case_count'),
            'authorized_plan_count':v.get('authorized_plan_count'),'validator_returncode':p.returncode,
            'staging_unchanged':True,'native_execution_started':False},rc

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--binding',required=True);ap.add_argument('--binding-sha256',required=True)
    ap.add_argument('--inbox',required=True);ap.add_argument('--json',action='store_true')
    a=ap.parse_args()
    try: out,rc=preflight(a.binding,a.binding_sha256,a.inbox)
    except ProfileError as e:
        out={'kind':'V02_AUTHORITY_PREFLIGHT_V2','status':'FAIL','reason':str(e),
             'ready_for_intake':False,'staging_unchanged':True,'native_execution_started':False};rc=12
    print(json.dumps(out,sort_keys=True,separators=(',',':')) if a.json else
          f"V02_AUTHORITY_PREFLIGHT_V2_{out['status']} reason={out.get('reason') or 'NONE'} ready_for_intake={str(out['ready_for_intake']).lower()} staging_unchanged={str(out['staging_unchanged']).lower()}")
    return rc
if __name__=='__main__': raise SystemExit(main())
