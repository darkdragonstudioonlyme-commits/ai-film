#!/usr/bin/env python3
import hashlib, json, os, subprocess
from datetime import datetime, timezone
from pathlib import Path
from control_common import load_control

BASE=Path('/home/dragon/ai-film-runtime')
CONTROL=load_control()
HIST=BASE/'run-evidence/prodlike-program/history'
STATE=HIST/'chain-state.json'
SOURCES={
 'health': BASE/'health/latest.json',
 'dr_rehearsal': BASE/'run-evidence/prodlike-program/recovery-rehearsal/latest.json',
 'failclosed': BASE/'run-evidence/prodlike-program/failclosed-campaign/latest.json',
 'authority': Path(CONTROL['authority_evidence_root'])/'latest.json',
}
RETENTION=30

def sha(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for c in iter(lambda:f.read(1024*1024),b''): h.update(c)
 return h.hexdigest()
def safe_load(path):
 try: return json.loads(path.read_text(encoding='utf-8'))
 except Exception: return {}

def timers():
 env=os.environ.copy(); env.setdefault('XDG_RUNTIME_DIR',f'/run/user/{os.getuid()}')
 p=subprocess.run(['systemctl','--user','list-timers','aifilm-p00-*','--all','--no-legend'],text=True,capture_output=True,env=env)
 names=[]
 if p.returncode==0:
  for line in p.stdout.splitlines():
   parts=line.split()
   for token in parts:
    if token.startswith('aifilm-p00-') and token.endswith('.timer'):
     names.append(token); break
 return sorted(set(names))

def latest_record():
 records=sorted(p for p in HIST.glob('*.json') if p.name!='chain-state.json')
 return records[-1] if records else None

def write_json_atomic(path,obj):
 tmp=path.with_name('.'+path.name+'.tmp')
 tmp.write_text(json.dumps(obj,sort_keys=True,indent=2)+'\n',encoding='utf-8')
 os.chmod(tmp,0o600); tmp.replace(path)
def main():
 HIST.mkdir(parents=True,exist_ok=True,mode=0o700)
 prev=latest_record(); prev_sha=sha(prev) if prev else safe_load(STATE).get('last_record_sha256')
 src={k:{'sha256':sha(p),'size':p.stat().st_size} for k,p in SOURCES.items() if p.is_file()}
 health=safe_load(SOURCES['health']); dr=safe_load(SOURCES['dr_rehearsal'])
 fault=safe_load(SOURCES['failclosed']); auth=safe_load(SOURCES['authority'])
 now=datetime.now(timezone.utc); stamp=now.strftime('%Y%m%dT%H%M%SZ')
 rec={
  'schema_version':1,'kind':'AIFILM_P00_OPERATIONAL_EVIDENCE_LEDGER','timestamp_utc':now.isoformat(),
  'previous_record_sha256':prev_sha,'sources':src,'timer_names':timers(),
  'summary':{
   'health_status':health.get('status'),'authority_status':auth.get('status'),'authority_reason':auth.get('reason'),
   'native_execution_started':auth.get('native_execution_started',False),'dr_rehearsal_status':dr.get('status'),
   'dr_control_files':dr.get('control_files'),'dr_timer_definitions':dr.get('timer_definitions'),
   'failclosed_status':fault.get('status'),'failclosed_passed':fault.get('passed'),'failclosed_total':fault.get('total')},
  'protected_authority_objects_included':False,'credentials_included':False}
 path=HIST/f'{stamp}.json'; write_json_atomic(path,rec)
 digest=sha(path); (path.with_suffix('.json.sha256')).write_text(digest+'  '+path.name+'\n',encoding='utf-8')
 os.chmod(path.with_suffix('.json.sha256'),0o600)
 records=sorted(p for p in HIST.glob('*.json') if p.name!='chain-state.json')
 pruned=[]
 while len(records)>RETENTION:
  old=records.pop(0); old_sha=sha(old); side=old.with_suffix('.json.sha256')
  pruned.append({'name':old.name,'sha256':old_sha}); old.unlink(missing_ok=True); side.unlink(missing_ok=True)
 state={'schema_version':1,'kind':'AIFILM_P00_EVIDENCE_CHAIN_STATE','last_record':path.name,
        'last_record_sha256':digest,'retention':RETENTION,
        'anchor_before_oldest_sha256':pruned[-1]['sha256'] if pruned else safe_load(STATE).get('anchor_before_oldest_sha256')}
 write_json_atomic(STATE,state)
 print(f'AIFILM_EVIDENCE_LEDGER_PASS record={path.name} sha256={digest} retained={len(records)} timers={len(rec["timer_names"])}')
 return 0

if __name__=='__main__':
 raise SystemExit(main())
