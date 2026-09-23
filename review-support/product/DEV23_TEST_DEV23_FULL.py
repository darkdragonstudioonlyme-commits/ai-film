import ast
import hashlib
import inspect
import json
from pathlib import Path
import tomllib
import unittest
from unittest import mock
from helpers import binding

from aifilm_p00 import CONTRACT_DIGEST, NATIVE_BACKEND_AVAILABLE, __version__
from aifilm_p00.codec import canonical, digest, sha256
from aifilm_p00.errors import P00Error
from aifilm_p00.native.harness_cases import procedure
from aifilm_p00.native.stage_authority import (
    EXPECTED_MODE_COUNTS, LATE_PROOF_SLOTS, MODE_COUNTS, RULES,
    authority_rule, build_next_policy, classify_publication, generation_record,
    manifest_for_suite, object_ref, select_destination_locator,
    validate_base_manifest, validate_catalog_invariants, validate_copy_receipt,
    validate_destination_allowlist, validate_late_proof_scope, validate_request_row,
    materialize_stage_objects, validate_lineage, lineage_revocation_refs, publish_candidate,
    prepare_lineage_revocation, resolve_reconciliation_plan,
)

H='a'*64

EXPECTED_LATE_PROOF_CONTRACT = {
    'source_manifest': {'scope_fields':['host_id','target_registration','source_class'],'owner_assertion':True},
    'protection': {'scope_fields':['host_id','source_witness'],'owner_assertion':True},
    'restore_envelope': {'scope_fields':['host_id','checkpoint_digest','envelope_digest'],'owner_assertion':False},
    'user_init_receipt': {'scope_fields':['host_id','plan_digest','target_registration','user'],'owner_assertion':False},
    'c3_postchecks': {'scope_fields':['host_id','plan_digest','host_boot'],'owner_assertion':True},
    'operation_postcheck': {'scope_variants':[
        ['host_id','plan_digest','step_id','target_registration','host_boot'],
        ['host_id','plan_digest','execution_phase','baseline_digest','host_boot','target_registration']], 'owner_assertion':False},
    'run_revocation': {'scope_fields':['host_id','original_plan_digest','recovery_request_digest','disposition'],'owner_assertion':True},
    'read_absence_observation': {'scope_fields':['host_id','original_plan_digest','read_id','intent_digest','command_digest'],'owner_assertion':False},
    'restore_result': {'scope_fields':['host_id','checkpoint_digest','source_target_registration'],'owner_assertion':False},
}

ACCEPTED_PRIMITIVE_SHA256 = {
    'src/aifilm_p00/native/request_entry.py':'9f94cb7bfdbf5217ff330c5b3bcf74c1ad951a54d2ae9a2ef28520564bd036e3',
    'src/aifilm_p00/native/trust.py':'fa14b8d76d9967cb9f66600ec186ec8b2601ea6a2fc377f8a4cdc3bcd7d09e08',
    'src/aifilm_p00/session.py':'184c20ea26c3b082a17c6de99b7c3f1137c2e55d203b1c8f3975ef6a54eefdab',
    'src/aifilm_p00/native/proofs.py':'bb1977bb25b7f2612822f8a16fc5ee9d1d944de31da817b4c9d364920c13be9f',
    'src/aifilm_p00/admission.py':'619726fd419846da5cd5dbd07b9584a84ee2cf5e082254a9d136c89c17e59533',
    'src/aifilm_p00/native/coordination.py':'d40024d253dda9d5a3639d202dad6ff3bcdd8118b746be836ec824fe268714cc',
}

class Store:
    def __init__(self, objects):
        self.objects=objects
        self.pins={}
        for (role,ref),value in objects.items(): self.pins.setdefault(role,set()).add(ref)
        self.pins={k:frozenset(v) for k,v in self.pins.items()}
        self.withdrawn=frozenset()
        self.generation=1
        self.policy_digest='e'*64
    def get(self,role,ref):
        if (role,ref) not in self.objects: raise P00Error(15,'UNTRUSTED_DOCUMENT')
        return self.objects[(role,ref)]

def add(objects,role,value):
    value={'role':role,**value}
    ref=object_ref(value);objects[(role,ref)]=value;return ref

def suite(case_id='T00-09'):
    return {'role':'lab_acceptance_suite','schema_version':1,'withdrawn':False,'approved':True,'source_kind':'LAB',
            'host_id':'lab-host','owner_sid':'S-1-5-21-1','build_digest':'b'*64,'test_set_digest':'c'*64,
            'contract_digest':CONTRACT_DIGEST,'execution_id':'exec-1','issued_at':'2026-09-22T00:00:00Z',
            'expires_at':'2026-09-22T23:00:00Z','cases':{case_id:{}}}

def descriptor(s):
    return {'schema_version':1,'withdrawn':False,'source_kind':'LAB','host_id':s['host_id'],'owner_sid':s['owner_sid'],
            'build_digest':s['build_digest'],'test_set_digest':s['test_set_digest'],'contract_digest':CONTRACT_DIGEST,
            'execution_id':s['execution_id'],'host_roles':{'source':'lab-host','destination':'lab-host'},
            'issued_at':s['issued_at'],'expires_at':s['expires_at']}

def manifest(objects,suite_ref,descriptor_ref,extra):
    entries=[{'role':'lab_acceptance_suite','ref':suite_ref},{'role':'lab_campaign_descriptor','ref':descriptor_ref},*extra]
    entries=sorted(entries,key=lambda x:(x['role'],x['ref']))
    return add(objects,'lab_base_manifest',{'schema_version':1,'withdrawn':False,'source_kind':'LAB',
        'descriptor_ref':descriptor_ref,'entries':entries})


def policy_bytes(objects,generation=1,withdrawn=()):
    pins={};blobs={}
    for (role,ref),value in objects.items():
        pins.setdefault(role,[]).append(ref);blobs[ref]=canonical(value).decode('utf-8')
    return canonical({'schema_version':1,'host_id':'lab-host','operator_sids':['S-1-5-21-1'],
        'role_pins':{k:sorted(v) for k,v in pins.items()},'blobs':blobs,'withdrawn_refs':sorted(withdrawn),'generation':generation})

class CatalogTests(unittest.TestCase):
    def test_catalog_exact_population(self):
        from collections import Counter
        reviewed={'CONCRETE_PRE_V03':94,'STAGE_DERIVED':15,'ENTRY_PROBE_AUTHORITY':10,'FENCE_BOUND_RECONCILIATION':14}
        actual=dict(Counter(row['authority_mode'] for row in RULES.values()))
        self.assertTrue(validate_catalog_invariants());self.assertEqual(len(RULES),133);self.assertEqual(actual,reviewed);self.assertEqual(MODE_COUNTS,reviewed)
    def test_exact_modes(self):
        self.assertEqual(authority_rule('T00-09',1)['authority_mode'],'STAGE_DERIVED')
        self.assertEqual(authority_rule('T00-07',1)['authority_mode'],'FENCE_BOUND_RECONCILIATION')
        self.assertEqual(authority_rule('T00-14',0)['authority_mode'],'ENTRY_PROBE_AUTHORITY')
    def test_route_drift_rejected(self):
        with self.assertRaises(P00Error): authority_rule('T00-09',1,'CREATE')

class ManifestTests(unittest.TestCase):
    def setUp(self):
        self.objects={};self.s=suite();self.sref=add(self.objects,'lab_acceptance_suite',{k:v for k,v in self.s.items() if k!='role'});self.dref=add(self.objects,'lab_campaign_descriptor',descriptor(self.s))
    def test_manifest_selects_exact_suite(self):
        mref=manifest(self.objects,self.sref,self.dref,[]);ref,m=manifest_for_suite(Store(self.objects),self.sref);self.assertEqual(ref,mref);self.assertEqual(m['descriptor_ref'],self.dref)
    def test_unsorted_manifest_rejected(self):
        value={'role':'lab_base_manifest','schema_version':1,'withdrawn':False,'source_kind':'LAB','descriptor_ref':self.dref,
               'entries':[{'role':'lab_campaign_descriptor','ref':self.dref},{'role':'lab_acceptance_suite','ref':self.sref}]}
        ref=object_ref(value);self.objects[('lab_base_manifest',ref)]=value
        with self.assertRaises(P00Error): validate_base_manifest(Store(self.objects),ref,self.sref)
    def test_unrelated_manifest_does_not_break_suite_selection(self):
        mref=manifest(self.objects,self.sref,self.dref,[])
        other_suite='e'*64;other_desc='f'*64
        add(self.objects,'lab_base_manifest',{'schema_version':1,'withdrawn':False,'source_kind':'LAB','descriptor_ref':other_desc,
            'entries':sorted([{'role':'lab_acceptance_suite','ref':other_suite},{'role':'lab_campaign_descriptor','ref':other_desc}],key=lambda x:(x['role'],x['ref']))})
        ref,_=manifest_for_suite(Store(self.objects),self.sref);self.assertEqual(ref,mref)

    def test_manifest_self_reference_rejected(self):
        # The ref cannot appear in its own canonical entry set; a hash-shaped fake still fails exact self rule if selected.
        fake='f'*64;value={'role':'lab_base_manifest','schema_version':1,'withdrawn':False,'source_kind':'LAB','descriptor_ref':self.dref,
            'entries':sorted([{'role':'lab_acceptance_suite','ref':self.sref},{'role':'lab_base_manifest','ref':fake},{'role':'lab_campaign_descriptor','ref':self.dref}],key=lambda x:(x['role'],x['ref']))}
        self.objects[('lab_base_manifest',fake)]=value
        with self.assertRaises(P00Error): validate_base_manifest(Store(self.objects),fake,self.sref)

class LocatorProofTests(unittest.TestCase):
    def locator(self,host='lab-host',offline=True,path=r'C:\staging\checkpoint.tar'):
        return {'host_id':host,'volume_id':'VOL1','canonical_path':path,'purpose':'STAGING_IMPORT','max_bytes':1000,'offline_copy_required':offline}
    def test_locator_selection_exact(self):
        x=self.locator();self.assertEqual(select_destination_locator([x],'lab-host',require_offline=True),x)
    def test_ambiguous_locator_rejected(self):
        a=self.locator(path=r'C:\staging\a.tar');b=self.locator(path=r'C:\staging\b.tar')
        rows=sorted([a,b],key=lambda x:(x['host_id'],x['volume_id'],x['canonical_path']))
        with self.assertRaises(P00Error): select_destination_locator(rows,'lab-host',require_offline=True)
    def test_copy_receipt_binds_source_and_destination(self):
        loc=self.locator();src={'source_export_ref':'2'*64,'source_host_id':'source','source_volume_id':'SRC','source_canonical_path':r'D:\backup\c.tar','checkpoint_sha256':'1'*64,'checkpoint_bytes':500}
        r={'role':'checkpoint_copy_receipt','schema_version':1,'withdrawn':False,'source_kind':'LAB','source_export_ref':'2'*64,
           'source_host_id':'source','source_volume_id':'SRC','source_canonical_path':r'D:\backup\c.tar','source_checkpoint_sha256':'1'*64,
           'source_checkpoint_bytes':500,'destination':loc,'destination_sha256':'1'*64,'destination_bytes':500,
           'collector_ref':'3'*64,'raw_artifact_ref':'4'*64,'timestamp_utc':'2026-09-22T01:00:00Z'}
        self.assertIs(validate_copy_receipt(r,src,loc),r)
        wrong_ref=dict(r);wrong_ref['source_export_ref']='9'*64
        with self.assertRaises(P00Error): validate_copy_receipt(wrong_ref,src,loc)
        r=dict(r);r['destination_sha256']='9'*64
        with self.assertRaises(P00Error): validate_copy_receipt(r,src,loc)
        wrong_bytes=dict(r);wrong_bytes['destination_sha256']='1'*64;wrong_bytes['destination_bytes']=499
        with self.assertRaises(P00Error): validate_copy_receipt(wrong_bytes,src,loc)
        too_large=dict(r);too_large['destination_sha256']='1'*64;too_large['destination_bytes']=1500;too_large['source_checkpoint_bytes']=1500
        src_too_large=dict(src);src_too_large['checkpoint_bytes']=1500
        with self.assertRaises(P00Error): validate_copy_receipt(too_large,src_too_large,loc)
    def test_late_proof_contract_matches_reviewed_design_independently(self):
        self.assertEqual(set(LATE_PROOF_SLOTS),set(EXPECTED_LATE_PROOF_CONTRACT))
        for role,expected in EXPECTED_LATE_PROOF_CONTRACT.items():
            actual=LATE_PROOF_SLOTS[role]
            self.assertEqual(actual['owner_assertion'],expected['owner_assertion'])
            if 'scope_fields' in expected:
                self.assertEqual(actual.get('scope_fields'),expected['scope_fields'])
                self.assertNotIn('scope_variants',actual)
            else:
                self.assertEqual(actual.get('scope_variants'),expected['scope_variants'])
                self.assertNotIn('scope_fields',actual)

    def test_nine_proof_scope_contracts(self):
        self.assertEqual(len(LATE_PROOF_SLOTS),9)
        for role,spec in LATE_PROOF_SLOTS.items():
            variants=spec.get('scope_variants',[spec.get('scope_fields')])
            for fields in variants:
                scope={k:'x' for k in fields};self.assertEqual(validate_late_proof_scope(role,scope),spec)
                bad=dict(scope);bad['extra']='x'
                with self.assertRaises(P00Error): validate_late_proof_scope(role,bad)

    def test_read_absence_scope_binds_exact_intent(self):
        fields=LATE_PROOF_SLOTS['read_absence_observation']['scope_fields']
        self.assertEqual(fields,['host_id','original_plan_digest','read_id','intent_digest','command_digest'])
        scope={k:'x' for k in fields};self.assertEqual(validate_late_proof_scope('read_absence_observation',scope),LATE_PROOF_SLOTS['read_absence_observation'])
        with self.assertRaises(P00Error): validate_late_proof_scope('read_absence_observation',{'host_id':'x','read_id':'x'})

    def test_operation_postcheck_supports_both_exact_consumers(self):
        variants=LATE_PROOF_SLOTS['operation_postcheck']['scope_variants'];self.assertEqual(len(variants),2)
        for fields in variants:self.assertEqual(validate_late_proof_scope('operation_postcheck',{k:'x' for k in fields}),LATE_PROOF_SLOTS['operation_postcheck'])
        merged={k:'x' for fields in variants for k in fields}
        with self.assertRaises(P00Error): validate_late_proof_scope('operation_postcheck',merged)

    def test_run_revocation_scope_matches_consumer(self):
        fields=LATE_PROOF_SLOTS['run_revocation']['scope_fields']
        self.assertEqual(fields,['host_id','original_plan_digest','recovery_request_digest','disposition'])
        self.assertEqual(validate_late_proof_scope('run_revocation',{k:'x' for k in fields}),LATE_PROOF_SLOTS['run_revocation'])
    def test_owner_assertion_policy_is_exact(self):
        spec=LATE_PROOF_SLOTS['restore_envelope'];scope={k:'x' for k in spec['scope_fields']}
        with self.assertRaises(P00Error): validate_late_proof_scope('restore_envelope',scope,owner_assertion=True)

class RequestModeTests(unittest.TestCase):
    def concrete_store(self,case='T00-02',index=0):
        objects={};s=suite(case);sref=add(objects,'lab_acceptance_suite',{k:v for k,v in s.items() if k!='role'});dref=add(objects,'lab_campaign_descriptor',descriptor(s));plan='1'*64
        # Manifest membership is authority; test store need not contain the plan body for static request shape.
        mref=manifest(objects,sref,dref,[{'role':'execution_plan','ref':plan}]);return Store(objects),s,sref,plan,mref
    def test_legacy_concrete_only_on_concrete_rule(self):
        store,s,sref,plan,_=self.concrete_store();proc=procedure('T00-02')
        row=validate_request_row(store,sref,s,'T00-02',proc,0,{'route':proc.routes[0],'interface':'verify','plan_ref':plan})
        self.assertEqual(row['authority_mode'],'CONCRETE_PRE_V03')
    def test_legacy_plan_rejected_for_derived_stage(self):
        objects={};s=suite('T00-09');sref=add(objects,'lab_acceptance_suite',{k:v for k,v in s.items() if k!='role'});dref=add(objects,'lab_campaign_descriptor',descriptor(s));plan='1'*64;manifest(objects,sref,dref,[{'role':'execution_plan','ref':plan}])
        with self.assertRaises(P00Error): validate_request_row(Store(objects),sref,s,'T00-09',procedure('T00-09'),1,{'route':'RESTORE_IMPORT','interface':'apply','plan_ref':plan})

class GenerationTests(unittest.TestCase):
    def parent(self):
        return canonical({'schema_version':1,'host_id':'lab-host','operator_sids':['S-1-5-21-1'],'role_pins':{'registration':['1'*64]},
                          'blobs':{'1'*64:'{}'},'withdrawn_refs':[],'generation':1})
    def test_generation_record_excludes_future_policy_digest(self):
        raw=self.parent();ref,g=generation_record(raw,'2'*64,{'execution_plan':['3'*64]},'4'*64)
        self.assertEqual(g['parent_policy_digest'],sha256(raw));self.assertEqual(g['new_generation'],2);self.assertNotIn('new_policy_digest',g);self.assertEqual(ref,object_ref(g))
    def test_next_policy_is_monotonic_and_preserves_parent(self):
        raw=self.parent();obj={'role':'execution_plan','schema_version':1,'withdrawn':False,'x':1};oref=object_ref(obj)
        _,g=generation_record(raw,'2'*64,{'execution_plan':[oref]},'4'*64);n,refs,gref=build_next_policy(raw,{'execution_plan':[obj]},g)
        p=json.loads(n);self.assertEqual(set(p),{'schema_version','host_id','operator_sids','role_pins','blobs','withdrawn_refs','generation'});self.assertEqual(p['generation'],2);self.assertIn('1'*64,p['role_pins']['registration']);self.assertEqual(refs['execution_plan'],[oref]);self.assertIn(gref,p['role_pins']['lab_authority_generation'])
    def test_recovery_classifier_never_overwrites_unknown_parent(self):
        p=b'parent';c=b'candidate'
        self.assertEqual(classify_publication(p,c,p,'ABSENT'),'WRITE_CANDIDATE')
        self.assertEqual(classify_publication(p,c,c,'ABSENT'),'APPEND_EVENT')
        self.assertEqual(classify_publication(p,c,c,'EXACT'),'COMPLETE')
        self.assertEqual(classify_publication(p,c,b'newer','ABSENT'),'RECONCILE_REQUIRED')
        self.assertEqual(classify_publication(p,c,p,'EXACT'),'RECONCILE_REQUIRED')
    def test_single_selection_augmentation_rejected(self):
        raw=self.parent();obj={'role':'code','schema_version':1,'withdrawn':False};oref=object_ref(obj)
        _,g=generation_record(raw,'2'*64,{'code':[oref]},'4'*64)
        with self.assertRaises(P00Error): build_next_policy(raw,{'code':[obj]},g)
    def test_immutable_base_withdrawal_rejected(self):
        raw=self.parent();_,g=generation_record(raw,'2'*64,{},'4'*64,['1'*64])
        with self.assertRaises(P00Error): build_next_policy(raw,{},g,['1'*64],['1'*64])


class MaterializationTests(unittest.TestCase):
    def setUp(self):
        self.objects={};self.s=suite('T00-14');self.sref=add(self.objects,'lab_acceptance_suite',{k:v for k,v in self.s.items() if k!='role'})
        self.dref=add(self.objects,'lab_campaign_descriptor',descriptor(self.s))
        self.proc=procedure('T00-14');self.rule=authority_rule('T00-14',3)
        before={'distros':{'rows':[],'default':None},'runtime':{'status':'PRESENT'},'features':[]}
        after={'distros':{'rows':[{'name':'AI-Film','registration_id':'{11111111-1111-1111-1111-111111111111}','base_path':r'D:\AI-Film','default_uid':1000}],'default':'{11111111-1111-1111-1111-111111111111}'},'runtime':{'status':'PRESENT'},'features':[]}
        profile={'windows_build':'B','wsl_version':'2','kernel':'K','network':'NAT','storage':'NTFS','startup':'CLEAN_P00'}
        semantic={'schema_version':1,'run_id':'run-derived','work_item':'IMPL-P00-V03-STAGE-DERIVED-AUTHORITY-DEV23','execution_class':'LAB',
          'host_id':self.s['host_id'],'owner_sid':self.s['owner_sid'],'target':{'name':'AI-Film','base_path':r'D:\AI-Film','registration_id':None,'user':'film'},
          'purpose':'CREATE','contract_digest':CONTRACT_DIGEST,'build_digest':self.s['build_digest'],'test_set_digest':self.s['test_set_digest'],
          'profile':{'$late':'semantic.profile'},'before':{'$late':'semantic.before'},'expected_after':{'$late':'semantic.expected_after'},
          'budgets':[{'volume_id':'VOL1','roles':['OS','DISTRO','EVIDENCE'],'allocations':{'distro':1024,'logs':1024}}],
          'payload_digest':None,'source_class':'NOT_YET_CREATED',
          'refs':{'registration':'1'*64,'design':'2'*64,'code':'3'*64,'lab_plan':'4'*64,'payload':'5'*64,'native_binding':{'$late':'semantic.refs.native_binding'}},
          'final_state':'RUNNING'}
        pt={'schema_version':1,'withdrawn':False,'source_kind':'LAB','campaign_descriptor_ref':self.dref,'case_id':'T00-14',
            'procedure_digest':self.proc.procedure_digest,'stage_index':3,'route':'CREATE','interface':'apply','semantic_template':semantic,'created_at':'2026-09-22T01:00:00Z'}
        self.ptref=add(self.objects,'lab_stage_plan_template',pt)
        actions=['INSTALL_DISTRO','AWAIT_OWNER_USER_INIT','CREATE_WORKSPACE']
        bt={'schema_version':1,'withdrawn':False,'source_kind':'LAB','campaign_descriptor_ref':self.dref,'case_id':'T00-14',
            'procedure_digest':self.proc.procedure_digest,'stage_index':3,'route':'CREATE',
            'binding_template':{'schema_version':1,'host_id':self.s['host_id'],'owner_sid':self.s['owner_sid'],'withdrawn':False,
                'profile_catalog_ref':'6'*64,'executable_policy_ref':'7'*64,'volume_paths':{},
                'allocation_lifetimes':{'VOL1':{'distro':2,'logs':None}},'scratch_directory':r'C:\ProgramData\AI-FILM\scratch',
                'after_by_action':{a:{'material':after,'captures':[]} for a in actions},'snapshot_maximum_bytes':1024,
                'workspace':r'/home/film/ai-film','critical_files':['/etc/os-release'],
                'timeout_seconds':{'INSTALL_DISTRO':60}},'selectors':{}}
        self.btref=add(self.objects,'lab_native_binding_template',bt)
        slot={'schema_version':1,'withdrawn':False,'source_kind':'LAB','host_id':self.s['host_id'],'owner_sid':self.s['owner_sid'],
            'build_digest':self.s['build_digest'],'test_set_digest':self.s['test_set_digest'],'contract_digest':CONTRACT_DIGEST,
            'execution_id':self.s['execution_id'],'case_id':'T00-14','procedure_digest':self.proc.procedure_digest,'stage_index':3,
            'route':'CREATE','interface':'apply','authority_mode':'STAGE_DERIVED','campaign_descriptor_ref':self.dref,
            'plan_template_ref':self.ptref,'native_binding_template_ref':self.btref,'producer_dependencies':self.rule['producer_dependencies'],
            'late_fields':self.rule['late_fields'],'derived_object_roles':self.rule['derived_object_roles'],'maximum_approval_seconds':3600,
            'destination_locator_allowlist':[],'reconciliation_plan_refs':[],
            'semantic_selectors':{'semantic.before':{'producer_stage_index':2,'actual_path':['material_after_or_current']},
                                  'semantic.profile':{'producer_stage_index':2,'actual_path':['matched_profile']}}}
        self.slotref=add(self.objects,'lab_stage_derivation_slot',slot)
        manifest(self.objects,self.sref,self.dref,[{'role':'lab_stage_plan_template','ref':self.ptref},
            {'role':'lab_native_binding_template','ref':self.btref},{'role':'lab_stage_derivation_slot','ref':self.slotref}])
        hand={'schema_version':1,'withdrawn':False,'source_kind':'LAB','host_id':self.s['host_id'],'owner_sid':self.s['owner_sid'],
            'execution_id':self.s['execution_id'],'suite_ref':self.sref,'case_id':'T00-14','procedure_digest':self.proc.procedure_digest,
            'stage_index':2,'route':'ENGINE','plan_digest':'8'*64,'stage_ref':'9'*64,'state':'TERMINAL_OBSERVATION_WITH_CURRENT_MATERIAL',
            'evidence_digest':'a'*64,'actual':{'material_after_or_current':before,'matched_profile':profile},'timestamp_utc':'2026-09-22T02:00:00Z'}
        self.href=add(self.objects,'lab_stage_state_handoff',hand);self.store=Store(self.objects)

    def test_materializes_binding_plan_approval_lineage(self):
        from aifilm_p00.codec import instant
        out=materialize_stage_objects(self.store,self.sref,self.s,'T00-14',3,self.proc,self.slotref,instant('2026-09-22T02:30:00Z'))
        self.assertEqual(out['plan']['semantic']['before'],self.objects[('lab_stage_state_handoff',self.href)]['actual']['material_after_or_current'])
        self.assertEqual(out['plan']['semantic']['profile'],self.objects[('lab_stage_state_handoff',self.href)]['actual']['matched_profile'])
        self.assertEqual(out['lineage']['producer_handoff_refs'],[self.href])
        self.assertEqual(set(out['additions']),{'native_binding','approval','execution_plan','lab_derived_stage_authority'})

    def test_lineage_validation_and_atomic_revocation_set(self):
        from aifilm_p00.codec import instant
        out=materialize_stage_objects(self.store,self.sref,self.s,'T00-14',3,self.proc,self.slotref,instant('2026-09-22T02:30:00Z'))
        for role,objs in out['additions'].items():
            for obj in objs: add(self.objects,role,{k:v for k,v in obj.items() if k!='role'})
        self.store=Store(self.objects);self.store.generation=2
        validate_lineage(self.store,out['lineage_ref'],self.sref,'T00-14',3,self.slotref)
        refs=lineage_revocation_refs(self.store,out['lineage_ref']);self.assertIn(out['lineage_ref'],refs);self.assertIn(out['execution_plan_ref'],refs);self.assertGreaterEqual(len(refs),4)

    def test_missing_selector_is_rejected(self):
        slot=self.objects[('lab_stage_derivation_slot',self.slotref)];slot['semantic_selectors'].pop('semantic.profile')
        from aifilm_p00.codec import instant
        with self.assertRaises(P00Error): materialize_stage_objects(self.store,self.sref,self.s,'T00-14',3,self.proc,self.slotref,instant('2026-09-22T02:30:00Z'))
    def test_binding_selector_cannot_change_timeout_authority(self):
        bt=self.objects[('lab_native_binding_template',self.btref)];bt['binding_template']['timeout_seconds']['INSTALL_DISTRO']={'$late':'binding.timeout_seconds.INSTALL_DISTRO'}
        bt['selectors']={'binding.timeout_seconds.INSTALL_DISTRO':{'producer_stage_index':2,'actual_path':['matched_profile']}}
        from aifilm_p00.codec import instant
        with self.assertRaises(P00Error): materialize_stage_objects(self.store,self.sref,self.s,'T00-14',3,self.proc,self.slotref,instant('2026-09-22T02:30:00Z'))
    def test_revocation_withdraws_entire_derived_set(self):
        from aifilm_p00.codec import instant
        out=materialize_stage_objects(self.store,self.sref,self.s,'T00-14',3,self.proc,self.slotref,instant('2026-09-22T02:30:00Z'))
        for role,objs in out['additions'].items():
            for obj in objs:add(self.objects,role,{k:v for k,v in obj.items() if k!='role'})
        st=Store(self.objects);st.generation=2;st.policy_digest=sha256(policy_bytes(self.objects,2))
        rev=prepare_lineage_revocation(policy_bytes(self.objects,2),st,out['lineage_ref'],'f'*64)
        candidate=json.loads(rev['candidate_policy_bytes']);self.assertEqual(set(rev['withdrawn_refs']),set(lineage_revocation_refs(st,out['lineage_ref'])))
        self.assertTrue(set(rev['withdrawn_refs'])<=set(candidate['withdrawn_refs']))
        manifest_doc=st.get('lab_base_manifest',out['manifest_ref']);self.assertFalse({x['ref'] for x in manifest_doc['entries']}&set(rev['withdrawn_refs']))



class EntryFenceTests(unittest.TestCase):
    def test_entry_probe_binds_exact_presigned_plan(self):
        objects={};s=suite('T00-14');sref=add(objects,'lab_acceptance_suite',{k:v for k,v in s.items() if k!='role'});dref=add(objects,'lab_campaign_descriptor',descriptor(s))
        rule=authority_rule('T00-14',0);plan='1'*64
        probe=add(objects,'entry_probe_set',{'schema_version':1,'withdrawn':False,'source_kind':'LAB','host_id':s['host_id'],'owner_sid':s['owner_sid'],
            'build_digest':s['build_digest'],'test_set_digest':s['test_set_digest'],'contract_digest':CONTRACT_DIGEST,'execution_id':s['execution_id'],
            'case_id':'T00-14','procedure_digest':procedure('T00-14').procedure_digest,'stage_index':0,'route':'ENTRY_ONLY','interface':'preflight','plan_ref':plan})
        manifest(objects,sref,dref,[{'role':'entry_probe_set','ref':probe},{'role':'execution_plan','ref':plan}])
        row=validate_request_row(Store(objects),sref,s,'T00-14',procedure('T00-14'),0,{'route':'ENTRY_ONLY','interface':'preflight','authority_mode':'ENTRY_PROBE_AUTHORITY','entry_probe_ref':probe})
        self.assertEqual(row['authority_ref'],probe)

    def test_fence_plan_requires_actual_matching_original_fence(self):
        objects={};s=suite('T00-07');sref=add(objects,'lab_acceptance_suite',{k:v for k,v in s.items() if k!='role'});dref=add(objects,'lab_campaign_descriptor',descriptor(s));proc=procedure('T00-07');rule=authority_rule('T00-07',1)
        from aifilm_p00.plans import make_plan
        semantic={'schema_version':1,'run_id':'original-run','work_item':'W','execution_class':'LAB','host_id':s['host_id'],'owner_sid':s['owner_sid'],
          'target':{'name':'AI-Film','base_path':r'D:\AI-Film','registration_id':None,'user':'film'},'purpose':'CREATE','contract_digest':CONTRACT_DIGEST,
          'build_digest':s['build_digest'],'test_set_digest':s['test_set_digest'],'profile':{},'before':{},'expected_after':{},
          'budgets':[{'volume_id':'VOL','roles':['OS'],'allocations':{'x':1}}],'payload_digest':None,'source_class':'CLEAN_P00','refs':{},'final_state':'RUNNING'}
        original=make_plan(semantic,'2026-09-22T00:00:00Z');oref=add(objects,'original_plan',{'schema_version':1,'withdrawn':False,'plan':original})
        rec=dict(semantic);rec['run_id']='recovery-run';rec['purpose']='RECONCILIATION_ONLY';rec['refs']={'original_plan':oref};rec['target']=dict(semantic['target']);rec['expected_after']={}
        rplan=make_plan(rec,'2026-09-22T00:10:00Z');rref=add(objects,'execution_plan',{'schema_version':1,'withdrawn':False,'plan':rplan})
        slot={'schema_version':1,'withdrawn':False,'source_kind':'LAB','host_id':s['host_id'],'owner_sid':s['owner_sid'],'build_digest':s['build_digest'],
            'test_set_digest':s['test_set_digest'],'contract_digest':CONTRACT_DIGEST,'execution_id':s['execution_id'],'case_id':'T00-07','procedure_digest':proc.procedure_digest,
            'stage_index':1,'route':'RECONCILIATION_ONLY','interface':'verify','authority_mode':'FENCE_BOUND_RECONCILIATION','campaign_descriptor_ref':dref,
            'plan_template_ref':None,'native_binding_template_ref':None,'producer_dependencies':rule['producer_dependencies'],'late_fields':rule['late_fields'],
            'derived_object_roles':rule['derived_object_roles'],'maximum_approval_seconds':3600,'destination_locator_allowlist':[],'reconciliation_plan_refs':[rref],'semantic_selectors':{}}
        slotref=add(objects,'lab_stage_derivation_slot',slot);manifest(objects,sref,dref,[{'role':'lab_stage_derivation_slot','ref':slotref},{'role':'execution_plan','ref':rref}])
        fence={'run_id':original['semantic']['run_id'],'host_id':s['host_id'],'owner_sid':s['owner_sid'],'plan_digest':original['plan_digest']}
        out=resolve_reconciliation_plan(Store(objects),sref,s,'T00-07',1,proc,slotref,fence);self.assertEqual(out['plan_ref'],rref)
        bad=dict(fence);bad['plan_digest']='f'*64
        with self.assertRaises(P00Error):resolve_reconciliation_plan(Store(objects),sref,s,'T00-07',1,proc,slotref,bad)

class FakePort:
    def __init__(self,current,event=None,fail_append_once=False): self.current=current;self.event=event;self.writes=0;self.appends=0;self.fail_append_once=fail_append_once
    def read_policy(self): return self.current
    def write_policy(self,raw): self.current=raw;self.writes+=1
    def event_status(self,event):
        if self.event is None:return 'ABSENT'
        return 'EXACT' if self.event==event else 'CONFLICT'
    def append_event(self,event):
        self.appends+=1
        if self.fail_append_once:
            self.fail_append_once=False;raise OSError('journal append failure')
        self.event=json.loads(json.dumps(event))


class RestoreMaterializationTests(unittest.TestCase):
    def setUp(self):
        self.objects={};self.s=suite('T00-09');self.sref=add(self.objects,'lab_acceptance_suite',{k:v for k,v in self.s.items() if k!='role'});self.dref=add(self.objects,'lab_campaign_descriptor',descriptor(self.s));self.proc=procedure('T00-09');self.rule=authority_rule('T00-09',1)
        cp='a'*64;env='b'*64;src_path=r'E:\backup\checkpoint.tar';dst_path=r'C:\staging\checkpoint.tar'
        sem=binding('RESTORE_IMPORT','LAB');sem['host_id']=self.s['host_id'];sem['owner_sid']=self.s['owner_sid'];sem['build_digest']=self.s['build_digest'];sem['test_set_digest']=self.s['test_set_digest']
        sem['expected_checkpoint']={'$late':'semantic.expected_checkpoint'};sem['expected_envelope']={'$late':'semantic.expected_envelope'}
        sem['refs']={'registration':'1'*64,'design':'2'*64,'code':'3'*64,'lab_plan':'4'*64,'native_binding':'5'*64,
                     'checkpoint_payload':{'$late':'semantic.refs.checkpoint_payload'},'restore_envelope':{'$late':'semantic.refs.restore_envelope'}}
        pt={'schema_version':1,'withdrawn':False,'source_kind':'LAB','campaign_descriptor_ref':self.dref,'case_id':'T00-09','procedure_digest':self.proc.procedure_digest,'stage_index':1,'route':'RESTORE_IMPORT','interface':'apply','semantic_template':sem,'created_at':'2026-09-22T01:00:00Z'}
        self.ptref=add(self.objects,'lab_stage_plan_template',pt)
        slot={'schema_version':1,'withdrawn':False,'source_kind':'LAB','host_id':self.s['host_id'],'owner_sid':self.s['owner_sid'],'build_digest':self.s['build_digest'],'test_set_digest':self.s['test_set_digest'],'contract_digest':CONTRACT_DIGEST,'execution_id':self.s['execution_id'],'case_id':'T00-09','procedure_digest':self.proc.procedure_digest,'stage_index':1,'route':'RESTORE_IMPORT','interface':'apply','authority_mode':'STAGE_DERIVED','campaign_descriptor_ref':self.dref,'plan_template_ref':self.ptref,'native_binding_template_ref':None,'producer_dependencies':self.rule['producer_dependencies'],'late_fields':self.rule['late_fields'],'derived_object_roles':self.rule['derived_object_roles'],'maximum_approval_seconds':7200,
              'destination_locator_allowlist':[{'host_id':self.s['host_id'],'volume_id':'DSTVOL','canonical_path':dst_path,'purpose':'STAGING_IMPORT','max_bytes':4096,'offline_copy_required':True}],
              'reconciliation_plan_refs':[],'semantic_selectors':{'semantic.expected_checkpoint':{'producer_stage_index':0,'actual_path':['checkpoint_sha256']}}}
        self.slotref=add(self.objects,'lab_stage_derivation_slot',slot)
        manifest(self.objects,self.sref,self.dref,[{'role':'lab_stage_plan_template','ref':self.ptref},{'role':'lab_stage_derivation_slot','ref':self.slotref},{'role':'native_binding','ref':'5'*64}])
        hand={'schema_version':1,'withdrawn':False,'source_kind':'LAB','host_id':self.s['host_id'],'owner_sid':self.s['owner_sid'],'execution_id':self.s['execution_id'],'suite_ref':self.sref,'case_id':'T00-09','procedure_digest':self.proc.procedure_digest,'stage_index':0,'route':'RESTORE_EXPORT','plan_digest':'6'*64,'stage_ref':'7'*64,'state':'COMMITTED_TERMINAL','evidence_digest':'8'*64,
              'actual':{'checkpoint_sha256':cp,'checkpoint_path':src_path,'checkpoint_bytes':2048,'source_host_id':'source-host','source_volume_id':'SRCVOL','source_canonical_path':src_path},'timestamp_utc':'2026-09-22T02:00:00Z'}
        self.href=add(self.objects,'lab_stage_state_handoff',hand)
        loc=slot['destination_locator_allowlist'][0];copy={'schema_version':1,'withdrawn':False,'source_kind':'LAB','source_export_ref':self.href,'source_host_id':'source-host','source_volume_id':'SRCVOL','source_canonical_path':src_path,'source_checkpoint_sha256':cp,'source_checkpoint_bytes':2048,'destination':loc,'destination_sha256':cp,'destination_bytes':2048,'collector_ref':'9'*64,'raw_artifact_ref':'c'*64,'timestamp_utc':'2026-09-22T02:05:00Z'}
        add(self.objects,'checkpoint_copy_receipt',copy)
        scope={'host_id':self.s['host_id'],'checkpoint_digest':cp,'envelope_digest':env};actual={'checkpoint_digest':cp,'envelope_digest':env,'destination_host_id':self.s['host_id'],'no_auto_launch':True,'isolated_destination':True,'source_unchanged':True,'source_backup_of_record':True}
        collector=add(self.objects,'collector_release',{'withdrawn':False,'review_verdict':'PASS','build_digest':'d'*64})
        raw=add(self.objects,'measurement_artifact',{'measurement_actual_digest':digest(actual),'subject_digest':digest(scope),'withdrawn':False})
        measurement=add(self.objects,'measurement',{'fixture_only':False,'source_kind':'LAB','status':'OBSERVED','contract_digest':CONTRACT_DIGEST,'actual':actual,'host_id':self.s['host_id'],'subject_digest':digest(scope),'timestamp_utc':'2026-09-22T02:04:00Z','collector_ref':collector,'raw_artifact_ref':raw,'collector_digest':'d'*64})
        owner=add(self.objects,'resource_owner',{'withdrawn':False,'fixture_only':False,'owner_sid':self.s['owner_sid'],'receipt_roles':['restore_envelope'],'host_ids':[self.s['host_id']]})
        proof={'schema_version':1,'withdrawn':False,'fixture_only':False,'contract_digest':CONTRACT_DIGEST,'scope':scope,'issued_at':'2026-09-22T02:06:00Z','expires_at':'2026-09-22T23:00:00Z','authorizer_ref':owner,'owner_sid':self.s['owner_sid'],'measurements':[measurement],'claim':actual,
               'claim_map':{k:{'measurement_ref':measurement,'actual_key':k} for k in actual}}
        self.proofref=add(self.objects,'restore_envelope',proof);self.store=Store(self.objects);self.cp=cp;self.env=env;self.src_path=src_path;self.dst_path=dst_path

    def test_external_restore_uses_destination_locator_not_source_path(self):
        from aifilm_p00.codec import instant
        out=materialize_stage_objects(self.store,self.sref,self.s,'T00-09',1,self.proc,self.slotref,instant('2026-09-22T02:30:00Z'))
        self.assertEqual(out['plan']['semantic']['expected_checkpoint'],self.cp);self.assertEqual(out['plan']['semantic']['expected_envelope'],self.env)
        self.assertEqual(out['plan']['semantic']['refs']['restore_envelope'],self.proofref)
        payload=out['additions']['checkpoint_payload'][0];self.assertEqual(payload['path'],self.dst_path);self.assertNotEqual(payload['path'],self.src_path);self.assertEqual(payload['payload_digest'],self.cp)

    def test_copy_hash_drift_blocks_materialization(self):
        copyref=next(iter(self.store.pins['checkpoint_copy_receipt']));self.objects[('checkpoint_copy_receipt',copyref)]['destination_sha256']='e'*64
        from aifilm_p00.codec import instant
        with self.assertRaises(P00Error):materialize_stage_objects(Store(self.objects),self.sref,self.s,'T00-09',1,self.proc,self.slotref,instant('2026-09-22T02:30:00Z'))

    def test_restore_revocation_includes_checkpoint_payload_ref(self):
        from aifilm_p00.codec import instant
        out=materialize_stage_objects(self.store,self.sref,self.s,'T00-09',1,self.proc,self.slotref,instant('2026-09-22T02:30:00Z'))
        for role,objs in out['additions'].items():
            for obj in objs:add(self.objects,role,{k:v for k,v in obj.items() if k!='role'})
        st=Store(self.objects);st.generation=2
        refs=lineage_revocation_refs(st,out['lineage_ref'])
        payload_ref=out['lineage']['checkpoint_payload_ref']
        self.assertIsNotNone(payload_ref);self.assertIn(payload_ref,refs);self.assertIn(out['execution_plan_ref'],refs);self.assertIn(out['lineage']['approval_ref'],refs);self.assertIn(out['lineage_ref'],refs)

class PublicationTests(unittest.TestCase):
    def event(self): return {'kind':'AUTHORITY_GENERATION_PUBLISHED','publication_key':'1'*64}
    def test_parent_writes_once_and_commits_event(self):
        p=FakePort(b'parent');out=publish_candidate(p,b'parent',b'candidate',self.event())
        self.assertEqual(out['state'],'COMPLETE');self.assertEqual((p.writes,p.appends),(1,1));self.assertEqual(p.current,b'candidate')
    def test_written_candidate_appends_missing_event_without_rewrite(self):
        p=FakePort(b'candidate');publish_candidate(p,b'parent',b'candidate',self.event());self.assertEqual((p.writes,p.appends),(0,1))
    def test_exact_event_is_idempotent(self):
        e=self.event();p=FakePort(b'candidate',e);publish_candidate(p,b'parent',b'candidate',e);self.assertEqual((p.writes,p.appends),(0,0))
    def test_unknown_parent_blocks_without_write(self):
        p=FakePort(b'newer')
        with self.assertRaises(P00Error): publish_candidate(p,b'parent',b'candidate',self.event())
        self.assertEqual((p.writes,p.appends),(0,0))
    def test_conflicting_publication_event_blocks(self):
        p=FakePort(b'candidate',{'kind':'AUTHORITY_GENERATION_PUBLISHED','publication_key':'2'*64})
        with self.assertRaises(P00Error): publish_candidate(p,b'parent',b'candidate',self.event())
    def test_write_then_event_failure_recovers_without_rewrite(self):
        e=self.event();p=FakePort(b'parent',fail_append_once=True)
        with self.assertRaises(OSError): publish_candidate(p,b'parent',b'candidate',e)
        self.assertEqual(p.current,b'candidate');self.assertEqual(p.writes,1)
        publish_candidate(p,b'parent',b'candidate',e);self.assertEqual(p.writes,1);self.assertEqual(p.event,e)

class SourceBoundaryTests(unittest.TestCase):
    def test_accepted_primitives_remain_byte_identical(self):
        root=Path(__file__).resolve().parents[1]
        for rel,expected in ACCEPTED_PRIMITIVE_SHA256.items():
            self.assertEqual(hashlib.sha256((root/rel).read_bytes()).hexdigest(),expected,rel)

    def test_publish_derived_stage_guard_is_behavioral_and_releases_on_failure(self):
        from aifilm_p00.native import stage_authority
        from aifilm_p00.native import entry as entry_mod, coordination as coordination_mod, filesystem as filesystem_mod, trust as trust_mod
        parent_raw=canonical({'schema_version':1,'host_id':'host','operator_sids':['S-1-5-21-1'],
                              'role_pins':{},'blobs':{},'withdrawn_refs':[],'generation':1})
        class Store:
            policy_digest=sha256(parent_raw);generation=1;operators=frozenset({'S-1-5-21-1'});host_id='host';pins={}
            def get(self,role,ref):
                if role=='lab_acceptance_suite': return suite
                raise AssertionError((role,ref))
        suite={'suite':'exact'};store=Store();trace=[]
        class Guard:
            held=False
            def __init__(self,*a): pass
            def acquire(self): self.held=True;trace.append('acquire');return True
            def release(self): self.held=False;trace.append('release')
        class Journal:
            def __init__(self,*a): pass
            def load_fence(self): trace.append('fence');return None
            def admission_check(self): trace.append('admission')
        class Paths:
            def __init__(self,*a): pass
        class Port:
            def __init__(self,*a): pass
            def read_policy(self): trace.append('read');return parent_raw
            def lineage_events(self,*a): return []
        prepared={'candidate_policy_bytes':b'next','candidate_policy_digest':'1'*64,
                  'lineage_ref':'2'*64,'lineage':{},'generation_ref':'3'*64,'generation':{},
                  'execution_plan_ref':'4'*64}
        def prep(*a,**k): trace.append('derive');return prepared
        def event(*a,**k): return {'publication_key':'5'*64}
        def publish(*a,**k): trace.append('publish');return {'new_policy_digest':'1'*64}
        original_require=stage_authority.require
        def test_require(ok,code,reason):
            if reason=='WINDOWS_X64_REQUIRED': return None
            return original_require(ok,code,reason)
        patches=[mock.patch.object(stage_authority,'require',side_effect=test_require),mock.patch.object(entry_mod,'_entry',return_value=(object(),store,{},None,None)),
                 mock.patch.object(coordination_mod,'NativeGuard',Guard),mock.patch.object(coordination_mod,'NativeJournal',Journal),
                 mock.patch.object(filesystem_mod,'WindowsPaths',Paths),mock.patch.object(stage_authority,'JournalPolicyPort',Port),
                 mock.patch.object(trust_mod,'NativeStore',side_effect=lambda *a,**k:store),
                 mock.patch.object(stage_authority,'resolve_current_lineage',return_value=None),
                 mock.patch.object(stage_authority,'prepare_stage_generation',side_effect=prep),
                 mock.patch.object(stage_authority,'publication_event',side_effect=event),
                 mock.patch.object(stage_authority,'publish_candidate',side_effect=publish)]
        with patches[0],patches[1],patches[2],patches[3],patches[4],patches[5],patches[6],patches[7],patches[8],patches[9],patches[10]:
            out=stage_authority.publish_derived_stage('.',store,'6'*64,suite,'T00-09',1,object(),'7'*64)
        self.assertEqual(out['plan_ref'],'4'*64)
        self.assertEqual(trace,['acquire','fence','admission','read','derive','publish','release'])
        trace.clear()
        patches[-1]=mock.patch.object(stage_authority,'publish_candidate',side_effect=RuntimeError('publish-fail'))
        with patches[0],patches[1],patches[2],patches[3],patches[4],patches[5],patches[6],patches[7],patches[8],patches[9],patches[10]:
            with self.assertRaisesRegex(RuntimeError,'publish-fail'):
                stage_authority.publish_derived_stage('.',store,'6'*64,suite,'T00-09',1,object(),'7'*64)
        self.assertEqual(trace[-1],'release')
        self.assertFalse(trace.count('acquire')!=1 or trace.count('release')!=1)

    def test_reused_lineage_rechecks_parent_after_guard_acquire(self):
        from aifilm_p00.native import stage_authority
        from aifilm_p00.native import entry as entry_mod, coordination as coordination_mod, filesystem as filesystem_mod, trust as trust_mod
        parent_raw=canonical({'schema_version':1,'host_id':'host','operator_sids':['S-1-5-21-1'],
                              'role_pins':{},'blobs':{},'withdrawn_refs':[],'generation':1})
        drift_raw=canonical({'schema_version':1,'host_id':'host','operator_sids':['S-1-5-21-1'],
                             'role_pins':{},'blobs':{},'withdrawn_refs':[],'generation':2})
        class Store:
            operators=frozenset({'S-1-5-21-1'});host_id='host';pins={}
            def __init__(self,raw):
                self.policy_digest=sha256(raw);self.generation=1 if raw==parent_raw else 2
            def get(self,role,ref):
                if role=='lab_acceptance_suite': return suite
                raise AssertionError((role,ref))
        suite={'suite':'exact'};initial=Store(parent_raw);entry_store=Store(parent_raw);trace=[]
        class Guard:
            held=False
            def __init__(self,*a): pass
            def acquire(self): self.held=True;trace.append('acquire');return True
            def release(self): self.held=False;trace.append('release')
        class Journal:
            def __init__(self,*a): pass
            def load_fence(self): return None
            def admission_check(self): pass
        class Paths:
            def __init__(self,*a): pass
        class Port:
            def __init__(self,*a): pass
            def read_policy(self): return drift_raw
        original_require=stage_authority.require
        def test_require(ok,code,reason):
            if reason=='WINDOWS_X64_REQUIRED': return None
            return original_require(ok,code,reason)
        with mock.patch.object(stage_authority,'require',side_effect=test_require), \
             mock.patch.object(entry_mod,'_entry',return_value=(object(),entry_store,{},None,None)), \
             mock.patch.object(coordination_mod,'NativeGuard',Guard), \
             mock.patch.object(coordination_mod,'NativeJournal',Journal), \
             mock.patch.object(filesystem_mod,'WindowsPaths',Paths), \
             mock.patch.object(stage_authority,'JournalPolicyPort',Port), \
             mock.patch.object(trust_mod,'NativeStore',side_effect=lambda raw,*a,**k: Store(raw)), \
             mock.patch.object(stage_authority,'resolve_current_lineage',side_effect=AssertionError('must block before lineage lookup')):
            with self.assertRaisesRegex(P00Error,'AUTHORITY_PARENT_DRIFT'):
                stage_authority.publish_derived_stage('.',initial,'6'*64,suite,'T00-09',1,object(),'7'*64)
        self.assertEqual(trace,['acquire','release'])

    def test_publisher_releases_global_guard_before_existing_request_entry(self):
        from aifilm_p00.native import stage_authority, harness_controller
        pub=inspect.getsource(stage_authority.publish_derived_stage)
        tree=ast.parse(pub);fn=tree.body[0]
        calls=[]
        class V(ast.NodeVisitor):
            def visit_Call(self,node):
                name=None
                if isinstance(node.func,ast.Attribute): name=node.func.attr
                elif isinstance(node.func,ast.Name): name=node.func.id
                if name:calls.append((node.lineno,name))
                self.generic_visit(node)
        V().visit(fn)
        names=[n for _,n in calls]
        self.assertIn('acquire',names);self.assertIn('release',names)
        release_in_finally=any(isinstance(n,ast.Try) and any(isinstance(x,ast.Expr) and isinstance(x.value,ast.Call) and isinstance(x.value.func,ast.Attribute) and x.value.func.attr=='release' for x in n.finalbody) for n in ast.walk(fn))
        self.assertTrue(release_in_finally)
        harness=inspect.getsource(harness_controller.execute_stage)
        self.assertLess(harness.index('publish_derived_stage'),harness.index('prepare_execution'))
        self.assertNotIn('guard.acquire',harness[:harness.index('prepare_execution')])

class VersionIdentityTests(unittest.TestCase):
    def test_dev23_version_identity(self):
        root=Path(__file__).resolve().parents[1];meta=tomllib.loads((root/'pyproject.toml').read_text())
        self.assertEqual(meta['project']['version'],'0.1.0.dev23');self.assertEqual(__version__,'0.1.0.dev23')
    def test_contract_and_backend_constants_retained(self):
        self.assertEqual(CONTRACT_DIGEST,'f259656c48ed24c15bd48da2bb040950ed94d8edcf1473cf6456b96578c933ee');self.assertIs(NATIVE_BACKEND_AVAILABLE,False)

if __name__=='__main__': unittest.main(verbosity=2)
