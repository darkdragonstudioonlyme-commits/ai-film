#!/usr/bin/env python3
"""Verify candidate-bound prodlike control source/deployed bytes; never calls live systemd."""
from __future__ import annotations
import argparse,hashlib,json,os
from pathlib import Path
from v02_candidate_profile import ProfileError,load_profile

class VerifyError(RuntimeError):pass
def req(c,r):
    if not c:raise VerifyError(r)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def target(unit_dir,rel):
    parts=Path(rel).parts
    if parts[0]!='systemd':raise VerifyError('SYSTEMD_PATH')
    if len(parts)>=3 and parts[1].endswith('.service.d'):return unit_dir/parts[1]/Path(*parts[2:])
    return unit_dir/Path(*parts[1:])

def verify(binding,binding_sha256,bundle,runtime_manifest=None,deployed_bin=None,deployed_unit_dir=None,deployed_config=None,release_root=None):
    profile,profile_sha=load_profile(binding,binding_sha256);root=Path(bundle);mp=root/'CONTROL_BUNDLE_MANIFEST.json';m=json.loads(mp.read_text())
    req(m.get('schema_version')==1 and m.get('kind')=='AIFILM_P00_CONTROL_BUNDLE_V2','MANIFEST_SCHEMA')
    req(m.get('candidate_id')==profile['candidate_id'] and m.get('candidate_binding_sha256')==profile_sha,'MANIFEST_CANDIDATE')
    files=m.get('files');req(type(files) is dict and len(files)==64,'MEMBER_COUNT')
    actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and p.name!='CONTROL_BUNDLE_MANIFEST.json'}
    req(actual==set(files),'SOURCE_MEMBER_SET')
    for rel,rec in files.items():
        p=root/rel;raw=p.read_bytes();req(p.stat().st_size==rec.get('size') and sha(p)==rec.get('sha256'),'SOURCE_BYTE_DRIFT:'+rel)
        req(format(p.stat().st_mode&0o777,'o')==rec.get('deploy_mode'),'SOURCE_MODE_DRIFT:'+rel)
        if rel.startswith(('scripts/','systemd/')):
            low=raw.lower();req(b'dev21' not in low and b'dev22' not in low,'STALE_IDENTITY:'+rel)
    c=json.loads((root/'release-control.json').read_text());expected={'candidate_id':profile['candidate_id'],'candidate_binding_sha256':profile_sha,
        'implementation_version':profile['implementation_version'],'source_commit':profile['source_commit'],'source_digest':profile['build_digest'],
        'test_digest':profile['test_set_digest'],'contract_digest':profile['contract_digest'],'package_sha256':profile['package_sha256'],
        'wheel_sha256':profile['wheel_sha256'],'authority_model':profile['authority_model']}
    for k,v in expected.items():req(c.get(k)==v,'CONTROL_IDENTITY:'+k)
    req(c.get('native_authority') is False and c.get('native_execution_started') is False,'CONTROL_NATIVE_BOUNDARY')
    timers=sorted(p.name for p in (root/'systemd').glob('*.timer'));req(len(timers)==c.get('expected_timer_count')==m.get('timer_count')==11,'TIMER_COUNT')
    if runtime_manifest:
        rm=json.loads(Path(runtime_manifest).read_text())
        for k in ('candidate_id','candidate_binding_sha256','implementation_version','source_commit','source_digest','test_digest','contract_digest','package_sha256','wheel_sha256'):
            req(rm.get(k)==expected.get(k,profile_sha if k=='candidate_binding_sha256' else None),'RUNTIME_CONTROL_IDENTITY:'+k)
    args=[deployed_bin,deployed_unit_dir,deployed_config,release_root]
    deployed=any(x is not None for x in args)
    if deployed:
        req(all(x is not None for x in args),'DEPLOYED_ARGS_INCOMPLETE');db=Path(deployed_bin);du=Path(deployed_unit_dir);dc=Path(deployed_config);rr=Path(release_root)
        req(dc.read_bytes()==(root/'release-control.json').read_bytes() and format(dc.stat().st_mode&0o777,'o')=='600','DEPLOYED_CONFIG_DRIFT')
        for rel,rec in files.items():
            if rel=='release-control.json':continue
            dp=db/rel.removeprefix('scripts/') if rel.startswith('scripts/') else target(du,rel)
            req(dp.is_file() and sha(dp)==rec['sha256'],'DEPLOYED_BYTE_DRIFT:'+rel)
            req(format(dp.stat().st_mode&0o777,'o')==rec['deploy_mode'],'DEPLOYED_MODE_DRIFT:'+rel)
        rm=json.loads((rr/'runtime-manifest.json').read_text())
        for k,v in expected.items():
            if k in rm:req(rm[k]==v,'DEPLOYED_RELEASE_IDENTITY:'+k)
    return {'kind':'AIFILM_P00_CONTROL_BUNDLE_VERIFY_V2','status':'PASS','candidate_id':profile['candidate_id'],
            'candidate_binding_sha256':profile_sha,'file_count':64,'timer_count':11,'deployed_checked':deployed,
            'live_systemd_checked':False,'native_execution_started':False}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--binding',required=True);ap.add_argument('--binding-sha256',required=True);ap.add_argument('--bundle',required=True)
    ap.add_argument('--runtime-manifest');ap.add_argument('--deployed-bin');ap.add_argument('--deployed-unit-dir');ap.add_argument('--deployed-config');ap.add_argument('--release-root');a=ap.parse_args()
    try:o=verify(a.binding,a.binding_sha256,a.bundle,a.runtime_manifest,a.deployed_bin,a.deployed_unit_dir,a.deployed_config,a.release_root);rc=0
    except (ProfileError,VerifyError,OSError,ValueError,json.JSONDecodeError) as e:o={'kind':'AIFILM_P00_CONTROL_BUNDLE_VERIFY_V2','status':'FAIL','reason':str(e),'live_systemd_checked':False,'native_execution_started':False};rc=1
    print(json.dumps(o,sort_keys=True,separators=(',',':')));return rc
if __name__=='__main__':raise SystemExit(main())
