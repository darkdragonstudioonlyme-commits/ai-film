"""Synthetic author tests for restart/OOBE/resume control flow; no native execution."""
from copy import deepcopy
from dataclasses import replace
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from helpers import authority_case, SID
from test_session_integration import Guard, Storage
from test_dev4_recovery import RecoverDriver, extend
from aifilm_p00.admission import Coordinator
from aifilm_p00.errors import P00Error
from aifilm_p00.plans import make_plan
from aifilm_p00.session import SessionRunner
from aifilm_p00.native.lifecycle import (
    classify_c3_process_result, reboot_resume_boundary, owner_wait_can_relabel,
)
from aifilm_p00.native.session_driver import NativeDriver


class LifecyclePolicyTests(unittest.TestCase):
    def reject(self, code, fn, *args):
        with self.assertRaises(P00Error) as caught:
            fn(*args)
        self.assertEqual(int(caught.exception.code), code)
        return caught.exception.reason

    def test_exit_zero_with_observed_pending_reboot_becomes_operator_wait(self):
        result=classify_c3_process_result('ENABLE_PREREQUISITES',
            {'exit':0,'state':'NATIVE_PROCESS_COMPLETED'}, {'cbs':True,'wu':False})
        self.assertEqual(result['exit'],20);self.assertEqual(result['state'],'AWAITING_REBOOT')
        self.assertEqual(result['wait_reason'],'PENDING_REBOOT_OBSERVED')

    def test_no_pending_reboot_keeps_process_result(self):
        original={'exit':0,'state':'NATIVE_PROCESS_COMPLETED'}
        self.assertEqual(classify_c3_process_result('INSTALL_RUNTIME',original,
            {'cbs':False,'wu':False}),original)

    def test_reboot_boundary_requires_new_boot_and_clear_pending_state(self):
        fence={'action':'INSTALL_RUNTIME','witness':{'host_boot':'boot-a','step_id':'step-1'}}
        self.assertEqual(self.reject(20,reboot_resume_boundary,fence,
            {'boot_utc':'boot-a'},{'cbs':False}),'REBOOT_NOT_OBSERVED')
        self.assertEqual(self.reject(20,reboot_resume_boundary,fence,
            {'boot_utc':'boot-b'},{'cbs':True}),'REBOOT_STILL_PENDING')
        out=reboot_resume_boundary(fence,{'boot_utc':'boot-b'},{'cbs':False,'wu':False})
        self.assertEqual(out['before_boot'],'boot-a');self.assertEqual(out['after_boot'],'boot-b')

    def test_only_operator_wait_fence_can_relabel_owner_verification(self):
        self.assertTrue(owner_wait_can_relabel({'state':'AWAITING_REBOOT'},'AWAITING_OWNER_VERIFICATION'))
        self.assertFalse(owner_wait_can_relabel({'state':'UNCERTAIN'},'AWAITING_OWNER_VERIFICATION'))
        self.assertFalse(owner_wait_can_relabel({'state':'AWAITING_REBOOT'},'PROOF_EXPIRED'))


class NativeRunLifecycleTests(unittest.TestCase):
    def setup_driver(self, pending):
        d=NativeDriver.__new__(NativeDriver)
        d.paths=object();d.supervisor=object();d.environment={};d.binding={}
        d.api=SimpleNamespace(system_directory=lambda:r'C:\\Windows\\System32')
        d.system=SimpleNamespace(pending_reboot=lambda:deepcopy(pending))
        return d

    def test_native_driver_checks_pending_reboot_after_successful_c3_process(self):
        _,plan,_,store=authority_case('ENGINE')
        d=self.setup_driver({'cbs':True,'wu':False})
        actuator=SimpleNamespace(execute=lambda *a,**k:{'exit':0,'state':'NATIVE_PROCESS_COMPLETED'})
        with patch('aifilm_p00.native.session_driver.NativeActuator',return_value=actuator):
            result=d.run(plan,0,SimpleNamespace(store=store),SimpleNamespace())
        self.assertEqual(result['state'],'AWAITING_REBOOT')

    def test_native_driver_does_not_hide_existing_3010_wait(self):
        _,plan,_,store=authority_case('ENGINE')
        d=self.setup_driver({'cbs':False})
        d.system.pending_reboot=lambda:(_ for _ in ()).throw(AssertionError('must not be called'))
        actuator=SimpleNamespace(execute=lambda *a,**k:{'exit':20,'state':'AWAITING_REBOOT'})
        with patch('aifilm_p00.native.session_driver.NativeActuator',return_value=actuator):
            result=d.run(plan,0,SimpleNamespace(store=store),SimpleNamespace())
        self.assertEqual(result['state'],'AWAITING_REBOOT')


class NativeReconcileBoundaryTests(unittest.TestCase):
    def run_case(self, state, wait=None):
        _,original,_,store=authority_case('ENGINE')
        d=NativeDriver.__new__(NativeDriver);d.binding={'request':True}
        d.system=SimpleNamespace(pending_reboot=lambda:{'cbs':False})
        captured={}
        def after(*args,**kwargs):
            captured['boundary']=kwargs.get('resume_boundary');return 'completion'
        d._after=after
        fence={'state':state,'action':'ENABLE_PREREQUISITES','native':None,
               'witness':{'host_boot':'boot-a','step_id':'step-0'}}
        if wait is not None:fence['wait_observation']=wait
        c=SimpleNamespace(fence=fence,storage=SimpleNamespace(read_events=lambda:[]))
        fresh=SimpleNamespace(observed={'material':{},'profile_verified':True,
                                       'host':{'boot_utc':'boot-b'}},store=store)
        with patch('aifilm_p00.native.session_driver._binding',return_value={'original':True}), \
             patch('aifilm_p00.native.read_recovery.reconcile_detached_reads',return_value=[]):
            result=d.reconcile(original,0,fresh,c)
        return result,captured

    def test_reconcile_waiting_reboot_binds_actual_boot_boundary(self):
        result,captured=self.run_case('AWAITING_REBOOT')
        self.assertEqual(result,'completion');self.assertEqual(captured['boundary']['after_boot'],'boot-b')

    def test_owner_wait_from_reboot_preserves_boot_boundary_requirement(self):
        _,captured=self.run_case('AWAITING_OWNER_VERIFICATION',
                                 {'previous_state':'AWAITING_REBOOT','reason':'POSTCONDITION_OWNER_EVIDENCE_PENDING'})
        self.assertEqual(captured['boundary']['before_boot'],'boot-a')

    def test_owner_wait_from_oobe_does_not_invent_reboot_requirement(self):
        _,original,_,store=authority_case('CREATE')
        d=NativeDriver.__new__(NativeDriver);d.binding={}
        d.system=SimpleNamespace(pending_reboot=lambda:(_ for _ in ()).throw(AssertionError('no reboot probe')))
        captured={};d._after=lambda *a,**kw:captured.setdefault('boundary',kw.get('resume_boundary')) or 'completion'
        c=SimpleNamespace(fence={'state':'AWAITING_OWNER_VERIFICATION','action':'AWAIT_OWNER_USER_INIT','native':None,
            'witness':{'host_boot':'boot-a','step_id':'step-1'}},storage=SimpleNamespace(read_events=lambda:[]))
        fresh=SimpleNamespace(observed={'material':{},'profile_verified':True,'host':{'boot_utc':'boot-a'}},store=store)
        with patch('aifilm_p00.native.session_driver._binding',return_value={}), \
             patch('aifilm_p00.native.read_recovery.reconcile_detached_reads',return_value=[]):
            d.reconcile(original,1,fresh,c)
        self.assertIsNone(captured['boundary'])


def reconciliation_request(old, opening, old_store):
    _,request0,_,request_store=authority_case('RECONCILIATION_ONLY')
    request_store=replace(request_store,blobs={**old_store.blobs,**request_store.blobs},
        pins={k:frozenset(set(old_store.pins.get(k,()))|set(request_store.pins.get(k,())))
              for k in set(old_store.pins)|set(request_store.pins)})
    request_store,ref=extend(request_store,'original_plan',{'plan':old})
    binding={k:deepcopy(v) for k,v in request0['semantic'].items() if k!='operations'}
    binding['refs']['original_plan']=ref;binding['target']=deepcopy(old['semantic']['target'])
    request=make_plan(binding,'2026-09-13T23:00:00Z')
    approval=deepcopy(request_store.get('approval',request0['approval_ref']));approval['plan_digest']=request['plan_digest']
    request_store,ref=extend(request_store,'approval',approval);request['approval_ref']=ref
    return request,request_store


class RecoveryOwnerWaitTests(unittest.TestCase):
    def test_missing_owner_postcheck_relabels_only_existing_wait_fence(self):
        interface,old,ctx,store=authority_case('CREATE')
        class WaitDriver(RecoverDriver):
            def run(self,p,i,f,c):
                if i==1:
                    self.calls.append(('run',i));return {'state':'AWAITING_USER_INIT','exit':20}
                return super().run(p,i,f,c)
        d=WaitDriver(old,ctx,store);g=Guard();st=Storage();runner=SessionRunner(d,Coordinator(g,st))
        out=runner.execute(interface,old);self.assertEqual(out['state'],'AWAITING_USER_INIT')
        opening=st.load_fence();request,request_store=reconciliation_request(old,opening,store);d.store=request_store
        d.reconcile=lambda *a,**k:(_ for _ in ()).throw(P00Error(20,'AWAITING_OWNER_VERIFICATION'))
        report=runner.reconcile(request)
        self.assertEqual(report['state'],'AWAITING_OWNER_VERIFICATION');self.assertTrue(report['fence_retained'])
        fence=st.load_fence();self.assertEqual(fence['state'],'AWAITING_OWNER_VERIFICATION')
        self.assertEqual(fence['wait_observation']['previous_state'],'AWAITING_USER_INIT')
        self.assertEqual(report['step_committed'],False)


if __name__=='__main__':unittest.main()
