import hashlib,importlib.util,json,subprocess,tempfile,unittest
from pathlib import Path
import sys
TOOL=Path(__file__).resolve().parents[1];sys.path.insert(0,str(TOOL))
from v02_candidate_profile import canonical
def load(name,file):
 s=importlib.util.spec_from_file_location(name,TOOL/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
pre=load('pre','v02-authority-preflight-v2.py');mat=load('mat','materialize-v02-native-policy-v2.py');seal=load('seal','verify-lab-artifact-seal-v2.py');payload=load('payload','build_lab_payload-v2.py')
PROFILE={'authority_model':'LOCAL_OPERATOR_SAME_WSL_TRUST_DOMAIN','build_digest':'1'*64,'candidate_id':'acf18da3-4969-451c-8a4b-a7e46ad89c98','code_review_record':'reviews/code.md','contract_digest':'2'*64,'implementation_version':'0.1.0.dev23','package_sha256':'3'*64,'schema_version':1,'source_commit':'a'*40,'status':'CANDIDATE_BOUND','test_review_record':'test-governance/review.md','test_set_digest':'4'*64,'wheel_sha256':'5'*64}
class GenericTests(unittest.TestCase):
 def setUp(self):
  self.td=tempfile.TemporaryDirectory();self.root=Path(self.td.name);self.binding=self.root/'binding.json';self.binding.write_bytes(canonical(PROFILE)+b'\n');self.bsha=hashlib.sha256(self.binding.read_bytes()).hexdigest()
 def tearDown(self):self.td.cleanup()
 def test_preflight_detects_mutation(self):
  inbox=self.root/'inbox';inbox.mkdir();fake=self.root/'fake.py';fake.write_text("from pathlib import Path\nimport sys\np=Path(sys.argv[-1]);(p/'x').write_text('x')\nprint('{}')\n")
  out,rc=pre.preflight(self.binding,self.bsha,inbox,fake);self.assertEqual(rc,3);self.assertEqual(out['reason'],'PREFLIGHT_MUTATED_STAGING')
 def test_materializer_builds_generation_one_without_hklm(self):
  inbox=self.root/'inbox';obj=inbox/'objects';obj.mkdir(parents=True)
  def add(v):
   raw=canonical(v);ref=hashlib.sha256(raw).hexdigest();(obj/(ref+'.json')).write_bytes(raw);return ref
  reg={'role':'registration','execution_class':'LAB','host_id':'lab-host','operator_sids':['S-1']};regref=add(reg)
  suite={'role':'lab_acceptance_suite','build_digest':'1'*64,'test_set_digest':'4'*64,'contract_digest':'2'*64};sref=add(suite)
  env={'role_pins':{'registration':[regref],'lab_acceptance_suite':[sref]},'lab_registration_ref':regref};(inbox/'approval-envelope.json').write_text(json.dumps(env))
  old=mat.validate_intake;mat.validate_intake=lambda *a:{'lab_acceptance_suite_ref':sref}
  try:r=mat.materialize(self.binding,self.bsha,inbox,self.root/'policy.json')
  finally:mat.validate_intake=old
  self.assertEqual(r['generation'],1);self.assertFalse(r['hklm_written']);self.assertEqual(json.loads((self.root/'policy.json').read_text())['generation'],1)
 def test_seal_binds_profile_and_readonly_artifacts(self):
  root=self.root/'seal';root.mkdir();a=root/'a.bin';a.write_bytes(b'abc');a.chmod(0o444)
  v={'candidate_id':PROFILE['candidate_id'],'source_commit':PROFILE['source_commit'],'candidate_binding_sha256':self.bsha,'pristine_restore_probe':'PASS','artifacts':[{'name':'a.bin','bytes':3,'sha256':hashlib.sha256(b'abc').hexdigest()}]}
  s=root/'LAB_ARTIFACT_SEAL_V1.json';s.write_text(json.dumps(v));s.chmod(0o444)
  self.assertEqual(seal.verify(self.binding,self.bsha,root)['status'],'PASS')
 def test_generic_lab_payload_binds_candidate_and_excludes_host_venv(self):
  rel=self.root/'release';app=rel/'app';app.mkdir(parents=True);(app/'x.py').write_text('x=1\n')
  d=hashlib.sha256((app/'x.py').read_bytes()).hexdigest();(rel/'app-manifest.sha256').write_text(d+'  x.py\n')
  (rel/'runtime-manifest.json').write_text(json.dumps({'implementation_version':PROFILE['implementation_version'],'source_commit':PROFILE['source_commit'],'contract_digest':PROFILE['contract_digest'],'package_sha256':PROFILE['package_sha256'],'wheel_sha256':PROFILE['wheel_sha256'],'native_execution_started':False,'native_lab_authority':False}))
  out=self.root/'payload';r=payload.build(self.binding,self.bsha,rel,out);self.assertEqual(r['status'],'PASS');self.assertFalse(r['native_execution_started']);self.assertFalse(any('venv' in x.name.lower() for x in out.iterdir()))
 def test_watcher_and_stage_remove_stale_ready(self):
  inbox=self.root/'empty';inbox.mkdir();out=self.root/'out';out.mkdir();(out/'READY').write_text('stale')
  p=subprocess.run([str(TOOL/'watch-v02-authority-v2.sh'),'--binding',str(self.binding),'--binding-sha256',self.bsha,'--inbox',str(inbox),'--out-root',str(out)],capture_output=True,text=True)
  self.assertNotEqual(p.returncode,0);self.assertFalse((out/'READY').exists())
  (out/'READY').write_text('stale');state=self.root/'state';state.write_text('RUNNING');sealroot=self.root/'sealroot';sealroot.mkdir()
  p=subprocess.run([str(TOOL/'pre-v03-authority-stage-v2.sh'),'--binding',str(self.binding),'--binding-sha256',self.bsha,'--inbox',str(inbox),'--out-root',str(out),'--lab-state-file',str(state),'--seal-root',str(sealroot)],capture_output=True,text=True)
  self.assertEqual(p.returncode,20);self.assertFalse((out/'READY').exists())
if __name__=='__main__':unittest.main()
