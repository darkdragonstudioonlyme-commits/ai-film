#!/usr/bin/env python3
import argparse, hashlib, json, os, subprocess, tempfile, zipfile
from pathlib import Path
from control_common import load_control

CONTROL=load_control()
ROOT=Path(CONTROL['rebuild_root'])
SNAP=Path('/home/dragon/ai-film-runtime/state-snapshots')
EXPECTED={k:CONTROL[k] for k in ('source_commit','source_digest','test_digest','contract_digest')}


def sha(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for c in iter(lambda:f.read(1024*1024),b''): h.update(c)
 return h.hexdigest()

def run(args,cwd,env=None):
 p=subprocess.run(args,cwd=cwd,text=True,capture_output=True,env=env)
 if p.returncode: raise RuntimeError(p.stderr or p.stdout)
 return p.stdout.strip()

def verify_index():
 idxp=ROOT/'rebuild-index.json'
 idx=json.loads(idxp.read_text(encoding='utf-8'))
 assert idx.get('schema_version')==1 and idx.get('kind')=='AIFILM_P00_REBUILD_SET' and idx.get('release_name')==CONTROL['release_name']
 for k,v in EXPECTED.items(): assert idx.get(k)==v, k
 assert idx.get('native_authority_included') is False
 assert idx.get('protected_identity_included') is False
 files=idx.get('files'); assert isinstance(files,dict) and len(files)==4
 for name,rec in files.items():
  p=ROOT/name
  assert p.is_file() and p.stat().st_size==rec['size'] and sha(p)==rec['sha256'], name
 z=ROOT/CONTROL['package_name']
 with zipfile.ZipFile(z) as f:
  names=f.namelist(); assert len(names)==CONTROL['app_file_count']+1 and 'MANIFEST.json' in names
  for n in names:
   q=Path(n); assert not q.is_absolute() and '..' not in q.parts
 return idx

def cold_probe():
 SNAP.mkdir(parents=True,exist_ok=True,mode=0o700)
 with tempfile.TemporaryDirectory(prefix='rebuild-probe.',dir=SNAP) as td:
  td=Path(td); app=td/'app'
  with zipfile.ZipFile(ROOT/CONTROL['package_name']) as z:
   pm=json.loads(z.read('MANIFEST.json')); files=[r['path'] for r in pm['files']]
   for name in files: z.extract(name,app)
  manifest={}
  for line in (ROOT/'app-manifest.sha256').read_text(encoding='utf-8').splitlines():
   if not line.strip(): continue
   digest,name=line.split(None,1); name=name.strip().lstrip('*')
   p=app/name
   assert p.is_file() and sha(p)==digest, name
   manifest[name]=digest
  assert len(manifest)==CONTROL['app_file_count']
  assert pm.get('source_commit')==EXPECTED['source_commit']
  assert pm.get('implementation_version')==CONTROL['implementation_version']
  assert pm.get('source_content_digest')==EXPECTED['source_digest']
  assert pm.get('test_content_digest')==EXPECTED['test_digest']
  tmp=td/'tmp'; tmp.mkdir()
  venv=td/'venv'
  run(['/usr/bin/python3','-m','venv','--without-pip',str(venv)],td)
  vpy=venv/'bin/python'
  purelib=Path(run([str(vpy),'-c','import sysconfig; print(sysconfig.get_paths()[\"purelib\"])'],td))
  (purelib/'aifilm_current_app.pth').write_text(str(app/'src')+'\n',encoding='utf-8')
  env={'HOME':'/home/dragon','USER':'dragon','LOGNAME':'dragon','LANG':'C.UTF-8','LC_ALL':'C.UTF-8',
       'PATH':f'{venv}/bin:/usr/bin:/bin','PYTHONNOUSERSITE':'1',
       'PYTHONDONTWRITEBYTECODE':'1','PYTHONUNBUFFERED':'1','TMPDIR':str(tmp)}
  version=run([str(vpy),'-m','aifilm_p00','--version'],app,env)
  pre=json.loads(run([str(vpy),'-m','aifilm_p00','preflight','--workspace-only'],app,env))
  inv=json.loads(run([str(vpy),'tools/run_native_acceptance_tests.py','--list'],app,env))
  assert version==CONTROL['implementation_version']
  assert pre['source_kind']=='DOCUMENT' and pre['host_ready'] is False
  assert inv['case_count']==86 and inv['actual_status']=='NOT_RUN'
  assert inv['parent_cases_executed']==0 and inv['qualification_issued'] is False
  return {'version':version,'case_count':86,'status':'NOT_RUN','host_ready':False}

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--cold-probe',action='store_true'); ap.add_argument('--json',action='store_true')
 args=ap.parse_args()
 try:
  idx=verify_index(); probe=cold_probe() if args.cold_probe else None
  out={'kind':'AIFILM_P00_REBUILD_VERIFY','release_name':CONTROL['release_name'],'status':'PASS','source_commit':EXPECTED['source_commit'],
       'file_count':len(idx['files']),'package_sha256':idx['files'][CONTROL['package_name']]['sha256'],
       'cold_probe':probe,'native_authority_included':False,'protected_identity_included':False}
  if args.json: print(json.dumps(out,sort_keys=True,separators=(',',':')))
  else: print(f"AIFILM_REBUILD_SET_VERIFY_PASS files={out['file_count']} cold_probe={bool(probe)} package={out['package_sha256']}")
  return 0
 except Exception as e:
  print('AIFILM_REBUILD_SET_VERIFY_FAIL '+str(e))
  return 1

if __name__=='__main__':
 raise SystemExit(main())
