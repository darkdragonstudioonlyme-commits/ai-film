#!/usr/bin/env python3
import argparse,hashlib,json,shutil,sys
from pathlib import Path

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for c in iter(lambda:f.read(1024*1024),b''):h.update(c)
 return h.hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--control',required=True);ap.add_argument('--release-root',required=True);ap.add_argument('--package',required=True);ap.add_argument('--wheel',required=True);ap.add_argument('--output',required=True);a=ap.parse_args()
 c=json.load(open(a.control));r=Path(a.release_root);pkg=Path(a.package);wh=Path(a.wheel);out=Path(a.output)
 if out.exists(): raise RuntimeError('output-exists')
 m=json.loads((r/'runtime-manifest.json').read_text())
 for k in ('release_name','implementation_version','source_commit','source_digest','test_digest','contract_digest','package_sha256','wheel_sha256'):
  if m.get(k)!=c.get(k): raise RuntimeError('runtime-identity:'+k)
 if sha(pkg)!=c['package_sha256'] or sha(wh)!=c['wheel_sha256']:raise RuntimeError('artifact-identity')
 out.mkdir(parents=True)
 src={'package':pkg,'wheel':wh,'app-manifest':r/'app-manifest.sha256','runtime-manifest':r/'runtime-manifest.json'}
 names={'package':c['package_name'],'wheel':c['wheel_name'],'app-manifest':'app-manifest.sha256','runtime-manifest':'runtime-manifest.json'}
 files={}
 for k,p in src.items():
  n=names[k];shutil.copy2(p,out/n);files[n]={'sha256':sha(out/n),'size':(out/n).stat().st_size}
 idx={'schema_version':1,'kind':'AIFILM_P00_REBUILD_SET','release_name':c['release_name'],'source_commit':c['source_commit'],'source_digest':c['source_digest'],'test_digest':c['test_digest'],'contract_digest':c['contract_digest'],'native_authority_included':False,'protected_identity_included':False,'files':files}
 (out/'rebuild-index.json').write_text(json.dumps(idx,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'kind':'AIFILM_P00_REBUILD_SET_BUILD','status':'PASS','release_name':c['release_name'],'file_count':len(files),'package_sha256':files[c['package_name']]['sha256'],'native_execution_started':False},sort_keys=True,separators=(',',':')));return 0
if __name__=='__main__':
 try:raise SystemExit(main())
 except Exception as e:print('AIFILM_P00_REBUILD_SET_BUILD_FAIL '+str(e),file=sys.stderr);raise SystemExit(1)
