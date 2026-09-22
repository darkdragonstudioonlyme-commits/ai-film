import hashlib,importlib.util,json,tempfile,unittest
from pathlib import Path
import sys
TOOL=Path(__file__).resolve().parents[1];ROOT=TOOL.parents[1];sys.path.insert(0,str(TOOL))
from v02_candidate_profile import canonical
from v03_binding_producer_common import load_catalog
def load(name,file):
 s=importlib.util.spec_from_file_location(name,TOOL/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
comp=load('comp','v02b-authority-graph-compiler.py');ver=load('ver','verify-v03-binding-producer.py')
BIND=TOOL/'dev23-candidate-binding.json';CAT=ROOT/'docs/PHASE00_STAGE_DERIVED_AUTHORITY_DEPENDENCY_CATALOG_V1.json'
AUTO={'semantic.expected_after','semantic.expected_envelope','semantic.refs.restore_envelope','semantic.refs.native_binding','semantic.refs.checkpoint_payload'}
class ProducerTests(unittest.TestCase):
 def build_spec(self):
  c=load_catalog(CAT);p=json.loads(BIND.read_text());objects=[];requests={}
  desc={'role':'lab_campaign_descriptor','schema_version':1,'withdrawn':False,'source_kind':'LAB','host_id':'lab-host','owner_sid':'S-1','build_digest':p['build_digest'],'test_set_digest':p['test_set_digest'],'contract_digest':p['contract_digest'],'execution_id':'exec','host_roles':{'source':'lab-host'},'issued_at':'2026-09-23T00:00:00Z','expires_at':'2026-09-23T01:00:00Z'}
  objects.append({'id':'desc','value':desc})
  for r in c['stage_dependencies']:
   cid=r['case_id'];idx=r['stage_index'];requests.setdefault(cid,[])
   self.assertEqual(idx,len(requests[cid]))
   prefix=(cid.replace('-','_')+'_'+str(idx))
   mode=r['authority_mode']
   if mode=='CONCRETE_PRE_V03':
    pid='plan_'+prefix;objects.append({'id':pid,'value':{'role':'execution_plan','schema_version':1,'tag':prefix}})
    req={'route':r['route'],'interface':'apply','authority_mode':mode,'plan_ref':{'$ref':pid}}
   elif mode=='ENTRY_PROBE_AUTHORITY':
    pid='plan_'+prefix;eid='entry_'+prefix
    objects.append({'id':pid,'value':{'role':'execution_plan','schema_version':1,'tag':prefix}})
    objects.append({'id':eid,'value':{'role':'entry_probe_set','schema_version':1,'plan_ref':{'$ref':pid}}})
    req={'route':r['route'],'interface':'apply','authority_mode':mode,'entry_probe_ref':{'$ref':eid}}
   elif mode=='STAGE_DERIVED':
    pt='pt_'+prefix;objects.append({'id':pt,'value':{'role':'lab_stage_plan_template','schema_version':1,'tag':prefix}})
    nb=None
    if 'native_binding' in r['derived_object_roles']:
     nb='nb_'+prefix;objects.append({'id':nb,'value':{'role':'lab_native_binding_template','schema_version':1,'tag':prefix}})
    deps=r['producer_dependencies'];selectors={}
    if deps:
     for lf in set(r['late_fields'])-AUTO:selectors[lf]={'producer_stage_index':deps[0]['producer_stage_index'],'actual_path':['actual']}
    dest=[]
    if 'checkpoint_payload' in r['derived_object_roles']:
     dest=[{'host_id':'lab-host','volume_id':'VOL1','canonical_path':r'C:\\staging\\checkpoint.tar','purpose':'STAGING_IMPORT','max_bytes':1000000,'offline_copy_required':True}]
    sid='slot_'+prefix
    slot={'role':'lab_stage_derivation_slot','schema_version':1,'withdrawn':False,'source_kind':'LAB','host_id':'lab-host','owner_sid':'S-1','build_digest':p['build_digest'],'test_set_digest':p['test_set_digest'],'contract_digest':p['contract_digest'],'execution_id':'exec','case_id':cid,'procedure_digest':r['procedure_digest'],'stage_index':idx,'route':r['route'],'interface':'apply','authority_mode':mode,'campaign_descriptor_ref':{'$ref':'desc'},'plan_template_ref':{'$ref':pt},'native_binding_template_ref':({'$ref':nb} if nb else None),'producer_dependencies':r['producer_dependencies'],'late_fields':r['late_fields'],'derived_object_roles':r['derived_object_roles'],'maximum_approval_seconds':3600,'destination_locator_allowlist':dest,'reconciliation_plan_refs':[],'semantic_selectors':selectors}
    objects.append({'id':sid,'value':slot});req={'route':r['route'],'interface':'apply','authority_mode':mode,'derivation_slot_ref':{'$ref':sid}}
   else:
    pid='reconplan_'+prefix;sid='slot_'+prefix;objects.append({'id':pid,'value':{'role':'execution_plan','schema_version':1,'tag':prefix}})
    slot={'role':'lab_stage_derivation_slot','schema_version':1,'withdrawn':False,'source_kind':'LAB','host_id':'lab-host','owner_sid':'S-1','build_digest':p['build_digest'],'test_set_digest':p['test_set_digest'],'contract_digest':p['contract_digest'],'execution_id':'exec','case_id':cid,'procedure_digest':r['procedure_digest'],'stage_index':idx,'route':r['route'],'interface':'apply','authority_mode':mode,'campaign_descriptor_ref':{'$ref':'desc'},'plan_template_ref':None,'native_binding_template_ref':None,'producer_dependencies':r['producer_dependencies'],'late_fields':r['late_fields'],'derived_object_roles':r['derived_object_roles'],'maximum_approval_seconds':3600,'destination_locator_allowlist':[],'reconciliation_plan_refs':[{'$ref':pid}],'semantic_selectors':{}}
    objects.append({'id':sid,'value':slot});req={'route':r['route'],'interface':'apply','authority_mode':mode,'reconciliation_slot_ref':{'$ref':sid}}
   requests[cid].append(req)
  cases={cid:{'requests':rows} for cid,rows in requests.items()}
  suite={'role':'lab_acceptance_suite','schema_version':1,'withdrawn':False,'approved':True,'source_kind':'LAB','host_id':'lab-host','owner_sid':'S-1','build_digest':p['build_digest'],'test_set_digest':p['test_set_digest'],'contract_digest':p['contract_digest'],'execution_id':'exec','issued_at':'2026-09-23T00:00:00Z','expires_at':'2026-09-23T01:00:00Z','cases':cases}
  objects.append({'id':'suite','value':suite})
  return {'schema_version':1,'objects':objects,'suite_id':'suite','descriptor_id':'desc'}
 def test_full_133_compile_and_verify(self):
  with tempfile.TemporaryDirectory() as td:
   r=Path(td);spec=r/'spec.json';spec.write_text(json.dumps(self.build_spec()));obj=r/'objects';receipt=r/'receipt.json'
   bsha=hashlib.sha256(BIND.read_bytes()).hexdigest();out=comp.compile_graph(BIND,bsha,CAT,spec,obj,receipt);self.assertEqual(out['native_stage_count'],133);self.assertEqual(out['authority_mode_counts'],{'CONCRETE_PRE_V03':94,'STAGE_DERIVED':15,'ENTRY_PROBE_AUTHORITY':10,'FENCE_BOUND_RECONCILIATION':14})
   self.assertEqual(ver.verify(BIND,bsha,CAT,obj,receipt)['status'],'PASS')
 def test_forward_reference_rejected(self):
  with self.assertRaisesRegex(Exception,'FORWARD_OR_UNKNOWN_REF'):comp.resolve({'x':{'$ref':'future'}},{})
class RuntimeVerifierTests(unittest.TestCase):
 def setUp(self):
  self.td=tempfile.TemporaryDirectory();self.r=Path(self.td.name);self.bsha=hashlib.sha256(BIND.read_bytes()).hexdigest();self.cat=load_catalog(CAT)
  self.row=next(r for r in self.cat['stage_dependencies'] if r['authority_mode']=='STAGE_DERIVED' and r['producer_dependencies'])
  self.receipt=self.r/'receipt.json';self.receipt.write_text(json.dumps({'base_manifest_ref':'a'*64,'suite_ref':'b'*64}))
 def tearDown(self):self.td.cleanup()
 def bundle(self):
  hs=[]
  for d in self.row['producer_dependencies']:
   hs.append({'producer_stage_index':d['producer_stage_index'],'required_route':d['required_route'],'required_state':d['required_state'],'suite_ref':'b'*64,'case_id':self.row['case_id'],'current':True,'lineage_ref':'c'*64,'actual':{'ok':True}})
  return {'schema_version':1,'base_manifest_ref':'a'*64,'suite_ref':'b'*64,'case_id':self.row['case_id'],'stage_index':self.row['stage_index'],'authority_mode':self.row['authority_mode'],'handoffs':hs,'proof_scopes':{},'copy_binding':None}
 def verify(self,b):
  p=self.r/'runtime.json';p.write_text(json.dumps(b));return ver.verify_runtime_bundle(BIND,self.bsha,CAT,self.receipt,p)
 def test_exact_producer_lineage_passes(self):self.assertEqual(self.verify(self.bundle())['status'],'PASS')
 def test_foreign_or_stale_lineage_rejected(self):
  b=self.bundle();b['handoffs'][0]['suite_ref']='d'*64
  with self.assertRaisesRegex(Exception,'FOREIGN_PRODUCER'):self.verify(b)
  b=self.bundle();b['handoffs'][0]['current']=False
  with self.assertRaisesRegex(Exception,'STALE_PRODUCER'):self.verify(b)
 def test_mode_substitution_and_bad_proof_scope_rejected(self):
  b=self.bundle();b['authority_mode']='CONCRETE_PRE_V03'
  with self.assertRaisesRegex(Exception,'RUNTIME_MODE_SUBSTITUTION'):self.verify(b)
  b=self.bundle();b['proof_scopes']={'restore_result':{'host_id':'h'}}
  with self.assertRaises(Exception):self.verify(b)
 def test_copy_hash_and_size_drift_rejected(self):
  b=self.bundle();loc={'host_id':'h','volume_id':'v','canonical_path':r'C:\x\c.tar','purpose':'STAGING_IMPORT','max_bytes':10,'offline_copy_required':True};src={'source_export_ref':'1'*64,'source_host_id':'s','source_volume_id':'sv','source_canonical_path':r'D:\b\c.tar','checkpoint_sha256':'2'*64,'checkpoint_bytes':5};rc={'role':'checkpoint_copy_receipt','schema_version':1,'withdrawn':False,'source_kind':'LAB','source_export_ref':'1'*64,'source_host_id':'s','source_volume_id':'sv','source_canonical_path':r'D:\b\c.tar','source_checkpoint_sha256':'2'*64,'source_checkpoint_bytes':5,'destination':loc,'destination_sha256':'2'*64,'destination_bytes':5,'collector_ref':'3'*64,'raw_artifact_ref':'4'*64,'timestamp_utc':'x'};b['copy_binding']={'source':src,'locator':loc,'receipt':rc};self.assertEqual(self.verify(b)['status'],'PASS');b['copy_binding']['receipt']['destination_bytes']=11
  with self.assertRaises(Exception):self.verify(b)
if __name__=='__main__':unittest.main()
