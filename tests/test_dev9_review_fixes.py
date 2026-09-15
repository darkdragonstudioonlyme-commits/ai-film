"""Synthetic author regressions for CR-P00-002/003/004; no native execution."""
from copy import deepcopy
from dataclasses import replace
from datetime import timedelta
from unittest.mock import patch
import unittest

from helpers import authority_case, NOW, B
from test_session_integration import Driver, Guard, Storage
from test_dev4_recovery import RecoverDriver
from test_dev8_lifecycle import reconciliation_request
from aifilm_p00.admission import Coordinator
from aifilm_p00.authority import authorize
from aifilm_p00.codec import digest
from aifilm_p00.errors import P00Error
from aifilm_p00.session import SessionRunner
from aifilm_p00.native.lifecycle import wait_observation


class WaitPersistenceTests(unittest.TestCase):
    def reject(self, code, fn, *args):
        with self.assertRaises(P00Error) as caught:
            fn(*args)
        self.assertEqual(int(caught.exception.code), code)
        return caught.exception.reason

    def test_session_persists_safe_pending_reboot_cause(self):
        interface,plan,ctx,store=authority_case('ENGINE')
        d=Driver(plan,ctx,store);st=Storage();runner=SessionRunner(d,Coordinator(Guard(),st))
        d.run_result={'exit':20,'state':'AWAITING_REBOOT','wait_reason':'PENDING_REBOOT_OBSERVED',
            'pending_reboot':{'cbs_reboot_pending':True,'windows_update_reboot_required':False},
            'raw_output':'must-not-be-persisted'}
        out=runner.execute(interface,plan);fence=st.load_fence();wait=fence['wait_observation']
        self.assertEqual(out['state'],'AWAITING_REBOOT')
        self.assertEqual(wait['reason'],'PENDING_REBOOT_OBSERVED')
        self.assertEqual(wait['pending_reboot'],{'cbs_reboot_pending':True,'windows_update_reboot_required':False})
        self.assertEqual(wait['result_digest'],digest(d.run_result));self.assertNotIn('raw_output',wait)

    def admitted(self):
        interface,plan,ctx,store=authority_case('HOST_RESTART')
        auth=authorize(interface,plan,ctx,store);st=Storage();c=Coordinator(Guard(),st);c.acquire(auth)
        c.intent('AWAIT_OWNER_RESTART',[],{'host_boot':'boot-a','controller_pid':1,
            'controller_start':'1','build_digest':B,'step_id':'step-0'})
        valid=wait_observation('AWAIT_OWNER_RESTART',{'state':'AWAITING_REBOOT','exit':20},'INTENT')
        return c,st,valid

    def test_wait_context_rejects_unknown_sensitive_shape(self):
        c,st,obs=self.admitted();obs['raw_stdout']='secret'
        self.assertEqual(self.reject(10,c.awaiting,'AWAITING_REBOOT',obs),'WAIT_OBSERVATION_SCHEMA')
        self.assertEqual(st.load_fence()['state'],'INTENT');c.close()

    def test_wait_context_rejects_oversized_payload_before_persistence(self):
        c,st,obs=self.admitted();obs['reason']='X'*3000
        self.assertEqual(self.reject(22,c.awaiting,'AWAITING_REBOOT',obs),'WAIT_OBSERVATION_CAP')
        self.assertEqual(st.load_fence()['state'],'INTENT');c.close()

    def test_wait_context_binds_previous_fence_state(self):
        c,st,obs=self.admitted();obs['previous_state']='RUNNING'
        self.assertEqual(self.reject(15,c.awaiting,'AWAITING_REBOOT',obs),'WAIT_PREVIOUS_STATE_DRIFT')
        self.assertEqual(st.load_fence()['state'],'INTENT');c.close()


class OwnerRelabelReauthorizationTests(unittest.TestCase):
    def setup_wait(self):
        interface,old,ctx,store=authority_case('CREATE')
        class WaitDriver(RecoverDriver):
            def run(self,p,i,f,c):
                if i==1:
                    self.calls.append(('run',i));return {'state':'AWAITING_USER_INIT','exit':20}
                return super().run(p,i,f,c)
        d=WaitDriver(old,ctx,store);st=Storage();runner=SessionRunner(d,Coordinator(Guard(),st))
        self.assertEqual(runner.execute(interface,old)['state'],'AWAITING_USER_INIT')
        opening=deepcopy(st.load_fence());request,request_store=reconciliation_request(old,opening,store)
        d.store=request_store
        return runner,d,st,request,opening

    def reject(self, code, fn, *args):
        with self.assertRaises(P00Error) as caught:fn(*args)
        self.assertEqual(int(caught.exception.code),code);return caught.exception.reason

    def test_owner_wait_relabel_reauthorizes_after_observation(self):
        runner,d,st,request,opening=self.setup_wait()
        d.reconcile=lambda *a,**k:(_ for _ in ()).throw(P00Error(20,'AWAITING_OWNER_VERIFICATION'))
        out=runner.reconcile(request);fence=st.load_fence();wait=fence['wait_observation']
        self.assertEqual(out['state'],'AWAITING_OWNER_VERIFICATION')
        self.assertEqual(wait['reason'],'POSTCONDITION_OWNER_EVIDENCE_PENDING')
        self.assertEqual(wait['previous_state'],'AWAITING_USER_INIT')
        self.assertEqual(wait['previous_wait_digest'],digest(opening['wait_observation']))

    def test_expired_authority_after_observation_blocks_relabel(self):
        runner,d,st,request,opening=self.setup_wait()
        def late(*a,**k):
            d.ctx=replace(d.ctx,now=NOW+timedelta(days=2));raise P00Error(20,'AWAITING_OWNER_VERIFICATION')
        d.reconcile=late
        self.assertEqual(self.reject(12,runner.reconcile,request),'APPROVAL_EXPIRED')
        self.assertEqual(st.load_fence(),opening)

    def test_generation_rollback_after_observation_blocks_relabel(self):
        runner,d,st,request,opening=self.setup_wait();d.generation=3
        def late(*a,**k):
            d.generation=2;raise P00Error(20,'AWAITING_OWNER_VERIFICATION')
        d.reconcile=late
        self.assertEqual(self.reject(15,runner.reconcile,request),'AUTHORITY_ROLLBACK')
        self.assertEqual(st.load_fence(),opening)

    def test_actor_drift_after_observation_blocks_relabel(self):
        runner,d,st,request,opening=self.setup_wait()
        def late(*a,**k):
            d.ctx=replace(d.ctx,execution_sid='S-1-5-18');raise P00Error(20,'AWAITING_OWNER_VERIFICATION')
        d.reconcile=late
        self.assertEqual(self.reject(12,runner.reconcile,request),'WRONG_HOST_OR_PRINCIPAL')
        self.assertEqual(st.load_fence(),opening)

    def test_recovery_request_drift_after_observation_blocks_relabel(self):
        runner,d,st,request,opening=self.setup_wait()
        d.reconcile=lambda *a,**k:(_ for _ in ()).throw(P00Error(20,'AWAITING_OWNER_VERIFICATION'))
        stable={'mode':'RECONCILE','ref':None,'scope':{}}
        changed={'mode':'DIAGNOSE','ref':None,'scope':{}}
        with patch('aifilm_p00.recovery.recovery_intent',side_effect=[stable,stable,changed]):
            self.assertEqual(self.reject(16,runner.reconcile,request),'RECOVERY_REQUEST_DRIFT')
        self.assertEqual(st.load_fence(),opening)


if __name__=='__main__':unittest.main()
