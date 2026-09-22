import hashlib,importlib.util,json,tempfile,unittest
from pathlib import Path
import sys
TOOL=Path(__file__).resolve().parents[1];sys.path.insert(0,str(TOOL))
from v03_binding_producer_common import PROOF_SPECS,digest,write_object,read_object
spec=importlib.util.spec_from_file_location('lp',TOOL/'materialize-v03-late-proof.py');lp=importlib.util.module_from_spec(spec);spec.loader.exec_module(lp)
BIND=TOOL/'dev23-candidate-binding.json'
SCOPES={
'source_manifest':{'host_id':'lab-host','target_registration':'reg','source_class':'LAB'},
'protection':{'host_id':'lab-host','source_witness':'w'},
'restore_envelope':{'host_id':'lab-host','checkpoint_digest':'1'*64,'envelope_digest':'2'*64},
'user_init_receipt':{'host_id':'lab-host','plan_digest':'3'*64,'target_registration':'reg','user':'u'},
'c3_postchecks':{'host_id':'lab-host','plan_digest':'3'*64,'host_boot':'2026-09-23T00:00:00Z'},
'operation_postcheck':{'host_id':'lab-host','plan_digest':'3'*64,'step_id':'s','target_registration':'reg','host_boot':'2026-09-23T00:00:00Z'},
'run_revocation':{'host_id':'lab-host','original_plan_digest':'4'*64,'recovery_request_digest':'5'*64,'disposition':'REVOKE'},
'read_absence_observation':{'host_id':'lab-host','original_plan_digest':'4'*64,'read_id':'r','intent_digest':'6'*64,'command_digest':'7'*64},
'restore_result':{'host_id':'lab-host','checkpoint_digest':'1'*64,'source_target_registration':'reg'}}
class LateProofTests(unittest.TestCase):
 def setUp(self):
  self.td=tempfile.TemporaryDirectory();self.r=Path(self.td.name);self.obj=self.r/'objects';self.obj.mkdir();self.out=self.r/'out';self.out.mkdir()
  self.profile=json.loads(BIND.read_text());self.bsha=hashlib.sha256(BIND.read_bytes()).hexdigest()
  self.collector=write_object(self.obj,{'role':'collector_release','withdrawn':False,'review_verdict':'PASS','build_digest':'9'*64})
  self.authorizer=write_object(self.obj,{'role':'resource_owner','withdrawn':False,'owner_sid':'S-1','receipt_roles':list(PROOF_SPECS),'host_ids':['lab-host']})
 def tearDown(self):self.td.cleanup()
 def request(self,role,scope,measurement_time='2026-09-23T00:03:00Z',not_before=None,owner_assertion=None):
  actual={'ok':True};subject=digest(scope);raw=write_object(self.obj,{'role':'measurement_artifact','withdrawn':False,'measurement_actual_digest':digest(actual),'subject_digest':subject})
  m=write_object(self.obj,{'role':'measurement','source_kind':'LAB','status':'OBSERVED','contract_digest':self.profile['contract_digest'],'actual':actual,'host_id':'lab-host','subject_digest':subject,'timestamp_utc':measurement_time,'collector_ref':self.collector,'raw_artifact_ref':raw,'collector_digest':'9'*64})
  q={'schema_version':1,'role':role,'scope':scope,'owner_sid':'S-1','authorizer_ref':self.authorizer,'measurement_refs':[m],'claim':{'ok':True},'claim_map':{'ok':{'measurement_ref':m,'actual_key':'ok'}},'issued_at':'2026-09-23T00:05:00Z','expires_at':'2026-09-23T01:00:00Z','owner_assertion':PROOF_SPECS[role]['owner_assertion'] if owner_assertion is None else owner_assertion,'not_before':not_before}
  p=self.r/(role+'.json');p.write_text(json.dumps(q));return p
 def test_all_nine_roles_materialize(self):
  for role,scope in SCOPES.items():
   nb='2026-09-23T00:01:00Z' if role in ('read_absence_observation','operation_postcheck') else None
   out=lp.materialize(BIND,self.bsha,self.obj,self.request(role,scope,not_before=nb),self.out);self.assertEqual(out['status'],'PASS');self.assertEqual(read_object(self.out,out['proof_ref'],role)['scope'],scope)
 def test_read_absence_before_intent_rejected(self):
  p=self.request('read_absence_observation',SCOPES['read_absence_observation'],measurement_time='2026-09-23T00:01:00Z',not_before='2026-09-23T00:02:00Z')
  with self.assertRaisesRegex(Exception,'READ_ABSENCE_PRECEDES_INTENT'):lp.materialize(BIND,self.bsha,self.obj,p,self.out)
 def test_owner_assertion_disallowed_role_rejected(self):
  p=self.request('restore_result',SCOPES['restore_result'],owner_assertion=True)
  with self.assertRaises(Exception):lp.materialize(BIND,self.bsha,self.obj,p,self.out)
 def test_unreviewed_collector_and_raw_mismatch_rejected(self):
  role='restore_result';scope=SCOPES[role];p=self.request(role,scope);q=json.loads(p.read_text());mref=q['measurement_refs'][0];m=read_object(self.obj,mref,'measurement')
  badc=write_object(self.obj,{'role':'collector_release','withdrawn':False,'review_verdict':'FAIL','build_digest':'9'*64});m['collector_ref']=badc;self.obj.joinpath(mref+'.json').unlink();mref2=write_object(self.obj,m);q['measurement_refs']=[mref2];q['claim_map']['ok']['measurement_ref']=mref2;p.write_text(json.dumps(q))
  with self.assertRaisesRegex(Exception,'PROOF_COLLECTOR_UNREVIEWED'):lp.materialize(BIND,self.bsha,self.obj,p,self.out)
  p=self.request(role,scope);q=json.loads(p.read_text());mref=q['measurement_refs'][0];m=read_object(self.obj,mref,'measurement');raw=read_object(self.obj,m['raw_artifact_ref'],'measurement_artifact');raw['measurement_actual_digest']='0'*64;badraw=write_object(self.obj,raw);m['raw_artifact_ref']=badraw;self.obj.joinpath(mref+'.json').unlink();mref2=write_object(self.obj,m);q['measurement_refs']=[mref2];q['claim_map']['ok']['measurement_ref']=mref2;p.write_text(json.dumps(q))
  with self.assertRaisesRegex(Exception,'PROOF_RAW_BINDING'):lp.materialize(BIND,self.bsha,self.obj,p,self.out)
 def test_unmeasured_claim_rejected(self):
  role='restore_result';p=self.request(role,SCOPES[role]);q=json.loads(p.read_text());q['claim']={'ok':False};p.write_text(json.dumps(q))
  with self.assertRaisesRegex(Exception,'PROOF_CLAIM_NOT_MEASURED'):lp.materialize(BIND,self.bsha,self.obj,p,self.out)
if __name__=='__main__':unittest.main()
