"""Synthetic author tests for exact prior-stage/nested E00 provenance; no native execution."""
from copy import deepcopy
from dataclasses import replace
from datetime import datetime,timezone
from types import SimpleNamespace
import unittest

from helpers import authority_case, SID, B, CP
from aifilm_p00 import CONTRACT_DIGEST
from aifilm_p00.authority import PinnedStore
from aifilm_p00.codec import canonical,digest,sha256
from aifilm_p00.evidence_catalog import new_body
from aifilm_p00.errors import P00Error
from aifilm_p00.native.evidence_pipeline import (
    NativeCatalogProducer,_checkpoint_history_ref,_pre_c3_events,_prior_guest_from_events,
)

AT='2026-09-14T00:00:00Z'
G={'uid':1000,'gid':1000,'user':'film','home':'/home/film','os_id':'ubuntu','version_id':'24.04',
   'architecture':'x86_64','kernel':'6.6','kernel_boot_id':'boot','pid1_start_ticks':'1','pid1_comm':'systemd',
   'home_access_writable':True,'resources':{'logical_cpu':2,'mem_total_bytes':4,'mem_available_bytes':2,'fs_available_bytes':30},
   'wsl_conf_sha256':'b'*64}


def reject(test,code,fn,*args,**kwargs):
    with test.assertRaises(P00Error) as caught:fn(*args,**kwargs)
    test.assertEqual(int(caught.exception.code),code)
    return caught.exception.reason


def guest_event(plan,*,host='synthetic-host',target='SYNTHETIC-REG',at=AT,pd=None):
    pd=pd or plan['plan_digest']
    evidence={'kind':'NATIVE_OPERATION_AFTER','host_id':host,'source_kind':plan['semantic']['execution_class'],
        'plan_digest':pd,'timestamp_utc':at,'metadata':{'target':{'registration_id':target}},
        'details':{'actual_result':{'guest':{'inventory':{'actual':deepcopy(G)},'admin':{'actual':{'ready':True}}}}}}
    return {'event':{'kind':'OPERATION_AFTER_OBSERVED','plan_digest':pd,'step_id':'step-0',
                     'evidence':evidence,'evidence_digest':digest(evidence)}}


def pre_event(plan,*,host='synthetic-host',boundary=None,checked='2026-09-13T23:00:00Z',proof_ref=None,claim_digest=None):
    boundary=boundary or {'target':'SYNTHETIC-REG','state':'STOPPED','generation':1}
    scope={'host_id':host,'source_witness':digest(boundary)}
    return {'event':{'kind':'PRE_C3_PROOF_OBSERVED','plan_digest':plan['plan_digest'],'scope':scope,
        'proof_ref':proof_ref or ('c'*64),'checked_at':checked,'boundary':deepcopy(boundary),
        'claim_digest':claim_digest or ('d'*64)}}


def checkpoint_history(plan,*,checkpoint=CP,host='synthetic-host',target='SYNTHETIC-REG'):
    observation={'kind':'NATIVE_OPERATION_AFTER','host_id':host,'source_kind':plan['semantic']['execution_class'],
        'timestamp_utc':'2026-09-14T00:10:00Z','metadata':{'target':{'registration_id':target}},
        'details':{'checkpoint':{'sha256':checkpoint,'bytes':123}}}
    return {'history':{'entries':{'checkpoint':{'plan_digest':'e'*64,'evidence_digest':digest(observation),
                                                'observation':observation}}}}


class PriorGuestScopeTests(unittest.TestCase):
    def setup_plan(self):return authority_case('HOST_RESTART')[1]
    def test_exact_prior_guest_preserves_source_time_and_ref(self):
        plan=self.setup_plan();g,a,ref=_prior_guest_from_events([guest_event(plan)],plan,{},
            not_after=datetime(2026,9,14,1,0,tzinfo=timezone.utc))
        self.assertEqual(g['uid'],1000);self.assertTrue(a['ready']);self.assertEqual(ref['observed_at'],AT)
        self.assertTrue(ref['source_ref'].startswith('journal:'+plan['plan_digest']))
    def test_wrong_host_rejected(self):
        plan=self.setup_plan();self.assertEqual(reject(self,16,_prior_guest_from_events,[guest_event(plan,host='other')],plan,{}),'PRIOR_GUEST_SOURCE_SCOPE')
    def test_wrong_target_rejected(self):
        plan=self.setup_plan();self.assertEqual(reject(self,16,_prior_guest_from_events,[guest_event(plan,target='OTHER')],plan,{}),'PRIOR_GUEST_TARGET_SCOPE')
    def test_future_prior_observation_rejected(self):
        plan=self.setup_plan();self.assertEqual(reject(self,16,_prior_guest_from_events,[guest_event(plan,at='2026-09-15T00:00:00Z')],plan,{},
            datetime(2026,9,14,1,0,tzinfo=timezone.utc)),'PRIOR_GUEST_FUTURE')
    def test_unrelated_plan_is_not_adopted(self):
        plan=self.setup_plan();self.assertEqual(_prior_guest_from_events([guest_event(plan,pd='f'*64)],plan,{}),(None,None,None))


class PreC3EventTests(unittest.TestCase):
    def setup_plan(self):return authority_case('HOST_RESTART')[1]
    def test_exact_pre_c3_event_selected(self):
        plan=self.setup_plan();rows=_pre_c3_events([pre_event(plan)],plan,{})
        self.assertEqual(len(rows),1);self.assertEqual(rows[0]['scope']['host_id'],'synthetic-host')
    def test_wrong_host_rejected(self):
        plan=self.setup_plan();self.assertEqual(reject(self,16,_pre_c3_events,[pre_event(plan,host='other')],plan,{}),'PRE_C3_HOST_SCOPE')
    def test_tampered_boundary_rejected(self):
        plan=self.setup_plan();row=pre_event(plan);row['event']['boundary']['generation']=2
        self.assertEqual(reject(self,15,_pre_c3_events,[row],plan,{}),'PRE_C3_BOUNDARY_INTEGRITY')
    def test_conflicting_duplicate_rejected(self):
        plan=self.setup_plan();a=pre_event(plan);b=deepcopy(a);b['event']['claim_digest']='a'*64
        self.assertEqual(reject(self,15,_pre_c3_events,[a,b],plan,{}),'PRE_C3_EVENT_AMBIGUOUS')


class CheckpointHistoryTests(unittest.TestCase):
    def setup_plan(self):
        plan=authority_case('SITE_VERIFY')[1];plan['semantic']['expected_checkpoint']=CP;return plan
    def test_checkpoint_history_binds_exact_source(self):
        plan=self.setup_plan();ref=_checkpoint_history_ref(plan,checkpoint_history(plan),CP)
        self.assertEqual(ref['checkpoint_digest'],CP);self.assertIn('#checkpoint',ref['source_ref'])
    def test_tampered_checkpoint_observation_rejected(self):
        plan=self.setup_plan();result=checkpoint_history(plan);result['history']['entries']['checkpoint']['observation']['details']['checkpoint']['bytes']=999
        self.assertEqual(reject(self,15,_checkpoint_history_ref,plan,result,CP),'CHECKPOINT_HISTORY_INTEGRITY')
    def test_wrong_checkpoint_rejected(self):
        plan=self.setup_plan();self.assertEqual(reject(self,15,_checkpoint_history_ref,plan,checkpoint_history(plan,checkpoint='0'*64),CP),'CHECKPOINT_HISTORY_MISMATCH')
    def test_wrong_target_rejected(self):
        plan=self.setup_plan();self.assertEqual(reject(self,16,_checkpoint_history_ref,plan,checkpoint_history(plan,target='OTHER'),CP),'CHECKPOINT_HISTORY_TARGET')


class NestedFieldSourceTests(unittest.TestCase):
    def test_field_specific_source_is_preserved(self):
        values={'host':{'ram':1},'guest':{'ram':2},'measurement_context':{'x':1}}
        prior={'source_ref':'journal:prior','observed_at':'2026-09-13T23:00:00Z','source_kind':'SITE'}
        body=new_body('E00-05',values,at=AT,source_ref='journal:current',source_kind='SITE',field_sources={'guest':prior})
        self.assertEqual(body['fields']['guest']['source_ref'],'journal:prior')
        self.assertEqual(body['fields']['guest']['observed_at'],prior['observed_at'])
        self.assertEqual(body['fields']['host']['source_ref'],'journal:current')
    def test_unknown_field_source_rejected(self):
        values={'host':{},'measurement_context':{}}
        self.assertEqual(reject(self,15,new_body,'E00-05',values,at=AT,source_ref='current',source_kind='SITE',
            field_sources={'guest':{'source_ref':'x','observed_at':AT,'source_kind':'SITE'}}),'CATALOG_FIELD_SOURCE_UNKNOWN')
    def test_producer_prior_guest_fields_use_prior_source(self):
        producer=NativeCatalogProducer.__new__(NativeCatalogProducer)
        producer.prior_guest_ref={'source_ref':'journal:prior','observed_at':'2026-09-13T23:00:00Z','source_kind':'SITE'}
        sources=producer._field_sources('E00-07',{'guest_config':{'sha':'x'},'host_config':{}})
        self.assertEqual(sources['guest_config']['source_ref'],'journal:prior')
        self.assertNotIn('host_config',sources)


class AuthenticatedPreC3Tests(unittest.TestCase):
    def build(self,owner=SID):
        _,plan,_,base=authority_case('HOST_RESTART')
        boundary={'target':'SYNTHETIC-REG','state':'STOPPED','generation':1};scope={'host_id':'synthetic-host','source_witness':digest(boundary)}
        claim={'host_id':'synthetic-host','coverage_complete':True,'owner_authorized':True,'source_witness':scope['source_witness'],
            'sealed_at':'2026-09-13T22:00:00Z','windows_writers_safe':True,'rows':[{'resource_id':'SYNTHETIC-REG','authorized':True,
            'disposition':'DATA_BEARING_NONSENSITIVE','post_assertions':['content'],'post_actor':'owner','no_writes_since_boundary':True,
            'retention_bound':True,'checkpoint_digest':CP,'restore_checkpoint_digest':CP,'restore_pass':True,'independent_ready':True,
            'accessible_without_source_runtime':True,'restore_environment':'ISO-EXTERNAL','proof_completed_at':'2026-09-13T21:00:00Z'}]}
        pins={k:set(v) for k,v in base.pins.items()};blobs=dict(base.blobs)
        def put(role,obj):
            raw=canonical({'role':role,**obj});ref=sha256(raw);pins.setdefault(role,set()).add(ref);blobs[ref]=raw;return ref
        collector=put('collector_release',{'withdrawn':False,'review_verdict':'PASS','build_digest':B})
        rawref=put('measurement_artifact',{'measurement_actual_digest':digest(claim),'subject_digest':digest(scope),'withdrawn':False})
        measurement=put('measurement',{'fixture_only':False,'source_kind':'SITE','status':'OBSERVED','contract_digest':CONTRACT_DIGEST,
            'actual':claim,'host_id':'synthetic-host','subject_digest':digest(scope),'timestamp_utc':'2026-09-13T22:30:00Z',
            'collector_ref':collector,'collector_digest':B,'raw_artifact_ref':rawref})
        authorizer=put('resource_owner',{'withdrawn':False,'fixture_only':False,'owner_sid':owner,'receipt_roles':['protection'],'host_ids':['synthetic-host']})
        mapping={k:{'measurement_ref':measurement,'actual_key':k} for k in claim}
        proof=put('protection',{'schema_version':1,'withdrawn':False,'fixture_only':False,'contract_digest':CONTRACT_DIGEST,
            'scope':scope,'issued_at':'2026-09-13T23:00:00Z','expires_at':'2026-09-14T23:00:00Z','authorizer_ref':authorizer,
            'owner_sid':owner,'measurements':[measurement],'claim':claim,'claim_map':mapping})
        store=PinnedStore({k:frozenset(v) for k,v in pins.items()},blobs,'SYNTHETIC')
        event=pre_event(plan,boundary=boundary,proof_ref=proof,claim_digest=digest(claim))
        producer=NativeCatalogProducer.__new__(NativeCatalogProducer);producer.events=[event];producer.plan=plan;producer.result={}
        producer.f=SimpleNamespace(store=store);producer.s=plan['semantic']
        return producer
    def test_authenticated_pre_c3_proof_yields_target_checkpoint_ref(self):
        producer=self.build();rows=producer._validated_pre_c3()
        self.assertEqual(rows[0]['ref']['target_checkpoint_digest'],CP)
        self.assertEqual(rows[0]['proof']['owner_sid'],SID)
    def test_wrong_owner_receipt_rejected_by_consumer(self):
        producer=self.build(owner='S-1-5-21-999')
        self.assertEqual(reject(self,12,producer._validated_pre_c3),'PRE_C3_OWNER_SCOPE')


if __name__=='__main__':unittest.main()
