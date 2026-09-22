#!/usr/bin/env python3
"""Build deterministic candidate-bound LAB application payload from reviewed release bytes."""
from __future__ import annotations
import argparse,hashlib,json,os,tarfile
from pathlib import Path
from v02_candidate_profile import ProfileError,load_profile

class PayloadError(RuntimeError):pass
def require(c,r):
    if not c:raise PayloadError(r)
def sha_file(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(4*1024*1024),b''):h.update(chunk)
    return h.hexdigest()
def safe_rel(name):
    p=Path(name);return bool(name) and not p.is_absolute() and '..' not in p.parts and '\\' not in name
def parse_manifest(path):
    rows={}
    for line in Path(path).read_text().splitlines():
        if not line.strip():continue
        digest,name=line.split('  ',1);require(safe_rel(name) and name not in rows,'APP_MANIFEST_PATH')
        require(len(digest)==64 and all(c in '0123456789abcdef' for c in digest),'APP_MANIFEST_DIGEST');rows[name]=digest
    require(rows,'APP_MANIFEST_EMPTY');return rows
def build_tar(app,rows,out):
    with tarfile.open(out,'w',format=tarfile.PAX_FORMAT) as tf:
        for name in sorted(rows):
            p=app/name;require(p.is_file() and not p.is_symlink(),'APP_FILE_MISSING:'+name);require(sha_file(p)==rows[name],'APP_FILE_DRIFT:'+name)
            info=tf.gettarinfo(str(p),arcname=name);info.uid=0;info.gid=0;info.uname='';info.gname='';info.mtime=0
            with p.open('rb') as fh:tf.addfile(info,fh)
def verify_tar(path,rows):
    with tarfile.open(path,'r') as tf:
        members=[m for m in tf.getmembers() if m.isfile()];require([m.name for m in members]==sorted(rows),'TAR_MEMBER_SET')
        for m in members:
            f=tf.extractfile(m);require(f is not None and hashlib.sha256(f.read()).hexdigest()==rows[m.name],'TAR_MEMBER_HASH')
def build(binding,binding_sha256,release_root,output):
    profile,profile_sha=load_profile(binding,binding_sha256);root=Path(release_root);out=Path(output)
    manifest=json.loads((root/'runtime-manifest.json').read_text())
    expected={'implementation_version':profile['implementation_version'],'source_commit':profile['source_commit'],
              'contract_digest':profile['contract_digest'],'package_sha256':profile['package_sha256']}
    for k,want in expected.items():require(manifest.get(k)==want,'RUNTIME_MANIFEST:'+k)
    if 'wheel_sha256' in manifest:require(manifest['wheel_sha256']==profile['wheel_sha256'],'RUNTIME_MANIFEST:wheel_sha256')
    require(manifest.get('native_execution_started') is False and manifest.get('native_lab_authority') is False,'RUNTIME_NATIVE_CLAIM')
    app=root/'app';app_manifest=root/'app-manifest.sha256';rows=parse_manifest(app_manifest)
    out.mkdir(parents=True,exist_ok=True)
    label=profile['implementation_version'].replace('.','_')
    tar=out/f'AI-FILM-P00-{label}_APP.tar';build_tar(app,rows,tar);verify_tar(tar,rows)
    copied=out/f'AI-FILM-P00-{label}_APP.sha256';copied.write_bytes(app_manifest.read_bytes())
    meta={'schema_version':1,'kind':'P00_LAB_CANDIDATE_APP_PAYLOAD','candidate_id':profile['candidate_id'],
          'candidate_binding_sha256':profile_sha,**expected,'wheel_sha256':profile['wheel_sha256'],
          'app_manifest_sha256':sha_file(copied),'app_tar_sha256':sha_file(tar),'app_tar_bytes':tar.stat().st_size,
          'app_files':len(rows),'target_root':f"/opt/ai-film-lab/runtime/{profile['implementation_version']}",
          'native_execution_started':False}
    mp=out/'LAB_CANDIDATE_PAYLOAD_MANIFEST.json';mp.write_text(json.dumps(meta,indent=2,sort_keys=True)+'\n')
    for p in (tar,copied,mp):os.chmod(p,0o444)
    return {'kind':'P00_LAB_CANDIDATE_PAYLOAD_BUILD','status':'PASS','candidate_id':profile['candidate_id'],
            'app_files':len(rows),'app_tar_sha256':meta['app_tar_sha256'],
            'app_manifest_sha256':meta['app_manifest_sha256'],'native_execution_started':False}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--binding',required=True);ap.add_argument('--binding-sha256',required=True)
    ap.add_argument('--release-root',required=True);ap.add_argument('--output',required=True);a=ap.parse_args()
    try:o=build(a.binding,a.binding_sha256,a.release_root,a.output);rc=0
    except (ProfileError,PayloadError,OSError,ValueError,json.JSONDecodeError,tarfile.TarError) as e:
        o={'kind':'P00_LAB_CANDIDATE_PAYLOAD_BUILD','status':'FAIL','reason':str(e),'native_execution_started':False};rc=1
    print(json.dumps(o,sort_keys=True,separators=(',',':')));return rc
if __name__=='__main__':raise SystemExit(main())
