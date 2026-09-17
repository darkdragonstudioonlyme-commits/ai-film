#!/usr/bin/env python3
import argparse, json, os, subprocess
from pathlib import Path

VALIDATOR=Path(__file__).resolve().with_name('v02-authority-intake.py')
DEFAULT=Path('/mnt/c/Users/Admin/AppData/Local/AI-FILM/LAB/authority-approved/dev21')

def snapshot(root):
 out={}
 if not root.exists(): return out
 for p in sorted(root.rglob('*')):
  try:
   st=p.lstat(); out[str(p.relative_to(root))]=(p.is_dir(),st.st_size,st.st_mtime_ns)
  except OSError: out[str(p.relative_to(root))]=('unreadable',)
 return out

def main():
 ap=argparse.ArgumentParser(description='Read-only preflight using the exact V02 authority validator semantics.')
 ap.add_argument('--inbox',default=str(DEFAULT)); ap.add_argument('--json',action='store_true'); args=ap.parse_args()
 root=Path(args.inbox); before=snapshot(root)
 env={'HOME':'/home/dragon','USER':'dragon','LOGNAME':'dragon','LANG':'C.UTF-8','LC_ALL':'C.UTF-8','PATH':'/usr/bin:/bin','PYTHONNOUSERSITE':'1','PYTHONDONTWRITEBYTECODE':'1'}
 p=subprocess.run(['/usr/bin/python3',str(VALIDATOR),'--inbox',str(root)],text=True,capture_output=True,env=env)
 after=snapshot(root)
 if before!=after:
  out={'kind':'V02_AUTHORITY_PREFLIGHT','status':'FAIL','reason':'PREFLIGHT_MUTATED_STAGING','ready_for_intake':False,'native_execution_started':False}
  print(json.dumps(out,sort_keys=True,separators=(',',':'))); return 3
 try:
  raw=(p.stdout.strip().splitlines() or ['{}'])[-1]; v=json.loads(raw)
 except Exception:
  out={'kind':'V02_AUTHORITY_PREFLIGHT','status':'FAIL','reason':'VALIDATOR_OUTPUT_UNREADABLE','ready_for_intake':False,'native_execution_started':False}
  print(json.dumps(out,sort_keys=True,separators=(',',':'))); return 4
 vstatus=v.get('status'); reason=v.get('reason')
 if p.returncode==0 and vstatus=='READY_TO_ADVANCE' and v.get('ready_to_advance') is True:
  status='READY_FOR_INTAKE'; ready=True; reason=None
 elif reason=='APPROVAL_ENVELOPE_MISSING': status='MISSING'; ready=False
 else: status='INVALID'; ready=False
 out={'kind':'V02_AUTHORITY_PREFLIGHT','status':status,'reason':reason,'ready_for_intake':ready,
      'candidate_id':v.get('candidate_id'),'case_count':v.get('case_count'),
      'authorized_plan_count':v.get('authorized_plan_count'),'native_execution_started':False,
      'validator_returncode':p.returncode,'staging_unchanged':True}
 print(json.dumps(out,sort_keys=True,separators=(',',':')) if args.json else
       f"V02_AUTHORITY_PREFLIGHT_{status} reason={reason or 'NONE'} ready_for_intake={str(ready).lower()} staging_unchanged=true")
 return 0 if ready else (10 if status=='MISSING' else 11)

if __name__=='__main__': raise SystemExit(main())
