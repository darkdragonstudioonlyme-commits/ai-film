#!/usr/bin/env python3
"""Verify canonical dev22 prodlike control source and, optionally, its live user-scope deployment."""
import argparse,hashlib,json,os,re,subprocess,sys
from pathlib import Path
BUNDLE_MANIFEST='CONTROL_BUNDLE_MANIFEST.json'
FORBIDDEN=(b'dev21',b'0.1.0.dev21',b'934659f535d81d9a4a07389531acc2b9c304fa6d',b'BLOCKED_EXTERNAL_AUTHORITY',b'/run-evidence/validation/v02-authority/latest.json')
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for c in iter(lambda:f.read(1024*1024),b''):h.update(c)
 return h.hexdigest()
def fail(reason,**extra): print(json.dumps({'kind':'AIFILM_P00_DEV22_CONTROL_BUNDLE_VERIFY','status':'FAIL','reason':reason,**extra},sort_keys=True,separators=(',',':')));raise SystemExit(1)
def run(args):
 env=os.environ.copy();env.setdefault('XDG_RUNTIME_DIR',f'/run/user/{os.getuid()}');p=subprocess.run(args,text=True,capture_output=True,env=env);return p.returncode,p.stdout.strip(),p.stderr.strip()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--bundle',required=True);ap.add_argument('--deployed-bin');ap.add_argument('--deployed-unit-dir');ap.add_argument('--deployed-config');ap.add_argument('--release-root');ap.add_argument('--check-live',action='store_true');a=ap.parse_args()
 root=Path(a.bundle);mp=root/BUNDLE_MANIFEST
 try:m=json.loads(mp.read_text())
 except Exception:fail('MANIFEST_UNREADABLE')
 if m.get('schema_version')!=1 or m.get('kind')!='AIFILM_P00_DEV22_CONTROL_BUNDLE':fail('MANIFEST_SCHEMA')
 files=m.get('files');
 if not isinstance(files,dict):fail('MANIFEST_SCHEMA')
 actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and p.name!=BUNDLE_MANIFEST}
 if actual!=set(files):fail('SOURCE_MEMBER_SET',missing=sorted(set(files)-actual),extra=sorted(actual-set(files)))
 for rel,rec in files.items():
  p=root/rel;raw=p.read_bytes()
  if len(raw)!=rec.get('size') or sha(p)!=rec.get('sha256'):fail('SOURCE_BYTE_DRIFT',path=rel)
  if rel.startswith('scripts/') and not (p.stat().st_mode & 0o111): fail('SOURCE_EXECUTABLE_BIT_MISSING',path=rel)
  if rel.startswith(('scripts/','systemd/')):
   for token in FORBIDDEN:
    if token in raw:fail('FORBIDDEN_STALE_IDENTITY',path=rel,token=token.decode(errors='replace'))
 c=json.loads((root/'release-control.json').read_text())
 for k,v in {'release_name':'dev22','implementation_version':'0.1.0.dev22','source_commit':'86bb64938a136e3f8d6cfd0266685a01cb832b77','package_sha256':'c2ea52087039f4c7b98c53a7cc0eaf1a4a0f931645f86491bf2eb8ef12956aae','authority_evidence_root':'/home/dragon/ai-film-dev/run-evidence/validation/v02-authority-dev22','authority_model':'LOCAL_OPERATOR_SAME_WSL_TRUST_DOMAIN','verify_service':'aifilm-p00-current-verify.service','verify_timer':'aifilm-p00-current-verify.timer'}.items():
  if c.get(k)!=v:fail('CONTROL_IDENTITY',field=k)
 timers=sorted(p.name for p in (root/'systemd').glob('*.timer'))
 if len(timers)!=11 or c.get('expected_timer_count')!=11:fail('TIMER_COUNT')
 if 'aifilm-p00-current-verify.timer' not in timers:fail('CURRENT_VERIFY_TIMER_MISSING')
 if (root/'systemd/aifilm-p00-dev21-verify.timer').exists() or (root/'systemd/aifilm-p00-dev21-verify.service').exists():fail('OLD_VERIFY_UNIT_PRESENT')
 deployed=False
 if any([a.deployed_bin,a.deployed_unit_dir,a.deployed_config,a.release_root]):
  if not all([a.deployed_bin,a.deployed_unit_dir,a.deployed_config,a.release_root]):fail('DEPLOYED_ARGS_INCOMPLETE')
  db=Path(a.deployed_bin);du=Path(a.deployed_unit_dir);dc=Path(a.deployed_config);rr=Path(a.release_root)
  if dc.read_bytes()!=(root/'release-control.json').read_bytes():fail('DEPLOYED_CONFIG_DRIFT')
  if oct(dc.stat().st_mode & 0o777)[2:]!='600':fail('DEPLOYED_CONFIG_MODE',mode=oct(dc.stat().st_mode & 0o777))
  dm=dc.parent/'control-bundle-manifest.json'
  if not dm.is_file() or dm.read_bytes()!=mp.read_bytes():fail('DEPLOYED_BUNDLE_MANIFEST_DRIFT')
  for rel,rec in files.items():
   if rel=='release-control.json':continue
   if rel.startswith('scripts/'):dp=db/rel.removeprefix('scripts/')
   elif rel.startswith('systemd/'):dp=du/rel.removeprefix('systemd/')
   else:continue
   if not dp.is_file() or sha(dp)!=rec['sha256']:fail('DEPLOYED_BYTE_DRIFT',path=rel)
   if oct(dp.stat().st_mode & 0o777)[2:]!=rec['deploy_mode']:fail('DEPLOYED_MODE_DRIFT',path=rel,mode=oct(dp.stat().st_mode & 0o777))
  rm=json.loads((rr/'runtime-manifest.json').read_text())
  for k in ('release_name','implementation_version','source_commit','source_digest','test_digest','contract_digest','package_sha256','wheel_sha256'):
   if rm.get(k)!=c.get(k):fail('DEPLOYED_RELEASE_IDENTITY',field=k)
  if (du/'aifilm-p00-dev21-verify.service').exists() or (du/'aifilm-p00-dev21-verify.timer').exists():fail('OLD_VERIFY_DEPLOYMENT_PRESENT')
  deployed=True
  if a.check_live:
   current=Path('/home/dragon/ai-film-runtime/current')
   if not current.exists() or current.resolve()!=rr.resolve():fail('CURRENT_RELEASE_DRIFT',actual=str(current.resolve()) if current.exists() else 'MISSING',expected=str(rr.resolve()))
   expected_user=Path.home()/'.config/systemd/user'
   if du.resolve()!=expected_user.resolve():fail('WRONG_SYSTEMD_SCOPE',unit_dir=str(du))
   for name in timers:
    erc,en,_=run(['systemctl','--user','is-enabled',name]);arc,ac,_=run(['systemctl','--user','is-active',name])
    if erc or arc or en!='enabled' or ac!='active':fail('LIVE_TIMER_STATE',timer=name,enabled=en,active=ac)
   rc,res,_=run(['systemctl','--user','show','-p','Result','--value',c['verify_service']])
   if rc or res!='success':fail('LIVE_VERIFY_RESULT',result=res)
 out={'kind':'AIFILM_P00_DEV22_CONTROL_BUNDLE_VERIFY','status':'PASS','release_name':c['release_name'],'source_commit':c['source_commit'],'file_count':len(files),'script_count':m.get('script_count'),'systemd_file_count':m.get('systemd_file_count'),'timer_count':len(timers),'deployed_checked':deployed,'live_timer_state_checked':bool(a.check_live),'native_execution_started':False}
 print(json.dumps(out,sort_keys=True,separators=(',',':')));return 0
if __name__=='__main__':main()
