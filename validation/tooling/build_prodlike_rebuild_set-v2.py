#!/usr/bin/env python3
"""Build immutable candidate-bound prodlike recovery set. No protected/native identity is included."""
from __future__ import annotations
import argparse,hashlib,json,os,shutil
from pathlib import Path
from v02_candidate_profile import ProfileError,load_profile

class RebuildError(RuntimeError):pass
def req(c,r):
    if not c:raise RebuildError(r)
def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for c in iter(lambda:f.read(1024*1024),b''):h.update(c)
    return h.hexdigest()

def build(binding,binding_sha256,release_root,package,wheel,output):
    profile,profile_sha=load_profile(binding,binding_sha256);r=Path(release_root);pkg=Path(package);wh=Path(wheel);out=Path(output)
    req(not out.exists(),'OUTPUT_EXISTS');m=json.loads((r/'runtime-manifest.json').read_text())
    expected={'candidate_id':profile['candidate_id'],'candidate_binding_sha256':profile_sha,'implementation_version':profile['implementation_version'],
              'source_commit':profile['source_commit'],'source_digest':profile['build_digest'],'test_digest':profile['test_set_digest'],
              'contract_digest':profile['contract_digest'],'package_sha256':profile['package_sha256'],'wheel_sha256':profile['wheel_sha256']}
    for k,v in expected.items():req(m.get(k)==v,'RUNTIME_IDENTITY:'+k)
    req(sha(pkg)==profile['package_sha256'] and sha(wh)==profile['wheel_sha256'],'ARTIFACT_IDENTITY')
    out.mkdir(parents=True);src={'package':pkg,'wheel':wh,'app-manifest':r/'app-manifest.sha256','runtime-manifest':r/'runtime-manifest.json'}
    names={'package':pkg.name,'wheel':wh.name,'app-manifest':'app-manifest.sha256','runtime-manifest':'runtime-manifest.json'};files={}
    for k,p in src.items():
        n=names[k];shutil.copy2(p,out/n);files[n]={'sha256':sha(out/n),'bytes':(out/n).stat().st_size};os.chmod(out/n,0o444)
    idx={'schema_version':1,'kind':'AIFILM_P00_REBUILD_SET_V2','candidate_id':profile['candidate_id'],'candidate_binding_sha256':profile_sha,
         'implementation_version':profile['implementation_version'],'source_commit':profile['source_commit'],'source_digest':profile['build_digest'],
         'test_digest':profile['test_set_digest'],'contract_digest':profile['contract_digest'],'package_sha256':profile['package_sha256'],
         'wheel_sha256':profile['wheel_sha256'],'native_authority_included':False,'protected_identity_included':False,
         'private_key_included':False,'host_venv_included':False,'files':files}
    ip=out/'rebuild-index.json';ip.write_text(json.dumps(idx,indent=2,sort_keys=True)+'\n');os.chmod(ip,0o444)
    return {'kind':'AIFILM_P00_REBUILD_SET_BUILD_V2','status':'PASS','candidate_id':profile['candidate_id'],
            'candidate_binding_sha256':profile_sha,'file_count':len(files),'rebuild_index_sha256':sha(ip),
            'native_execution_started':False,'deployment_started':False}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--binding',required=True);ap.add_argument('--binding-sha256',required=True)
    ap.add_argument('--release-root',required=True);ap.add_argument('--package',required=True);ap.add_argument('--wheel',required=True);ap.add_argument('--output',required=True);a=ap.parse_args()
    try:o=build(a.binding,a.binding_sha256,a.release_root,a.package,a.wheel,a.output);rc=0
    except (ProfileError,RebuildError,OSError,ValueError,json.JSONDecodeError) as e:o={'kind':'AIFILM_P00_REBUILD_SET_BUILD_V2','status':'FAIL','reason':str(e),'native_execution_started':False,'deployment_started':False};rc=1
    print(json.dumps(o,sort_keys=True,separators=(',',':')));return rc
if __name__=='__main__':raise SystemExit(main())
