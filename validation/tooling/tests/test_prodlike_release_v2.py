import hashlib,importlib.util,json,stat,tempfile,unittest,zipfile
from pathlib import Path
import sys
TOOL=Path(__file__).resolve().parents[1];sys.path.insert(0,str(TOOL))
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
 def test_release_and_rebuild_set(self):
  out=self.r/'release';r=rel.build(self.binding,self.bsha,self.pkg,self.wh,out);self.assertEqual(r['status'],'PASS');self.assertEqual(r['inventory_status'],'NOT_RUN');self.assertFalse(r['native_execution_started'])
  m=json.loads((out/'runtime-manifest.json').read_text());self.assertEqual(m['candidate_binding_sha256'],self.bsha);self.assertFalse(m['host_ready'])
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
if __name__=='__main__':unittest.main()
