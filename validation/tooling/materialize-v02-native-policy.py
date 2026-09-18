#!/usr/bin/env python3
import argparse, json, os, subprocess, sys
from pathlib import Path

APP=Path('/home/dragon/ai-film-dev/validation')
sys.path.insert(0,str(APP/'src'))
from aifilm_p00.codec import canonical, sha256
from aifilm_p00.native.trust import NativeStore
from v02_local_identity import load_local_identity

VALIDATOR=Path(__file__).resolve().with_name('v02-authority-intake.py')
DEFAULT_INBOX=Path('/mnt/c/Users/Admin/AppData/Local/AI-FILM/LAB/authority-approved/dev22')
DEFAULT_OUT=Path('/home/dragon/ai-film-dev/run-evidence/validation/v02-authority-dev22/native-policy.candidate.json')

def blocked(reason,**extra):
    print(json.dumps({'kind':'V02_NATIVE_POLICY_MATERIALIZER','status':'BLOCKED',
        'reason':reason,'policy_written':False,'hklm_written':False,**extra},
        sort_keys=True,separators=(',',':')))
    raise SystemExit(12)

def run_validator(inbox):
    p=subprocess.run([str(VALIDATOR),'--inbox',str(inbox)],capture_output=True,text=True)
    line=(p.stdout.strip().splitlines() or ['{}'])[-1]
    try: data=json.loads(line)
    except json.JSONDecodeError: blocked('VALIDATOR_OUTPUT_INVALID',validator_rc=p.returncode)
    if p.returncode!=0 or data.get('ready_to_advance') is not True:
        blocked('AUTHORITY_INTAKE_NOT_READY',validator_rc=p.returncode,
                validator_reason=data.get('reason'),validator_status=data.get('status'))
    return data

def read_object(objects,ref):
    path=objects/(ref+'.json')
    try: raw=path.read_bytes()
    except OSError: blocked('PINNED_OBJECT_MISSING',ref=ref)
    if sha256(raw)!=ref: blocked('PINNED_OBJECT_HASH_MISMATCH',ref=ref)
    try: raw.decode('utf-8')
    except UnicodeDecodeError: blocked('PINNED_OBJECT_NOT_UTF8',ref=ref)
    return raw

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--inbox',default=str(DEFAULT_INBOX))
    ap.add_argument('--out',default=str(DEFAULT_OUT))
    args=ap.parse_args(); inbox=Path(args.inbox); out=Path(args.out)
    ready=run_validator(inbox)
    identity=load_local_identity(blocked); host_id=identity['host_id']
    env=json.loads((inbox/'approval-envelope.json').read_text(encoding='utf-8'))
    objects=inbox/'objects'; pins=env['role_pins']
    blobs={}
    for role,refs in pins.items():
        for ref in refs:
            blobs[ref]=read_object(objects,ref).decode('utf-8')
    reg_ref=env['lab_registration_ref']
    reg=json.loads(blobs[reg_ref])
    operators=reg.get('operator_sids')
    if not isinstance(operators,list) or not operators: blocked('REGISTRATION_OPERATORS_MISSING')
    policy={'schema_version':1,'host_id':host_id,'operator_sids':operators,
            'role_pins':pins,'blobs':blobs,'withdrawn_refs':[],'generation':1}
    raw=canonical(policy)
    try:
        store=NativeStore(raw,APP/'contracts')
        _,reg2=store.one('registration'); store.one('design'); store.one('code')
        suite=store.get('lab_acceptance_suite',ready['lab_acceptance_suite_ref'])
    except Exception as e:
        blocked('NATIVE_STORE_PREVALIDATION_FAILED',error_type=type(e).__name__)
    if store.host_id!=host_id or reg2.get('execution_class')!='LAB':
        blocked('NATIVE_STORE_SCOPE_MISMATCH')
    if suite.get('approved') is not True or suite.get('withdrawn') is not False:
        blocked('NATIVE_STORE_SUITE_STATUS')
    out.parent.mkdir(parents=True,exist_ok=True)
    tmp=out.with_suffix(out.suffix+'.tmp')
    tmp.write_bytes(raw); os.chmod(tmp,0o600); tmp.replace(out); os.chmod(out,0o600)
    print(json.dumps({'kind':'V02_NATIVE_POLICY_MATERIALIZER','status':'CANDIDATE_READY',
        'policy_written':True,'hklm_written':False,'policy_sha256':sha256(raw),
        'policy_path':str(out),'generation':1,'lab_acceptance_suite_ref':ready['lab_acceptance_suite_ref']},
        sort_keys=True,separators=(',',':')))

if __name__=='__main__': main()
