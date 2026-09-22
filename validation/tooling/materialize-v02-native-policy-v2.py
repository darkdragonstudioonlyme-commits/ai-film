#!/usr/bin/env python3
"""Materialize generation-1 NativeStore candidate bytes only; never write HKLM."""
from __future__ import annotations
import argparse,hashlib,json,os,subprocess
from pathlib import Path
from v02_candidate_profile import ProfileError,canonical,load_profile,sha

TOOL=Path(__file__).resolve().parent
VALIDATOR=TOOL/'v02-authority-intake-v2.py'

class MaterializeError(RuntimeError): pass
def require(c,r):
    if not c: raise MaterializeError(r)
def blocked(reason,**extra):
    return {'kind':'V02_NATIVE_POLICY_MATERIALIZER_V2','status':'BLOCKED','reason':reason,
            'policy_written':False,'hklm_written':False,'native_execution_started':False,**extra}

def read_object(objects,ref):
    require(isinstance(ref,str) and len(ref)==64,'PINNED_REF')
    p=objects/(ref+'.json');require(p.is_file() and not p.is_symlink(),'PINNED_OBJECT_MISSING')
    raw=p.read_bytes();require(hashlib.sha256(raw).hexdigest()==ref,'PINNED_OBJECT_HASH_MISMATCH')
    try:v=json.loads(raw.decode('utf-8'))
    except Exception as e: raise MaterializeError('PINNED_OBJECT_JSON') from e
    return raw,v

def validate_intake(binding,binding_sha256,inbox):
    env={'HOME':os.environ.get('HOME','/home/dragon'),'USER':os.environ.get('USER','dragon'),
         'LOGNAME':os.environ.get('LOGNAME','dragon'),'LANG':'C.UTF-8','LC_ALL':'C.UTF-8',
         'PATH':'/usr/bin:/bin','PYTHONNOUSERSITE':'1','PYTHONDONTWRITEBYTECODE':'1'}
    p=subprocess.run(['/usr/bin/python3',str(VALIDATOR),'--binding',str(binding),
                      '--binding-sha256',binding_sha256,'--inbox',str(inbox)],
                     text=True,capture_output=True,env=env)
    try:v=json.loads((p.stdout.strip().splitlines() or ['{}'])[-1])
    except Exception as e: raise MaterializeError('VALIDATOR_OUTPUT_INVALID') from e
    require(p.returncode==0 and v.get('ready_to_advance') is True,'AUTHORITY_INTAKE_NOT_READY')
    return v

def materialize(binding,binding_sha256,inbox,out):
    profile,profile_sha=load_profile(binding,binding_sha256); inbox=Path(inbox);out=Path(out)
    ready=validate_intake(binding,profile_sha,inbox)
    env_path=inbox/'approval-envelope.json';require(env_path.is_file() and not env_path.is_symlink(),'APPROVAL_ENVELOPE_MISSING')
    env=json.loads(env_path.read_text(encoding='utf-8')); pins=env.get('role_pins');require(type(pins) is dict and pins,'ROLE_PINS')
    objects=inbox/'objects';blobs={}
    for role,refs in pins.items():
        require(isinstance(role,str) and isinstance(refs,list),'ROLE_PINS')
        for ref in refs:
            raw,_=read_object(objects,ref);blobs[ref]=raw.decode('utf-8')
    reg_ref=env.get('lab_registration_ref');require(reg_ref in blobs,'REGISTRATION_REF')
    reg=json.loads(blobs[reg_ref]);operators=reg.get('operator_sids');host_id=reg.get('host_id')
    require(reg.get('role')=='registration' and reg.get('execution_class')=='LAB','REGISTRATION_SCOPE')
    require(isinstance(host_id,str) and host_id and isinstance(operators,list) and operators,'REGISTRATION_SCOPE')
    suite_ref=ready.get('lab_acceptance_suite_ref');require(suite_ref in blobs,'SUITE_REF')
    suite=json.loads(blobs[suite_ref])
    require(suite.get('build_digest')==profile['build_digest'] and
            suite.get('test_set_digest')==profile['test_set_digest'] and
            suite.get('contract_digest')==profile['contract_digest'],'SUITE_CANDIDATE_SCOPE')
    policy={'schema_version':1,'host_id':host_id,'operator_sids':operators,'role_pins':pins,
            'blobs':blobs,'withdrawn_refs':[],'generation':1}
    raw=canonical(policy)
    for refs in pins.values():
        for ref in refs: require(ref in blobs and hashlib.sha256(blobs[ref].encode()).hexdigest()==ref,'POLICY_BLOB_INTEGRITY')
    out.parent.mkdir(parents=True,exist_ok=True);tmp=out.with_suffix(out.suffix+'.tmp')
    tmp.write_bytes(raw);os.chmod(tmp,0o600);tmp.replace(out);os.chmod(out,0o600)
    return {'kind':'V02_NATIVE_POLICY_MATERIALIZER_V2','status':'CANDIDATE_READY',
            'candidate_id':profile['candidate_id'],'candidate_profile_sha256':profile_sha,
            'source_commit':profile['source_commit'],'policy_written':True,'hklm_written':False,
            'policy_sha256':sha(raw),'policy_path':str(out),'generation':1,
            'lab_acceptance_suite_ref':suite_ref,'native_execution_started':False}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--binding',required=True);ap.add_argument('--binding-sha256',required=True)
    ap.add_argument('--inbox',required=True);ap.add_argument('--out',required=True);a=ap.parse_args()
    try:o=materialize(a.binding,a.binding_sha256,a.inbox,a.out);rc=0
    except (ProfileError,MaterializeError,OSError,ValueError) as e:o=blocked(str(e));rc=12
    print(json.dumps(o,sort_keys=True,separators=(',',':')));return rc
if __name__=='__main__':raise SystemExit(main())
