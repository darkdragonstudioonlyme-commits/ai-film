import hashlib,importlib.util,json,re,subprocess,tempfile,unittest
from pathlib import Path
import sys,os
TOOL=Path(__file__).resolve().parents[1];ROOT=TOOL.parents[1];sys.path.insert(0,str(TOOL))
from v02_candidate_profile import canonical
def load(name,file):
 s=importlib.util.spec_from_file_location(name,TOOL/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
planm=load('plan','plan_lab_candidate_rebuild-v2.py');ver=load('ver','verify_lab_candidate_rebuild_receipt-v2.py')
class LabTests(unittest.TestCase):
 def setUp(self):
  self.td=tempfile.TemporaryDirectory();self.r=Path(self.td.name)
  self.p={'authority_model':'LOCAL_OPERATOR_SAME_WSL_TRUST_DOMAIN','build_digest':'1'*64,'candidate_id':'11111111-2222-4333-8444-555555555555','code_review_record':'reviews/x.md','contract_digest':'3'*64,'implementation_version':'0.1.0.dev99','package_sha256':'4'*64,'schema_version':1,'source_commit':'a'*40,'status':'CANDIDATE_BOUND','test_review_record':'test-governance/x.md','test_set_digest':'2'*64,'wheel_sha256':'5'*64}
  self.b=self.r/'b.json';self.b.write_bytes(canonical(self.p)+b'\n');self.bs=hashlib.sha256(self.b.read_bytes()).hexdigest()
  self.payload=self.r/'payload.json';self.payload.write_text(json.dumps({'schema_version':1,'kind':'P00_LAB_CANDIDATE_APP_PAYLOAD','candidate_id':self.p['candidate_id'],'candidate_binding_sha256':self.bs,'implementation_version':self.p['implementation_version'],'source_commit':self.p['source_commit'],'contract_digest':self.p['contract_digest'],'package_sha256':self.p['package_sha256'],'wheel_sha256':self.p['wheel_sha256'],'app_tar_sha256':'6'*64,'app_manifest_sha256':'7'*64,'native_execution_started':False}))
  self.prev=self.r/'prev.json';self.prev.write_text(json.dumps({'status':'PASS','lab_state':'STOPPED','restore_probe':'PASS','candidate_id':'old','candidate_binding_sha256':'8'*64,'source_commit':'b'*40,'pre_migration_export_sha256':'9'*64,'pristine_raw_sha256':'a'*64,'pristine_sealed_sha256':'b'*64,'artifact_seal_sha256':'c'*64}))
  self.obs=self.r/'state.json';self.obs.write_text(json.dumps({'schema_version':1,'distro':'AI-FILM-P00-LAB','observed_state':'STOPPED','observation_source':'HOST_WSL_LIST','observed_at':'2026-09-23T01:00:00Z'}))
 def tearDown(self):self.td.cleanup()
 def make_plan(self):
  p=self.r/'plan.json';planm.plan(self.b,self.bs,self.payload,self.prev,self.obs,p);return p
 def receipt(self):
  return {'schema_version':1,'kind':'P00_LAB_CANDIDATE_REBUILD_DEPLOYMENT_V2','status':'PASS','candidate_id':self.p['candidate_id'],'candidate_binding_sha256':self.bs,'source_commit':self.p['source_commit'],'implementation_version':self.p['implementation_version'],'package_sha256':self.p['package_sha256'],'wheel_sha256':self.p['wheel_sha256'],'app_tar_sha256':'6'*64,'app_manifest_sha256':'7'*64,'runtime_manifest_sha256':'d'*64,'inventory_sha256':'e'*64,'inventory_case_count':86,'inventory_status':'NOT_RUN','parent_cases_executed':0,'qualification_issued':False,'host_ready':False,'lab_state':'STOPPED','pre_rebuild_export_sha256':'f'*64,'pristine_raw_sha256':'1'*64,'pristine_sealed_sha256':'2'*64,'restore_probe':'PASS','restore_probe_unregistered':True,'restore_probe_receipt_sha256':'3'*64,'technical_facts_sha256':'4'*64,'artifact_seal_sha256':None,'authority_envelope_created':False,'native_execution_started':False,'v03_started':False,'rollback_source_commit':'b'*40}
 def seal(self):
  root=self.r/'seal';root.mkdir(exist_ok=True);s=root/'LAB_ARTIFACT_SEAL_V1.json';s.write_text(json.dumps({'candidate_id':self.p['candidate_id'],'candidate_binding_sha256':self.bs,'source_commit':self.p['source_commit'],'pristine_restore_probe':'PASS','artifacts':[]}));return root,s
 def test_plan_is_nonexecuting_and_candidate_bound(self):
  p=self.make_plan();x=json.loads(p.read_text());self.assertFalse(x['execution_authorized']);self.assertFalse(x['lab_mutation_started']);self.assertEqual(x['target']['candidate_binding_sha256'],self.bs);self.assertEqual(x['rollback']['source_commit'],'b'*40)
 def test_plan_requires_stopped_distinct_rollback(self):
  self.obs.write_text(json.dumps({'schema_version':1,'distro':'AI-FILM-P00-LAB','observed_state':'RUNNING','observation_source':'HOST_WSL_LIST','observed_at':'x'}))
  with self.assertRaisesRegex(Exception,'LAB_STOP_OBSERVATION'):self.make_plan()
  self.obs.write_text(json.dumps({'schema_version':1,'distro':'AI-FILM-P00-LAB','observed_state':'STOPPED','observation_source':'HOST_WSL_LIST','observed_at':'x'}));x=json.loads(self.prev.read_text());x['candidate_id']=self.p['candidate_id'];x['source_commit']=self.p['source_commit'];self.prev.write_text(json.dumps(x))
  with self.assertRaisesRegex(Exception,'ROLLBACK_NOT_DISTINCT'):self.make_plan()
 def test_receipt_verify_and_failure_modes(self):
  plan=self.make_plan();root,s=self.seal();r=self.receipt();r['artifact_seal_sha256']=hashlib.sha256(s.read_bytes()).hexdigest();rp=self.r/'receipt.json';rp.write_text(json.dumps(r));o=ver.verify(self.b,self.bs,plan,rp,root);self.assertEqual(o['status'],'PASS');self.assertEqual(o['inventory_status'],'NOT_RUN')
  for key,bad,reason in [('inventory_status','PASS','INVENTORY_STATE'),('restore_probe','FAIL','RESTORE_PROBE'),('lab_state','RUNNING','LAB_FINAL_STATE'),('authority_envelope_created',True,'NATIVE_BOUNDARY')]:
   x=dict(r);x[key]=bad;rp.write_text(json.dumps(x))
   with self.assertRaisesRegex(Exception,reason):ver.verify(self.b,self.bs,plan,rp,root)
 def test_stale_dev22_receipt_cannot_be_relabelled(self):
  plan=self.make_plan();root,s=self.seal();r=self.receipt();r['artifact_seal_sha256']=hashlib.sha256(s.read_bytes()).hexdigest();r['candidate_id']='old';rp=self.r/'receipt.json';rp.write_text(json.dumps(r))
  with self.assertRaisesRegex(Exception,'RECEIPT_IDENTITY:candidate_id'):ver.verify(self.b,self.bs,plan,rp,root)
 def test_rollback_loss_rejected(self):
  x=json.loads(self.prev.read_text());x['pristine_sealed_sha256']=None;self.prev.write_text(json.dumps(x))
  with self.assertRaises(Exception):self.make_plan()
 def test_writable_seal_artifact_rejected_by_reused_verifier(self):
  import importlib.util
  s=importlib.util.spec_from_file_location('sealv',TOOL/'verify-lab-artifact-seal-v2.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
  root=self.r/'sealx';root.mkdir();a=root/'a.bin';a.write_bytes(b'abc');a.chmod(0o644);seal=root/'LAB_ARTIFACT_SEAL_V1.json';seal.write_text(json.dumps({'candidate_id':self.p['candidate_id'],'source_commit':self.p['source_commit'],'candidate_binding_sha256':self.bs,'pristine_restore_probe':'PASS','artifacts':[{'name':'a.bin','bytes':3,'sha256':hashlib.sha256(b'abc').hexdigest()}]}));seal.chmod(0o444)
  with self.assertRaisesRegex(Exception,'ARTIFACT_WRITABLE'):m.verify(self.b,self.bs,root)
 def test_reuse_and_historical_byte_hardcuts(self):
  change=(ROOT/'test-governance/TEST_CHANGE-P00-DEV23-PRODLIKE-LAB-RECONCILIATION-010.md').read_text();m=re.search(r'^BASE_VALIDATION_COMMIT: ([0-9a-f]{40})$',change,re.M);self.assertIsNotNone(m);base=m.group(1)
  files=['validation/tooling/v02_candidate_profile.py','validation/tooling/build_lab_payload-v2.py','validation/tooling/verify-lab-artifact-seal-v2.py','validation/tooling/dev23-candidate-binding.json',
  'validation/tooling/build_prodlike_dev22_release.py','validation/tooling/build_prodlike_dev22_rebuild_set.py','validation/tooling/verify_prodlike_dev22_control_bundle.py','validation/tooling/verify_prodlike_user_systemd.py','validation/tooling/build_lab_dev22_payload.py','validation/tooling/verify-lab-artifact-seal.py',
  'validation/tooling/tests/test_prodlike_dev22_release_builder.py','validation/tooling/tests/test_prodlike_dev22_control_bundle.py','validation/tooling/tests/test_prodlike_user_systemd_verifier.py','validation/tooling/tests/test_lab_dev22_payload_builder.py',
  'validation/PRODLIKE_DEV22_MIGRATION_DEPLOYMENT-P00.md','validation/PRODLIKE_DEV22_MIGRATION_DEPLOYMENT_RECEIPT-P00.json','validation/V02_LAB_DEV22_REBUILD_DEPLOYMENT-P00.md','validation/V02_LAB_DEV22_REBUILD_DEPLOYMENT_RECEIPT-P00.json']
  for f in files:self.assertEqual(subprocess.run(['git','-C',str(ROOT),'diff','--quiet',base,'--',f]).returncode,0,f)
if __name__=='__main__':unittest.main()
