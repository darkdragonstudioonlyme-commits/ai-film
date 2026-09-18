#!/usr/bin/env python3
import hashlib, io, json, os, subprocess, tarfile, tempfile, zipfile
from datetime import datetime, timezone
from pathlib import Path
from control_common import load_control

BASE=Path('/home/dragon/ai-film-runtime')
CONTROL=load_control()
EXPORT_ROOT=Path(CONTROL['offhost_export_root'])
EXPORT=EXPORT_ROOT/CONTROL['offhost_export_name']
VERIFY=BASE/'bin/verify-offhost-export.py'
EVID=BASE/'run-evidence/prodlike-program/recovery-rehearsal'
SNAP=BASE/'state-snapshots'

def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def sha_file(p): return sha_bytes(Path(p).read_bytes())
def run(args,cwd=None,env=None):
 p=subprocess.run(args,cwd=cwd,text=True,capture_output=True,env=env)
 if p.returncode: raise RuntimeError((p.stderr or p.stdout).strip())
 return p.stdout.strip()
def safe(name):
 p=Path(name); return bool(name) and not p.is_absolute() and '..' not in p.parts and '\\' not in name


def verify_restored_ledger(root):
 statep=root/'chain-state.json'
 if not statep.is_file(): raise RuntimeError('ledger-state-missing')
 state=json.loads(statep.read_text())
 records=sorted(p for p in root.glob('*.json') if p.name!='chain-state.json')
 if not records or len(records)>30: raise RuntimeError('ledger-record-count')
 prev=None
 for i,p in enumerate(records):
  side=p.with_suffix('.json.sha256')
  if not side.is_file(): raise RuntimeError('ledger-sidecar')
  actual=sha_file(p); parts=side.read_text().split()
  if len(parts)<2 or parts[0]!=actual or parts[1]!=p.name: raise RuntimeError('ledger-sidecar-hash')
  obj=json.loads(p.read_text())
  expected=prev if i else state.get('anchor_before_oldest_sha256')
  if obj.get('previous_record_sha256')!=expected: raise RuntimeError('ledger-chain')
  if obj.get('protected_authority_objects_included') is not False or obj.get('credentials_included') is not False: raise RuntimeError('ledger-protected-domain')
  prev=actual
 last=records[-1]
 if state.get('last_record')!=last.name or state.get('last_record_sha256')!=sha_file(last): raise RuntimeError('ledger-state-drift')
 return len(records)

def main():
 start=datetime.now(timezone.utc); run([str(VERIFY),'--json'])
 SNAP.mkdir(exist_ok=True,mode=0o700); EVID.mkdir(parents=True,exist_ok=True,mode=0o700)
 with tempfile.TemporaryDirectory(prefix='full-dr-rehearsal.',dir=SNAP) as td:
  td=Path(td); bundle=td/'bundle'; control=td/'restored-control'; app=td/'app'; bundle.mkdir(); control.mkdir()
  with zipfile.ZipFile(EXPORT) as z:
   if any(not safe(n) for n in z.namelist()): raise RuntimeError('unsafe-export-path')
   z.extractall(bundle)
  meta=json.loads((bundle/'OFFHOST-DR-MANIFEST.json').read_text())
  if meta.get('status')!='TRANSFER_READY' or meta.get('off_host_copy_completed') is not False: raise RuntimeError('export-state')
  ctrl=next(bundle/n for n in meta['files'] if n.startswith('control/') and n.endswith('.tar.gz'))
  with tarfile.open(ctrl,'r:gz') as t:
   names=t.getnames()
   if any(not safe(n) for n in names): raise RuntimeError('unsafe-control-path')
   bmeta=json.load(t.extractfile('backup-manifest.json')); records=bmeta['files']
   if set(names)!={'backup-manifest.json',*records}: raise RuntimeError('control-member-set')
   for n,rec in records.items():
    raw=t.extractfile(n).read()
    if len(raw)!=rec['size'] or sha_bytes(raw)!=rec['sha256']: raise RuntimeError('control-hash:'+n)
   t.extractall(control)
  required=['bin/runtime-health.py','bin/backup-control-state.py','bin/verify-control-backup.py','bin/build-offhost-export.py','bin/verify-offhost-export.py','bin/run-failclosed-campaign.py','bin/run-dr-recovery-rehearsal.py','bin/archive-operational-evidence.py','bin/verify-operational-evidence.py','evidence/failclosed-campaign/latest.json','evidence/recovery-rehearsal/latest.json','evidence/operational-ledger/chain-state.json','systemd/aifilm-p00-dr-rehearsal.service','systemd/aifilm-p00-dr-rehearsal.timer','systemd/aifilm-p00-failclosed-campaign.service','systemd/aifilm-p00-failclosed-campaign.timer','systemd/aifilm-p00-evidence-ledger.service','systemd/aifilm-p00-evidence-ledger.timer']
  if any(not (control/p).is_file() for p in required): raise RuntimeError('control-required-file')
  timers=list((control/'systemd').glob('*.timer'))
  if len(timers)!=11: raise RuntimeError('timer-count')
  resources=list((control/'systemd/dropins').glob('*/resources.conf'))
  if len(resources)!=11: raise RuntimeError('resource-dropin-count')
  ledger_records=verify_restored_ledger(control/'evidence/operational-ledger')
  pyfiles=list((control/'bin').glob('*.py'))
  for p in pyfiles: run(['/usr/bin/python3','-m','py_compile',str(p)])
  pkg=bundle/'rebuild'/CONTROL['package_name']
  with zipfile.ZipFile(pkg) as z:
   pm=json.loads(z.read('MANIFEST.json'))
   for row in pm['files']: z.extract(row['path'],app)
  count=0
  for line in (bundle/'rebuild/app-manifest.sha256').read_text().splitlines():
   if not line.strip(): continue
   dg,name=line.split(None,1); p=app/name.strip().lstrip('*')
   if not p.is_file() or sha_file(p)!=dg: raise RuntimeError('app-hash:'+name)
   count+=1
  if count!=CONTROL['app_file_count']: raise RuntimeError('app-count')
  venv=td/'venv'; run(['/usr/bin/python3','-m','venv','--without-pip',str(venv)])
  py=venv/'bin/python'; purelib=Path(run([str(py),'-c','import sysconfig;print(sysconfig.get_paths()["purelib"])']))
  (purelib/'aifilm_current_app.pth').write_text(str(app/'src')+'\n')
  home=td/'home'; tmp=td/'tmp'; home.mkdir(); tmp.mkdir()
  env={'HOME':str(home),'USER':'dragon','LOGNAME':'dragon','LANG':'C.UTF-8','LC_ALL':'C.UTF-8','PATH':f'{venv}/bin:/usr/bin:/bin','PYTHONNOUSERSITE':'1','PYTHONDONTWRITEBYTECODE':'1','TMPDIR':str(tmp)}
  version=run([str(py),'-m','aifilm_p00','--version'],app,env)
  pre=json.loads(run([str(py),'-m','aifilm_p00','preflight','--workspace-only'],app,env))
  inv=json.loads(run([str(py),'tools/run_native_acceptance_tests.py','--list'],app,env))
  if version!=CONTROL['implementation_version'] or pre.get('host_ready') is not False: raise RuntimeError('runtime-shape')
  if inv.get('case_count')!=86 or inv.get('actual_status')!='NOT_RUN' or inv.get('parent_cases_executed')!=0: raise RuntimeError('inventory')
  end=datetime.now(timezone.utc); result={'kind':'AIFILM_P00_FULL_DR_REHEARSAL','status':'PASS','timestamp_utc':end.isoformat(),'duration_seconds':round((end-start).total_seconds(),3),'export_sha256':sha_file(EXPORT),'control_files':len(records),'timer_definitions':len(timers),'resource_dropins':len(resources),'ledger_records':ledger_records,'python_control_scripts_compiled':len(pyfiles),'app_files':count,'version':version,'inventory':'86 NOT_RUN','host_ready':False,'native_execution_started':False,'off_host_copy_completed':False}
  out=EVID/'latest.json'; tmpout=EVID/'.latest.json.tmp'; tmpout.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n'); os.chmod(tmpout,0o600); tmpout.replace(out)
  dg=sha_file(out); side=EVID/'latest.sha256'; side.write_text(dg+'  latest.json\n'); os.chmod(side,0o600)
  print('AIFILM_FULL_DR_REHEARSAL_PASS control_files=%d timers=%d app_files=%d version=%s inventory=86_NOT_RUN duration=%.3fs sha256=%s'%(len(records),len(timers),count,version,result['duration_seconds'],dg)); return 0
if __name__=='__main__':
 try: raise SystemExit(main())
 except Exception as e: print('AIFILM_FULL_DR_REHEARSAL_FAIL '+str(e)); raise SystemExit(1)
