#!/usr/bin/env python3
import hashlib,json,os,subprocess,sys,tempfile,zipfile
from pathlib import Path
TOOL=Path(__file__).resolve().parents[1]/'build_prodlike_dev22_release.py'
REBUILD=Path(__file__).resolve().parents[1]/'build_prodlike_dev22_rebuild_set.py'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 with tempfile.TemporaryDirectory() as td:
  r=Path(td);files={
   'src/aifilm_p00/__init__.py':b"__version__='9.9.0'\n",
   'src/aifilm_p00/__main__.py':b"import json,sys\nif '--version' in sys.argv: print('9.9.0')\nelif 'preflight' in sys.argv: print(json.dumps({'source_kind':'DOCUMENT','host_ready':False}))\nelse: print('{}')\n",
   'tools/run_native_acceptance_tests.py':b"import json\nprint(json.dumps({'case_count':86,'actual_status':'NOT_RUN','parent_cases_executed':0,'qualification_issued':False}))\n"}
  rows=[{'path':n,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()} for n,b in sorted(files.items())]
  pm={'source_commit':'1'*40,'implementation_version':'9.9.0','source_content_digest':'2'*64,'test_content_digest':'3'*64,'contract_digest':'4'*64,'files':rows}
  pkg=r/'fake.zip'
  with zipfile.ZipFile(pkg,'w') as z:
   for n,b in files.items():z.writestr(n,b)
   z.writestr('MANIFEST.json',json.dumps(pm))
  wheel=r/'fake.whl'
  with zipfile.ZipFile(wheel,'w') as z:
   z.writestr('aifilm_p00/__init__.py',files['src/aifilm_p00/__init__.py']);z.writestr('aifilm_p00/__main__.py',files['src/aifilm_p00/__main__.py'])
  c={'schema_version':1,'kind':'AIFILM_P00_RELEASE_CONTROL','release_name':'dev99','implementation_version':'9.9.0','source_commit':'1'*40,'source_digest':'2'*64,'test_digest':'3'*64,'contract_digest':'4'*64,'package_name':pkg.name,'package_sha256':sha(pkg),'wheel_name':wheel.name,'wheel_sha256':sha(wheel),'app_file_count':3,'runtime_root':'/x/dev99','rebuild_root':'/x/rebuild','host_backup_root':'/x/backups','offhost_export_root':'/x/export','offhost_export_name':'x.zip','authority_evidence_root':'/x/auth','authority_model':'LOCAL_OPERATOR_SAME_WSL_TRUST_DOMAIN','verify_service':'a.service','verify_timer':'a.timer','expected_timer_count':11,'native_authority':False,'native_execution_started':False}
  cp=r/'control.json';cp.write_text(json.dumps(c));out=r/'release'
  p=subprocess.run([sys.executable,str(TOOL),'--control',str(cp),'--package',str(pkg),'--wheel',str(wheel),'--output',str(out)],text=True,capture_output=True);assert p.returncode==0,(p.stdout,p.stderr);o=json.loads(p.stdout.strip());assert o['status']=='PASS' and o['app_files']==3 and o['wheel_modules']==2;print('PASS synthetic_release_build')
  v=subprocess.run([str(out/'bin/verify-runtime')],text=True,capture_output=True);assert v.returncode==0 and '3 86 NOT_RUN release=dev99' in v.stdout,(v.stdout,v.stderr);print('PASS generated_verify_runtime')
  rb=r/'rebuild';p=subprocess.run([sys.executable,str(REBUILD),'--control',str(cp),'--release-root',str(out),'--package',str(pkg),'--wheel',str(wheel),'--output',str(rb)],text=True,capture_output=True);assert p.returncode==0,(p.stdout,p.stderr);idx=json.loads((rb/'rebuild-index.json').read_text());assert idx['kind']=='AIFILM_P00_REBUILD_SET' and idx['release_name']=='dev99' and len(idx['files'])==4;print('PASS rebuild_set_build')
  bad=r/'bad.zip';bad.write_bytes(pkg.read_bytes()+b'x');p=subprocess.run([sys.executable,str(TOOL),'--control',str(cp),'--package',str(bad),'--wheel',str(wheel),'--output',str(r/'badrelease')],text=True,capture_output=True);assert p.returncode!=0 and 'package-identity' in p.stderr;print('PASS package_identity_failclosed')
 print('PRODLIKE_DEV22_RELEASE_BUILDER_TEST_PASS 4 cases')
if __name__=='__main__':main()
