"""Explicit synthetic C0 and native factory wiring tests; no OS or network IO."""
from copy import deepcopy
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import patch
import unittest

from helpers import authority_case, SID, B, T, CP, NOW, GIB, host, host_resources, canonical, digest, sha256
from test_session_integration import Driver, Guard, Storage
from test_dev4_recovery import extend
from aifilm_p00.session import SessionRunner, Refresh
from aifilm_p00.admission import Coordinator
from aifilm_p00.observation_binding import C0Capture, C0CaptureRunner, compose, load_capture, OBSERVED_KEYS
from aifilm_p00.native.request_entry import execute,requested_plan
from aifilm_p00.errors import P00Error


def actuals(plan):
    s=plan['semantic']
    mat={'schema_version':1,'host':{'host_id':s['host_id'],'build':'22631','ubr':1,'edition':'Pro','release':'23H2','architecture':'x64'},
         'execution_sid':SID,'runtime':{'status':'PACKAGED_ABSENT','version':None,'kernel':None,'package_identity':None},
         'features':[{'name':'VirtualMachinePlatform','state':'Disabled'}],
         'distros':{'default':None,'rows':[]},'wslconfig':{'status':'ABSENT','sha256':None}}
    return {'material':mat,'resources':host_resources(),'host':{**host(),'boot_utc':NOW.isoformat()},
            'free_bytes':{'volume1':100*GIB},'profile_verified':True,'collection_errors':{}}


class C0Driver(Driver):
    def reserve_c0_capture(self,p,c):self.calls.append(('reserve_c0',None))
    def capture_c0(self,p,c):
        self.calls.append(('capture_c0',None))
        out=self.refresh(p,coordinator=c)
        return replace(out,observed=actuals(p),collection_kind='WINDOWS_NATIVE_METADATA')


def setup():
    _,p,ctx,store=authority_case('PASSIVE')
    d=C0Driver(p,ctx,store);g=Guard();st=Storage();session=SessionRunner(d,Coordinator(g,st))
    return C0CaptureRunner(session),d,g,st,p


def captured():
    r,d,g,st,p=setup();out=r.execute(p)
    cap=load_capture(st.read_events(),out['capture_digest'],host_id=p['semantic']['host_id'],owner_sid=SID,build_digest=B)
    _,desired,_,_=authority_case('ENGINE')
    b={k:deepcopy(v) for k,v in desired['semantic'].items() if k not in OBSERVED_KEYS|{'operations'}}
    selection={'schema_version':1,'withdrawn':False,'binding':b,
               'scope':{'host_id':cap.body['host_id'],'owner_sid':SID,'capture_digest':cap.digest}}
    return cap,selection,st


class C0BindingTests(unittest.TestCase):
    def reject(self,code,fn,*args,**kw):
        with self.assertRaises(P00Error) as e:fn(*args,**kw)
        self.assertEqual(e.exception.code,code)
    def test_inventory_uses_one_admission(self):
        r,d,g,st,p=setup();out=r.execute(p)
        self.assertEqual(g.acquisitions,1);self.assertEqual(g.releases,1)
        self.assertEqual(len([c for c in d.calls if c[0]=='capture_c0']),2)
        self.assertFalse(any(c[0]=='run' for c in d.calls));self.assertIsNone(st.load_fence())
        self.assertFalse(out['host_ready'])
    def test_observation_copies_actual_before_not_desired(self):
        cap,sel,st=captured();out=compose(sel,cap,NOW)
        self.assertEqual(out['state'],'PLAN_PROPOSED');p=out['plan']
        self.assertEqual(p['semantic']['before'],cap.body['observed']['material'])
        self.assertEqual(p['semantic']['expected_after'],sel['binding']['expected_after'])
        self.assertNotIn('approval_ref',p);self.assertTrue(out['requires_exact_approval'])
    def test_caller_cannot_supply_observed_fields(self):
        cap,s,_=captured();s['binding']['before']={'fake':True}
        self.reject(10,compose,s,cap,NOW)
    def test_no_registration_created_for_engine(self):
        cap,s,_=captured();p=compose(s,cap,NOW)['plan']
        self.assertTrue(all(v is None for v in p['semantic']['target'].values()))
    def test_other_capture_selection_blocked(self):
        cap,s,_=captured();s['scope']['capture_digest']=CP
        self.reject(12,compose,s,cap,NOW)
    def test_changed_body_not_trusted(self):
        cap,s,_=captured();cap.body['profile']={}
        self.reject(15,compose,s,cap,NOW)
    def test_partial_actuals_non_applicable_not_fake(self):
        cap,s,_=captured();b=deepcopy(cap.body);b['observed']['collection_errors']={'runtime':'UNAVAILABLE'}
        cap=C0Capture(b,digest(b));s['scope']['capture_digest']=cap.digest
        out=compose(s,cap,NOW);self.assertEqual(out['state'],'NON_APPLICABLE');self.assertIsNone(out['plan'])
    def test_profile_not_verified_blocks(self):
        cap,s,_=captured();b=deepcopy(cap.body);b['observed']['profile_verified']=False
        cap=C0Capture(b,digest(b));s['scope']['capture_digest']=cap.digest
        self.assertIn('C0_PROFILE_NOT_OBSERVED',compose(s,cap,NOW)['blockers'])
    def test_capture_stale_non_applicable(self):
        cap,s,_=captured();self.assertEqual(compose(s,cap,NOW+timedelta(days=2))['state'],'NON_APPLICABLE')
    def test_capture_future_non_applicable(self):
        cap,s,_=captured();self.assertIn('C0_CAPTURE_FROM_FUTURE',compose(s,cap,NOW-timedelta(seconds=1))['blockers'])
    def test_capture_material_unstable_not_used(self):
        cap,s,_=captured();b=deepcopy(cap.body);b['stable_material']=False
        cap=C0Capture(b,digest(b));s['scope']['capture_digest']=cap.digest
        self.assertIn('C0_MATERIAL_NOT_STABLE',compose(s,cap,NOW)['blockers'])
    def test_zero_free_space_does_not_create_fake_binding(self):
        cap,s,_=captured();b=deepcopy(cap.body);b['observed']['free_bytes']['volume1']=0
        cap=C0Capture(b,digest(b));s['scope']['capture_digest']=cap.digest
        self.assertEqual(compose(s,cap,NOW)['state'],'NON_APPLICABLE')
    def test_no_arbitrary_snapshot_load(self):
        cap,s,st=captured();self.reject(15,load_capture,st.read_events(),CP,host_id=cap.body['host_id'],owner_sid=SID,build_digest=B)
    def test_wrong_host_snapshot_blocked(self):
        cap,s,st=captured();self.reject(16,load_capture,st.read_events(),cap.digest,host_id='other',owner_sid=SID,build_digest=B)
    def test_capture_requires_its_intent(self):
        cap,s,st=captured();rows=[r for r in st.read_events() if r['event']['kind']!='C0_CAPTURE_INTENT']
        self.reject(15,load_capture,rows,cap.digest,host_id=cap.body['host_id'],owner_sid=SID,build_digest=B)
    def test_unresolved_read_during_capture_not_committed(self):
        r,d,g,st,p=setup();orig=d.capture_c0
        def collect(p,c):
            st.append_event({'kind':'READ_PROBE_INTENT','read_id':'read-'+str(len(st.read_events())),'plan_digest':p['plan_digest']})
            return orig(p,c)
        d.capture_c0=collect;self.reject(21,r.execute,p)
        self.assertFalse(any(e['event']['kind']=='C0_CAPTURE_COMMITTED' for e in st.read_events()))
    def test_expired_permission_prevents_capture_commit(self):
        r,d,g,st,p=setup();orig=d.capture_c0
        def collect(p,c):
            out=orig(p,c);d.ctx=replace(d.ctx,now=NOW+timedelta(days=2));return out
        d.capture_c0=collect;self.reject(12,r.execute,p)
    def test_material_changes_record_unstable_inventory(self):
        r,d,g,st,p=setup();orig=d.capture_c0;calls=[]
        def collect(p,c):
            out=orig(p,c);calls.append(1)
            if len(calls)==2:out.observed['material']['wslconfig']={'new':True}
            return out
        d.capture_c0=collect;self.assertFalse(r.execute(p)['stable_material'])
    def test_production_source_cannot_use_workspace_observation(self):
        r,d,g,st,p=setup();d.source_kind='SITE';orig=d.capture_c0
        d.capture_c0=lambda p,c:replace(orig(p,c),collection_kind='WORKSPACE_TEST')
        self.reject(15,r.execute,p)
    def test_capture_does_not_publish_raw_native_data(self):
        r,d,g,st,p=setup();out=r.execute(p)
        self.assertNotIn('owner_sid',out);self.assertNotIn('material',out)
    def test_active_discovery_not_run_by_capture_entry(self):
        r,d,g,st,_=setup();_,p,_,_=authority_case('DISCOVERY')
        self.reject(12,r.execute,p);self.assertEqual(g.acquisitions,0)


class FactoryDispatchTests(unittest.TestCase):
    def run_native_dispatch(self,interface,purpose):
        _,p,_,store=authority_case(purpose)
        store,ref=extend(store,'execution_plan',{'schema_version':1,'withdrawn':False,'plan':p})
        calls=[]
        session=SimpleNamespace(execute=lambda i,p:calls.append(('execute',i,p['semantic']['purpose'])) or {'exit':0},
                                reconcile=lambda p:calls.append(('reconcile',p['semantic']['purpose'])) or {'exit':0})
        with patch('aifilm_p00.native.request_entry._entry',return_value=(None,store,None,None,None)),\
             patch('aifilm_p00.native.request_entry.native_session',return_value=session) as factory:
            result=execute('/workspace/synthetic',interface,ref)
            factory.assert_called_once()
        return calls,result
    def test_apply_dispatches_concrete_factory_symbol(self):
        calls,_=self.run_native_dispatch('apply','CREATE');self.assertEqual(calls,[('execute','apply','CREATE')])
    def test_verify_dispatches_concrete_factory_symbol(self):
        calls,_=self.run_native_dispatch('verify','SITE_VERIFY');self.assertEqual(calls,[('execute','verify','SITE_VERIFY')])
    def test_support_dispatches_concrete_factory_symbol(self):
        calls,_=self.run_native_dispatch('support-bundle','SUPPORT_BUNDLE');self.assertEqual(calls,[('execute','support-bundle','SUPPORT_BUNDLE')])
    def test_recovery_dispatches_original_request_entry(self):
        calls,_=self.run_native_dispatch('verify','RECONCILIATION_ONLY');self.assertEqual(calls,[('reconcile','RECONCILIATION_ONLY')])
    def test_execution_document_cannot_change_interface(self):
        _,p,_,store=authority_case('CREATE');store,ref=extend(store,'execution_plan',{'schema_version':1,'withdrawn':False,'plan':p})
        with self.assertRaises(P00Error):requested_plan(store,ref,'verify')
    def test_execution_document_not_self_pinning(self):
        _,p,_,store=authority_case('CREATE')
        with self.assertRaises(P00Error):requested_plan(store,CP,'apply')
    def test_withdrawn_document_not_run(self):
        _,p,_,store=authority_case('CREATE');store,ref=extend(store,'execution_plan',{'schema_version':1,'withdrawn':True,'plan':p})
        with self.assertRaises(P00Error):requested_plan(store,ref,'apply')

if __name__=='__main__':unittest.main()
