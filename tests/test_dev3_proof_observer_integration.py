"""Synthetic workspace ONLY: proof graph negatives and concrete observer logic.

No NativeDriver factory/Win32 API/PowerShell/guest/network operation is invoked.
The explicit fake ports here are not available through any production CLI.
"""
from copy import deepcopy
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import patch
import unittest

from helpers import NOW,SID,B,authority_case
from aifilm_p00 import CONTRACT_DIGEST
from aifilm_p00.codec import digest
from aifilm_p00.errors import P00Error
from aifilm_p00.native.proofs import ProofReader
from aifilm_p00.native.session_driver import NativeDriver
from aifilm_p00.native.bindings import verify_volume_coverage
from aifilm_p00.session import Refresh
import test_session_integration as session_fixtures

class BlobFixture:
    """Explicit synthetic dictionary, NOT NativeStore or a trust artifact."""
    def __init__(self,blobs,pins=None):self.blobs=blobs;self.pins=pins or {};self.withdrawn=set()
    def get(self,role,ref):
        if ref in self.withdrawn or (role,ref) not in self.blobs:raise P00Error(15,'FIXTURE_REF_REJECTED')
        return deepcopy(self.blobs[role,ref])

def proof_fixture():
    scope={'host_id':'synthetic-host','checkpoint':'synthetic-checkpoint'}
    claims={'protected':True,'files':['synthetic.bin']}
    ref='synthetic-receipt';measurement='synthetic-measurement'
    docs={
      ('resource_owner','synthetic-owner'):{'withdrawn':False,'owner_sid':SID,'receipt_roles':['protection'], 'host_ids':['synthetic-host']},
      ('collector_release','synthetic-collector'):{'withdrawn':False,'review_verdict':'PASS','build_digest':B},
      ('measurement_artifact','synthetic-raw'):{'withdrawn':False,'measurement_actual_digest':digest(claims),'subject_digest':digest(scope)},
      ('measurement',measurement):{'source_kind':'LAB','status':'OBSERVED','contract_digest':CONTRACT_DIGEST,
        'host_id':'synthetic-host','subject_digest':digest(scope),'actual':claims,'timestamp_utc':(NOW-timedelta(minutes=5)).isoformat(),
        'collector_ref':'synthetic-collector','collector_digest':B,'raw_artifact_ref':'synthetic-raw'},
      ('protection',ref):{'schema_version':1,'withdrawn':False,'contract_digest':CONTRACT_DIGEST,
        'scope':scope,'issued_at':(NOW-timedelta(minutes=1)).isoformat(),'expires_at':(NOW+timedelta(minutes=10)).isoformat(),
        'owner_sid':SID,'authorizer_ref':'synthetic-owner','measurements':[measurement],'claim':claims,
        'claim_map':{k:{'measurement_ref':measurement,'actual_key':k} for k in claims}}
    }
    store=BlobFixture(docs,{'protection':frozenset({ref})})
    return ProofReader(store,'synthetic-host',SID,NOW),store,scope,ref

class Check(unittest.TestCase):
    def reject(self,code,call,*a,**kw):
        with self.assertRaises(P00Error) as e:call(*a,**kw)
        self.assertEqual(int(e.exception.code),code,e.exception.reason)
        return e.exception.reason

class ProofGraphTests(Check):
    def test_exact_graph_maps_each_claim(self):
        r,st,scope,ref=proof_fixture();actual=r.receipt('protection',ref,scope)
        self.assertEqual(actual['claim'],{'protected':True,'files':['synthetic.bin']});self.assertEqual(len(actual['measurements']),1)
    def test_tampered_claim_not_certified_by_unrelated_measurement(self):
        r,st,scope,ref=proof_fixture();st.blobs['protection',ref]['claim']=dict(st.blobs['protection',ref]['claim'],protected=False)
        self.reject(15,r.receipt,'protection',ref,scope)
    def test_extra_flag_requires_claim_map(self):
        r,st,scope,ref=proof_fixture();st.blobs['protection',ref]['claim']={**st.blobs['protection',ref]['claim'],'extra':True}
        self.reject(15,r.receipt,'protection',ref,scope)
    def test_owner_assertion_opt_in_not_native(self):
        r,st,scope,ref=proof_fixture();st.blobs['measurement','synthetic-measurement']['source_kind']='OWNER_ASSERTION'
        self.reject(15,r.receipt,'protection',ref,scope)
        self.assertEqual(r.receipt('protection',ref,scope,owner_assertion=True)['claim']['protected'],True)
    def test_no_candidate_waits_not_fabricated(self):
        r,st,scope,ref=proof_fixture();st.pins={};self.reject(20,r.selected,'protection',scope)
    def test_ambiguous_postcheck_blocks(self):
        r,st,scope,ref=proof_fixture();st.blobs['protection','other']=deepcopy(st.blobs['protection',ref]);st.pins['protection']=frozenset({ref,'other'})
        self.reject(15,r.selected,'protection',scope)
    def test_withdrawn_candidate_not_selected(self):
        r,st,scope,ref=proof_fixture();st.withdrawn.add(ref);self.reject(20,r.selected,'protection',scope)
    def test_pre_operation_receipt_not_postcondition(self):
        r,st,scope,ref=proof_fixture();self.reject(16,r.receipt,'protection',ref,scope,not_before=NOW)

NEGATIVES=[
 ('fixture_receipt',('protection','synthetic-receipt'),'fixture_only',True,15),
 ('withdrawn_receipt',('protection','synthetic-receipt'),'withdrawn',True,15),
 ('old_contract',('protection','synthetic-receipt'),'contract_digest','wrong',16),
 ('expired',('protection','synthetic-receipt'),'expires_at',(NOW-timedelta(seconds=1)).isoformat(),11),
 ('future_issued',('protection','synthetic-receipt'),'issued_at',(NOW+timedelta(seconds=1)).isoformat(),11),
 ('no_measurements',('protection','synthetic-receipt'),'measurements',[],15),
 ('wrong_owner',('resource_owner','synthetic-owner'),'owner_sid','other',12),
 ('owner_withdrawn',('resource_owner','synthetic-owner'),'withdrawn',True,12),
 ('owner_fixture',('resource_owner','synthetic-owner'),'fixture_only',True,12),
 ('owner_other_host',('resource_owner','synthetic-owner'),'host_ids',['other'],12),
 ('owner_other_role',('resource_owner','synthetic-owner'),'receipt_roles',['other'],12),
 ('fixture_measurement',('measurement','synthetic-measurement'),'fixture_only',True,15),
 ('workspace_measurement',('measurement','synthetic-measurement'),'source_kind','WORKSPACE_TEST',15),
 ('not_run_measurement',('measurement','synthetic-measurement'),'status','NOT_RUN',15),
 ('missing_actual',('measurement','synthetic-measurement'),'actual',{},15),
 ('wrong_measurement_host',('measurement','synthetic-measurement'),'host_id','other',16),
 ('wrong_subject',('measurement','synthetic-measurement'),'subject_digest','other',16),
 ('future_measurement',('measurement','synthetic-measurement'),'timestamp_utc',NOW.isoformat(),15),
 ('no_provenance',('measurement','synthetic-measurement'),'raw_artifact_ref',None,15),
 ('unreviewed_collector',('collector_release','synthetic-collector'),'review_verdict','NOT_PERFORMED',15),
 ('withdrawn_collector',('collector_release','synthetic-collector'),'withdrawn',True,15),
 ('wrong_build',('collector_release','synthetic-collector'),'build_digest','other',15),
 ('raw_not_bound',('measurement_artifact','synthetic-raw'),'measurement_actual_digest','other',15),
 ('withdrawn_raw',('measurement_artifact','synthetic-raw'),'withdrawn',True,15),
]
for name,key,field,value,code in NEGATIVES:
    def test(self,key=key,field=field,value=value,code=code):
        r,st,scope,ref=proof_fixture();st.blobs[key][field]=deepcopy(value)
        self.reject(code,r.receipt,'protection',ref,scope)
    setattr(ProofGraphTests,'test_reject_'+name,test)

class ObserverTests(Check):
    def setup(self,action='OBSERVE_HOST'):
        _,p,ctx,store=authority_case('PASSIVE');s=p['semantic'];s['operations']=[{'action':action,'class':'C0'}]
        material={'features':[{'name':'VirtualMachinePlatform','state':'Enabled'}]}
        s['before']=deepcopy(material);s['expected_after']=deepcopy(material)
        driver=NativeDriver.__new__(NativeDriver);driver.binding={'after_by_action':{action:{'material':deepcopy(material),'captures':[]}},'features':['VirtualMachinePlatform']}
        driver.actual_steps={};driver.source_kind='LAB';driver.system=SimpleNamespace(all_writers=lambda _: {'all_terminal':True},installer_idle=lambda _: {'idle':True})
        events=[];c=SimpleNamespace(fence={'native':None,'action':action,'witness':{'host_boot':'boot-a'}},storage=SimpleNamespace(append_event=events.append))
        fresh=Refresh(ctx,store,{'material':material,'target':None,'host':{'boot_utc':'boot-a'},'running':[]},1,'WORKSPACE_TEST')
        return driver,p,fresh,c,events
    def test_metadata_observer_actual_after_state(self):
        d,p,f,c,e=self.setup();comp=d._after(p,0,{'exit':0},f,c)
        self.assertTrue(comp.postconditions_observed);self.assertEqual(e[-1]['kind'],'OPERATION_AFTER_OBSERVED')
    def test_actual_features_not_exit_code(self):
        d,p,f,c,e=self.setup('ENABLE_PREREQUISITES');f.observed['material']['features'][0]['state']='Disabled'
        self.reject(19,d._after,p,0,{'exit':0},f,c);self.assertEqual(e,[])
    def test_pending_service_blocks_commit(self):
        d,p,f,c,e=self.setup('ENABLE_PREREQUISITES')
        def pending(_):raise P00Error(21,'NATIVE_SERVICE_PENDING')
        d.system.installer_idle=pending;self.reject(21,d._after,p,0,{'exit':0},f,c);self.assertEqual(e,[])
    def test_pending_writer_checked_before_metadata(self):
        d,p,f,c,e=self.setup()
        def pending(_):raise P00Error(21,'NATIVE_WRITER_PENDING')
        d.system.all_writers=pending;self.reject(21,d._after,p,0,{'exit':0},f,c);self.assertEqual(e,[])
    def test_full_afterstate_drift_blocks(self):
        d,p,f,c,e=self.setup();f.observed['material']['different']=True
        self.reject(16,d._after,p,0,{'exit':0},f,c);self.assertEqual(e,[])
    def test_guest_route_process_exit_not_actual_capture(self):
        d,p,f,c,e=self.setup('CREATE_WORKSPACE');self.reject(19,d._after,p,0,{'exit':0},f,c)
    def test_noop_metadata_only_does_not_report_ready(self):
        d,p,f,c,e=self.setup();completed={0:{'evidence_digest':'old'}}
        self.assertEqual(self.reject(11,d.final_assertions,p,f,c,completed),'LIVE_REVALIDATION_REQUIRED')
    def test_stage_snapshot_failure_preserves_uncommitted_completion(self):
        d,p,f,c,e=self.setup();d.refresh=lambda *a,**k:f
        from aifilm_p00.native.evidence_pipeline import NativeEvidencePipeline
        with patch('aifilm_p00.native.session_driver.authorize'),patch.object(NativeEvidencePipeline,'capture',side_effect=P00Error(18,'NATIVE_DISK_WRITE')):
            self.reject(18,d.observe,p,0,{'exit':0},f,c)
        self.assertEqual(e[-1]['kind'],'OPERATION_AFTER_OBSERVED')
        self.assertFalse(any(x['kind']=='TERMINAL' for x in e))

class SnapshotBudgetTests(Check):
    def setup(self,peak=4096):
        paths=SimpleNamespace(root=r'C:\P00',volume=lambda _: {'volume_id':'v','filesystem':'NTFS'})
        b={'scratch_directory':r'C:\P00\scratch','snapshot_maximum_bytes':1024}
        s={'target':{'base_path':None},'operations':[{},{}]}
        budgets=[{'volume_id':'v','roles':['OS','EVIDENCE'],'allocations':{'snapshots':peak}}]
        return paths,b,s,budgets
    def test_two_pending_snapshots_need_two_allocations(self):
        p,b,s,budget=self.setup(1024);self.reject(13,verify_volume_coverage,p,r'C:\Windows',b,s,budget,pending_snapshots=2)
    def test_committed_snapshots_not_counted_again(self):
        p,b,s,budget=self.setup(0);self.assertTrue(verify_volume_coverage(p,r'C:\Windows',b,s,budget,pending_snapshots=0))
    def test_negative_pending_count_rejected(self):
        p,b,s,budget=self.setup();self.reject(10,verify_volume_coverage,p,r'C:\Windows',b,s,budget,pending_snapshots=-1)

# Reuse only its explicit workspace fixture constructor, not its whole TestCase
# inheritance: avoids reporting the same 27 tests twice.
class OutcomeTests(Check):
    def setup(self,purpose='SUPPORT_BUNDLE'):
        return session_fixtures.SessionTests.setup(self,purpose)
    def test_partial_outcome_not_erased_by_terminal_commit(self):
        r,d,st,g,i,p=self.setup();d.final_assertions=lambda *a:{'interface_outcome':{'exit':2,'state':'PARTIAL_OPTIONAL'}}
        out=r.execute(i,p);self.assertEqual(out['exit'],2);self.assertEqual(out['state'],'PARTIAL_OPTIONAL')
    def test_missing_mandatory_not_promoted_to_success(self):
        r,d,st,g,i,p=self.setup();d.final_assertions=lambda *a:{'interface_outcome':{'exit':22,'state':'INCOMPLETE_MANDATORY'}}
        self.assertEqual(r.execute(i,p)['exit'],22)
    def test_privacy_block_stays_23(self):
        r,d,st,g,i,p=self.setup();d.final_assertions=lambda *a:{'interface_outcome':{'exit':23,'state':'BLOCKED_REDACTION'}}
        self.assertEqual(r.execute(i,p)['exit'],23)
    def test_non_bundle_cannot_report_optional_partial(self):
        r,d,st,g,i,p=self.setup('CREATE');d.final_assertions=lambda *a:{'interface_outcome':{'exit':2,'state':'PARTIAL_OPTIONAL'}}
        self.reject(19,r.execute,i,p)
    def test_code_state_mismatch_blocked(self):
        r,d,st,g,i,p=self.setup();d.final_assertions=lambda *a:{'interface_outcome':{'exit':0,'state':'PARTIAL_OPTIONAL'}}
        self.reject(19,r.execute,i,p)

