import hashlib,importlib.util,json,os,shutil,stat,subprocess,tempfile,unittest,zipfile
from pathlib import Path
import sys
TOOL=Path(__file__).resolve().parents[1];ROOT=TOOL.parents[1];sys.path.insert(0,str(TOOL))
from v02_candidate_profile import canonical
def load(name,file):
 s=importlib.util.spec_from_file_location(name,TOOL/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
rel=load('rel','build_prodlike_release-v2.py');reb=load('reb','build_prodlike_rebuild_set-v2.py')

class ReleaseTests(unittest.TestCase):
 def setUp(self):
  self.td=tempfile.TemporaryDirectory();self.r=Path(self.td.name);self.pkg=self.r/'candidate.zip';self.wh=self.r/'candidate.whl'
  files={
   'src/aifilm_p00/__init__.py':b"__version__='0.1.0.dev99'\n",
   'src/aifilm_p00/__main__.py':b"import json,sys\nif '--version' in sys.argv: print('0.1.0.dev99')\nelif 'preflight' in sys.argv: print(json.dumps({'host_ready':False}))\n",
   'tools/run_native_acceptance_tests.py':b"import json\nprint(json.dumps({'case_count':86,'actual_status':'NOT_RUN','parent_cases_executed':0,'qualification_issued':False}))\n",
   'README.md':b'x\n'}
  manifest={'source_commit':'a'*40,'implementation_version':'0.1.0.dev99','source_content_digest':'1'*64,'test_content_digest':'2'*64,'contract_digest':'3'*64,'files':[]}
  for p,b in files.items():manifest['files'].append({'path':p,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
  with zipfile.ZipFile(self.pkg,'w') as z:
   z.writestr('MANIFEST.json',json.dumps(manifest))
   for p,b in files.items():z.writestr(p,b)
  with zipfile.ZipFile(self.wh,'w') as z:
   z.writestr('aifilm_p00/__init__.py',files['src/aifilm_p00/__init__.py']);z.writestr('aifilm_p00/__main__.py',files['src/aifilm_p00/__main__.py'])
  self.profile={'authority_model':'LOCAL_OPERATOR_SAME_WSL_TRUST_DOMAIN','build_digest':'1'*64,'candidate_id':'11111111-2222-4333-8444-555555555555','code_review_record':'reviews/x.md','contract_digest':'3'*64,'implementation_version':'0.1.0.dev99','package_sha256':rel.sha_file(self.pkg),'schema_version':1,'source_commit':'a'*40,'status':'CANDIDATE_BOUND','test_review_record':'test-governance/x.md','test_set_digest':'2'*64,'wheel_sha256':rel.sha_file(self.wh)}
  self.binding=self.r/'binding.json';self.binding.write_bytes(canonical(self.profile)+b'\n');self.bsha=hashlib.sha256(self.binding.read_bytes()).hexdigest()
 def tearDown(self):self.td.cleanup()
 def build_release(self,name='release'):
  out=self.r/name;r=rel.build(self.binding,self.bsha,self.pkg,self.wh,out);self.assertEqual(r['status'],'PASS');return out,r
 def run_verify(self,out,extra_env=None):
  env=os.environ.copy();env.update(extra_env or {})
  return subprocess.run([str(out/'bin/verify-runtime')],cwd=out,text=True,capture_output=True,env=env)
 def write_json_ro(self,path,value):
  os.chmod(path,0o644);path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n');os.chmod(path,0o444)
 def clone(self,base,name):
  dst=self.r/name;shutil.copytree(base,dst,symlinks=True);return dst

 def test_release_and_rebuild_set(self):
  out,r=self.build_release();self.assertEqual(r['inventory_status'],'NOT_RUN');self.assertFalse(r['native_execution_started'])
  m=json.loads((out/'runtime-manifest.json').read_text());self.assertEqual(m['candidate_binding_sha256'],self.bsha);self.assertFalse(m['host_ready'])
  self.assertEqual(m['runtime_verify'],'PASS');self.assertEqual(m['verify_runtime_sha256'],r['verify_runtime_sha256'])
  self.assertFalse((out/'app/src/aifilm_p00/__init__.py').stat().st_mode & 0o222)
  ro=self.r/'rebuild';rr=reb.build(self.binding,self.bsha,out,self.pkg,self.wh,ro);self.assertEqual(rr['status'],'PASS')
  idx=json.loads((ro/'rebuild-index.json').read_text());self.assertFalse(idx['private_key_included']);self.assertFalse(idx['host_venv_included'])
 def test_wrong_binding_or_artifact_fails(self):
  bad=self.r/'bad.zip';bad.write_bytes(self.pkg.read_bytes()+b'x')
  with self.assertRaises(Exception):rel.build(self.binding,self.bsha,bad,self.wh,self.r/'badout')
  with self.assertRaises(Exception):rel.build(self.binding,'0'*64,self.pkg,self.wh,self.r/'badout2')
 def test_package_manifest_candidate_drift_fails(self):
  bad=self.r/'badpkg.zip'
  with zipfile.ZipFile(self.pkg) as src,zipfile.ZipFile(bad,'w') as dst:
   for n in src.namelist():
    raw=src.read(n)
    if n=='MANIFEST.json':
     x=json.loads(raw);x['source_commit']='b'*40;raw=json.dumps(x).encode()
    dst.writestr(n,raw)
  p=dict(self.profile);p['package_sha256']=rel.sha_file(bad);b=self.r/'b2.json';b.write_bytes(canonical(p)+b'\n');h=hashlib.sha256(b.read_bytes()).hexdigest()
  with self.assertRaisesRegex(Exception,'PACKAGE_MANIFEST:source_commit'):rel.build(b,h,bad,self.wh,self.r/'badrel')

 def test_verify_runtime_generated_bound_and_runs_clean_env(self):
  out,r=self.build_release('verify-ok');v=out/'bin/verify-runtime';m=json.loads((out/'runtime-manifest.json').read_text())
  self.assertTrue(v.is_file());self.assertFalse(v.is_symlink());self.assertEqual(stat.S_IMODE(v.stat().st_mode),0o750);self.assertTrue(os.access(v,os.X_OK))
  self.assertEqual(rel.sha_file(v),m['verify_runtime_sha256']);self.assertEqual(r['verify_runtime_sha256'],m['verify_runtime_sha256']);self.assertEqual(r['verify_runtime_status'],'PASS')
  p=self.run_verify(out,{'VIRTUAL_ENV':'/tmp/evil-venv','PYTHONPATH':'/tmp/evil-pythonpath','PYTHONHOME':'/tmp/evil-pythonhome','SECRET_SHOULD_NOT_LEAK':'x'})
  self.assertEqual(p.returncode,0,p.stderr);self.assertIn('PRODLIKE_RUNTIME_VERIFY_PASS',p.stdout);self.assertFalse((out/'venv').exists());self.assertFalse((out/'.venv').exists())

 def test_verify_runtime_rejects_manifest_app_wheel_inventory_and_version_drift(self):
  base,_=self.build_release('matrix-base')
  cases=[]
  def manifest_mut(name,fn,reason):
   x=self.clone(base,name);mp=x/'runtime-manifest.json';m=json.loads(mp.read_text());fn(m);self.write_json_ro(mp,m);cases.append((name,x,reason))
  manifest_mut('bad-kind',lambda m:m.__setitem__('kind','WRONG'),'RUNTIME_MANIFEST_SCHEMA')
  manifest_mut('bad-version',lambda m:m.__setitem__('implementation_version','9.9.9'),'VERSION')
  manifest_mut('bad-host-ready',lambda m:m.__setitem__('host_ready',True),'RUNTIME_BOUNDARY')
  x=self.clone(base,'bad-app-manifest');am=x/'app-manifest.sha256';os.chmod(am,0o644);am.write_text(am.read_text()+'0'*64+'  extra\n');os.chmod(am,0o444);cases.append(('bad-app-manifest',x,'APP_MANIFEST_HASH'))
  x=self.clone(base,'bad-member');app=x/'app';os.chmod(app,0o755);extra=app/'unexpected.txt';extra.write_text('x');os.chmod(extra,0o444);os.chmod(app,0o555);cases.append(('bad-member',x,'APP_MEMBER_SET'))
  x=self.clone(base,'bad-app-bytes');p=x/'app/README.md';os.chmod(p,0o644);p.write_text('drift\n');os.chmod(p,0o444);cases.append(('bad-app-bytes',x,'APP_FILE_HASH'))
  x=self.clone(base,'bad-app-file-mode');p=x/'app/README.md';os.chmod(p,0o644);cases.append(('bad-app-file-mode',x,'APP_FILE_MODE'))
  x=self.clone(base,'bad-app-dir-mode');p=x/'app/src';os.chmod(p,0o755);cases.append(('bad-app-dir-mode',x,'APP_DIR_MODE'))
  x=self.clone(base,'bad-wheel');m=json.loads((x/'runtime-manifest.json').read_text());p=x/'dist'/m['wheel_name'];os.chmod(p,0o644);p.write_bytes(p.read_bytes()+b'x');os.chmod(p,0o444);cases.append(('bad-wheel',x,'WHEEL_HASH'))
  for field,value in [('case_count',85),('actual_status','PASS'),('parent_cases_executed',1),('qualification_issued',True)]:
   x=self.clone(base,'bad-inventory-'+field);ip=x/'evidence/native-inventory.json';inv=json.loads(ip.read_text());inv[field]=value;ip.write_text(json.dumps(inv,indent=2,sort_keys=True)+'\n')
   mp=x/'runtime-manifest.json';m=json.loads(mp.read_text());m['inventory_sha256']=rel.sha_file(ip);self.write_json_ro(mp,m);cases.append(('bad-inventory-'+field,x,'INVENTORY_SEMANTICS'))
  for name,x,reason in cases:
   with self.subTest(name=name):
    p=self.run_verify(x);self.assertNotEqual(p.returncode,0);self.assertIn(reason,p.stderr)

 def test_verify_runtime_rejects_self_hash_drift(self):
  out,_=self.build_release('self-drift');v=out/'bin/verify-runtime'
  with v.open('ab') as f:f.write(b'\n# self drift\n')
  p=self.run_verify(out);self.assertNotEqual(p.returncode,0);self.assertIn('VERIFY_RUNTIME_SELF_HASH',p.stderr)

 def test_verify_runtime_is_candidate_generic_and_secret_free(self):
  src=rel.render_verify_runtime().decode()
  forbidden=['dev21','dev22','0.1.0.dev99',self.profile['candidate_id'],self.profile['build_digest'],self.profile['test_set_digest'],self.profile['package_sha256'],'/home/dragon/ai-film-runtime','VIRTUAL_ENV','.venv']
  for token in forbidden:self.assertNotIn(token,src)
  self.assertIn('/usr/bin/python3',src);self.assertIn("root/'app/src'",src)

 def test_verify_runtime_composes_with_reviewed_control_consumers(self):
  x=json.loads((TOOL/'prodlike_control_templates_v2.json').read_text());rows={r['path']:r['content'] for r in x['files']}
  self.assertIn('$TARGET/bin/verify-runtime',rows['scripts/activate-release'])
  self.assertIn('/home/dragon/ai-film-runtime/current/bin/verify-runtime',rows['scripts/verify-current'])
  self.assertIn('ExecStart=/home/dragon/ai-film-runtime/current/bin/verify-runtime',rows['systemd/aifilm-p00-current-verify.service'])

 def test_verify_runtime_path_type_mode_and_exec_failclosed(self):
  base,_=self.build_release('artifact-base');m=json.loads((base/'runtime-manifest.json').read_text());expected=m['verify_runtime_sha256']
  x=self.clone(base,'artifact-missing');(x/'bin/verify-runtime').unlink()
  with self.assertRaisesRegex(Exception,'VERIFY_RUNTIME_PATH_TYPE'):rel.validate_verify_runtime_artifact(x/'bin/verify-runtime',expected)
  x=self.clone(base,'artifact-symlink');v=x/'bin/verify-runtime';v.unlink();v.symlink_to('/usr/bin/python3')
  with self.assertRaisesRegex(Exception,'VERIFY_RUNTIME_PATH_TYPE'):rel.validate_verify_runtime_artifact(v,expected)
  x=self.clone(base,'artifact-directory');v=x/'bin/verify-runtime';v.unlink();v.mkdir()
  with self.assertRaisesRegex(Exception,'VERIFY_RUNTIME_PATH_TYPE'):rel.validate_verify_runtime_artifact(v,expected)
  for name,mode in [('artifact-wrong-mode',0o740),('artifact-nonexec',0o640)]:
   x=self.clone(base,name);v=x/'bin/verify-runtime';os.chmod(v,mode)
   with self.assertRaisesRegex(Exception,'VERIFY_RUNTIME_MODE'):rel.validate_verify_runtime_artifact(v,expected)

 def test_verify_runtime_deterministic_and_rebuild_dependency_unchanged(self):
  a,ra=self.build_release('det-a');b,rb=self.build_release('det-b')
  self.assertEqual((a/'bin/verify-runtime').read_bytes(),(b/'bin/verify-runtime').read_bytes());self.assertEqual(ra['verify_runtime_sha256'],rb['verify_runtime_sha256'])
  dep='validation/tooling/build_prodlike_rebuild_set-v2.py';base='35605267fea7cac1fa332a3fd7c90da5dd0726f8'
  self.assertEqual(subprocess.run(['git','-C',str(ROOT),'diff','--quiet',base,'--',dep]).returncode,0)

 def test_verify_runtime_source_has_no_deployment_native_or_signing_capability(self):
  src=(TOOL/'build_prodlike_release-v2.py').read_text()
  for token in ['systemctl --user','wsl.exe','winreg','SetValueEx','--execute','PRIVATE KEY','/home/dragon/ai-film-runtime/current']:
   self.assertNotIn(token,src)

if __name__=='__main__':unittest.main()
