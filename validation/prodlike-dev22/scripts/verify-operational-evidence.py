#!/usr/bin/env python3
import hashlib, json, time
from pathlib import Path

ROOT=Path('/home/dragon/ai-film-runtime/run-evidence/prodlike-program/history')
STATE=ROOT/'chain-state.json'
MAX_AGE=30*3600
RETENTION=30

def sha(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for c in iter(lambda:f.read(1024*1024),b''): h.update(c)
 return h.hexdigest()

def fail(reason,**extra):
 print(json.dumps({'kind':'AIFILM_P00_EVIDENCE_LEDGER_VERIFY','status':'FAIL','reason':reason,**extra},sort_keys=True,separators=(',',':')))
 raise SystemExit(1)
def main():
 if not ROOT.is_dir() or not STATE.is_file(): fail('LEDGER_MISSING')
 try: state=json.loads(STATE.read_text(encoding='utf-8'))
 except Exception: fail('STATE_INVALID')
 records=sorted(p for p in ROOT.glob('*.json') if p.name!='chain-state.json')
 if not records or len(records)>RETENTION: fail('RETENTION_OR_EMPTY',count=len(records))
 prev=None
 for i,p in enumerate(records):
  side=p.with_suffix('.json.sha256')
  if not side.is_file(): fail('SIDECAR_MISSING',record=p.name)
  actual=sha(p); parts=side.read_text(encoding='utf-8').split()
  if len(parts)<2 or parts[0]!=actual or parts[1]!=p.name: fail('SIDECAR_MISMATCH',record=p.name)
  try: obj=json.loads(p.read_text(encoding='utf-8'))
  except Exception: fail('RECORD_INVALID',record=p.name)
  if obj.get('kind')!='AIFILM_P00_OPERATIONAL_EVIDENCE_LEDGER': fail('RECORD_KIND',record=p.name)
  if obj.get('protected_authority_objects_included') is not False or obj.get('credentials_included') is not False: fail('PROTECTED_DOMAIN',record=p.name)
  expected_prev=prev if i else state.get('anchor_before_oldest_sha256')
  if obj.get('previous_record_sha256')!=expected_prev: fail('CHAIN_BREAK',record=p.name)
  prev=actual
 last=records[-1]; last_sha=sha(last)
 if state.get('last_record')!=last.name or state.get('last_record_sha256')!=last_sha or state.get('retention')!=RETENTION:
  fail('STATE_DRIFT')
 age=max(0,int(time.time()-last.stat().st_mtime))
 if age>MAX_AGE: fail('LEDGER_STALE',age_seconds=age)
 out={'kind':'AIFILM_P00_EVIDENCE_LEDGER_VERIFY','status':'PASS','records':len(records),'age_seconds':age,
      'last_record':last.name,'last_record_sha256':last_sha,'retention':RETENTION}
 print(json.dumps(out,sort_keys=True,separators=(',',':')))
 return 0

if __name__=='__main__':
 raise SystemExit(main())
