"""Synthetic workspace integration; never registration, native proof or qualification."""
from copy import deepcopy
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace
import unittest

from helpers import *
from test_session_integration import Driver, Guard, Storage
from aifilm_p00.admission import Coordinator
from aifilm_p00.session import SessionRunner
from aifilm_p00.recovery import PauseObservation, recovery_intent
from aifilm_p00.resume import completed_steps
from aifilm_p00.native.read_recovery import pending_reads, reconcile_detached_reads
from aifilm_p00.native.recovery_driver import pause_observation, diagnose
from aifilm_p00.errors import P00Error


def extend(store, role, document):
    raw = canonical({'role': role, **document}); ref = sha256(raw)
    pins = {k:set(v) for k,v in store.pins.items()}; pins.setdefault(role,set()).add(ref)
    return replace(store, pins={k:frozenset(v) for k,v in pins.items()},
                   blobs={**store.blobs,ref:raw}),ref


class RecoverDriver(Driver):
    def __init__(self,*a):
        super().__init__(*a); self.pause_error=None; self.diag={'secret':'synthetic-private-only'}
    def diagnose(self,p,i,f,c): self.calls.append(('diagnose',i)); return self.diag
    def pause_observation(self,p,i,f,c,*,request,disposition):
        self.calls.append(('pause',i))
        if self.pause_error: raise P00Error(*self.pause_error)
        return PauseObservation({'kind':'SYNTHETIC_WORKSPACE_PAUSE'},not self.pending_writer,
                    self.post,CP,deepcopy(c.fence['native']))


def setup_recovery(mode='DIAGNOSE'):
    interface, old, ctx, store = authority_case('ADOPT')
    d=RecoverDriver(old,ctx,store); g=Guard(); st=Storage(); c=Coordinator(g,st)
    runner=SessionRunner(d,c);d.error='timeout'
    try:runner.execute(interface,old)
    except P00Error:pass
    d.error=None;opening=st.load_fence()
    _, request0, _, request_store=authority_case('RECONCILIATION_ONLY')
    # Merge synthetic trusted documents into the test-only in-memory store.
    request_store=replace(request_store, blobs={**store.blobs,**request_store.blobs},
        pins={k:frozenset(set(store.pins.get(k,()))|set(request_store.pins.get(k,())))
              for k in set(store.pins)|set(request_store.pins)})
    request_store, ref=extend(request_store,'original_plan',{'plan':old})
    b={k:deepcopy(v) for k,v in request0['semantic'].items() if k!='operations'}
    b['refs']['original_plan']=ref;b['target']=deepcopy(old['semantic']['target'])
    if mode is not None:
        request_store, ref=extend(request_store,'recovery_request',{
            'schema_version':1,'withdrawn':False,'mode':mode,
            'scope':{'host_id':old['semantic']['host_id'],'owner_sid':SID,
                'original_plan_digest':old['plan_digest'],'original_fence_digest':digest(opening)}})
        b['refs']['recovery_request']=ref
    request=make_plan(b,'2026-09-13T23:00:00Z')
    approval=deepcopy(request_store.get('approval',request0['approval_ref']));approval['plan_digest']=request['plan_digest']
    request_store, ref=extend(request_store,'approval',approval);request['approval_ref']=ref
    d.store=request_store;d.calls=[]
    return runner,d,st,g,request,old,opening


class RecoveryIntegrationTests(unittest.TestCase):
    def reject(self,code,function,*a):
        with self.assertRaises(P00Error) as caught:function(*a)
        self.assertEqual(int(caught.exception.code),code)
        return caught.exception.reason
    def test_diagnostics_preserve_exact_original_fence(self):
        r,d,st,g,p,old,before=setup_recovery(); n=g.acquisitions
        out=r.reconcile(p)
        self.assertEqual(st.load_fence(),before); self.assertEqual(g.acquisitions,n+1)
        self.assertEqual(out['state'],'DIAGNOSTICS_RECORDED');self.assertTrue(out['fence_retained'])
        self.assertNotIn('synthetic-private-only',str(out));self.assertNotIn('secret',str(out))
        self.assertFalse(any(k[0]=='run' for k in d.calls))
        self.assertEqual(completed_steps(st.read_events(),old),{})
    def test_diagnostics_can_report_low_ram_without_repair(self):
        r,d,st,g,p,old,before=setup_recovery(); original=d.refresh
        def refresh(*a,**kw):
            f=original(*a,**kw); f.observed['resources']['installed_ram_bytes']=0;return f
        d.refresh=refresh;self.assertEqual(r.reconcile(p)['exit'],0)
        self.assertEqual(st.load_fence(),before)
    def test_diagnostics_still_require_output_budget(self):
        r,d,st,g,p,old,before=setup_recovery(); original=d.refresh
        def refresh(*a,**kw):
            f=original(*a,**kw);f.observed['free_bytes']['volume1']=0;return f
        d.refresh=refresh;self.reject(13,r.reconcile,p);self.assertEqual(st.load_fence(),before)
    def test_diagnostic_cap_retains_fence(self):
        r,d,st,g,p,old,before=setup_recovery();d.diag={'secret':'x'*300000}
        self.reject(22,r.reconcile,p);self.assertEqual(st.load_fence(),before)
    def test_missing_diagnostics_not_success(self):
        r,d,st,g,p,old,before=setup_recovery();d.diag={}
        self.reject(19,r.reconcile,p);self.assertEqual(st.load_fence(),before)
    def test_pause_releases_without_committing(self):
        r,d,st,g,p,old,before=setup_recovery('PAUSE');out=r.reconcile(p)
        self.assertEqual(out['exit'],20);self.assertEqual(out['state'],'SAFE_PAUSE')
        self.assertIsNone(st.load_fence());self.assertFalse(out['step_committed'])
        self.assertEqual(self.reject(12,completed_steps,st.read_events(),old),'ORIGINAL_RUN_REVOKED')
    def test_cancel_is_not_rollback_or_success(self):
        r,d,st,g,p,old,before=setup_recovery('CANCEL');out=r.reconcile(p)
        self.assertEqual(out['state'],'CANCELLED');self.assertFalse(out['mutation_replayed'])
        self.assertFalse(out['host_ready']);self.assertFalse(out['qualification_issued'])
        self.assertFalse(any(k[0]=='run' for k in d.calls))
    def test_cancel_pending_writer_retains(self):
        r,d,st,g,p,old,before=setup_recovery('CANCEL');d.pending_writer=True
        self.reject(21,r.reconcile,p);self.assertEqual(st.load_fence(),before)
    def test_cancel_unrevoked_queue_retains(self):
        r,d,st,g,p,old,before=setup_recovery('CANCEL');d.post=False
        self.reject(21,r.reconcile,p);self.assertEqual(st.load_fence(),before)
    def test_failed_clear_keeps_durable_safe_pause(self):
        r,d,st,g,p,old,before=setup_recovery('PAUSE');st.fail_clear=True
        self.reject(18,r.reconcile,p);self.assertEqual(st.load_fence()['state'],'SAFE_PAUSE')
        self.assertEqual(completed_steps(st.read_events(),old),{})
    def test_expiry_after_observation_prevents_release(self):
        r,d,st,g,p,old,before=setup_recovery('PAUSE');orig=d.pause_observation
        def late(*a,**kw):
            out=orig(*a,**kw);d.ctx=replace(d.ctx,now=NOW+timedelta(days=2));return out
        d.pause_observation=late;self.reject(12,r.reconcile,p);self.assertEqual(st.load_fence(),before)
    def test_authority_rollback_before_release(self):
        r,d,st,g,p,old,before=setup_recovery('PAUSE');d.generation=3;orig=d.pause_observation
        def late(*a,**kw):
            out=orig(*a,**kw);d.generation=2;return out
        d.pause_observation=late;self.reject(15,r.reconcile,p);self.assertEqual(st.load_fence(),before)
    def test_wrong_sid_cannot_read_original_fence(self):
        r,d,st,g,p,old,before=setup_recovery();d.ctx=replace(d.ctx,execution_sid='S-1-5-18');n=g.acquisitions
        self.reject(12,r.reconcile,p);self.assertEqual(g.acquisitions,n)
    def test_default_reconcile_never_calls_run(self):
        r,d,st,g,p,old,before=setup_recovery(None);out=r.reconcile(p)
        self.assertEqual(out['state'],'RECONCILED');self.assertIsNone(st.load_fence())
        self.assertFalse(any(k[0]=='run' for k in d.calls));self.assertEqual(len(completed_steps(st.read_events(),old)),1)
    def test_bad_completion_keeps_original(self):
        r,d,st,g,p,old,before=setup_recovery(None);d.post=False
        self.reject(19,r.reconcile,p);self.assertEqual(st.load_fence(),before)
    def test_diagnostics_failure_does_not_relabel_original_state(self):
        r,d,st,g,p,old,before=setup_recovery()
        d.diagnose=lambda *a: (_ for _ in ()).throw(P00Error(18,'CAPTURE_FAILED'))
        self.reject(18,r.reconcile,p);self.assertEqual(st.load_fence(),before)
    def test_fence_changed_under_read_blocks(self):
        r,d,st,g,p,old,before=setup_recovery();original=d.diagnose
        def changed(*a):
            out=original(*a);r.coordinator.fence['reason']='CHANGED';return out
        d.diagnose=changed;self.reject(16,r.reconcile,p)
    def test_unknown_mode_not_a_dynamic_command(self):
        r,d,st,g,p,old,before=setup_recovery('KILL')
        self.reject(12,r.reconcile,p);self.assertEqual(st.load_fence(),before)
    def test_old_digest_cannot_cancel_later_fence(self):
        r,d,st,g,p,old,before=setup_recovery('CANCEL')
        before['reason']='DIFFERENT_ATTEMPT';st.write_fence(before)
        self.reject(12,r.reconcile,p);self.assertEqual(st.load_fence(),before)
    def test_safe_pause_refuses_terminal_success_flags(self):
        r,d,st,g,p,old,before=setup_recovery('PAUSE')
        observed=PauseObservation({'x':1},True,True,CP,before['native']).record(before['action'],'PAUSE',p['plan_digest'])
        observed['postconditions_observed']=True
        c=r.coordinator
        initial,auth=r._fresh('verify',p)
        with c.acquire_bound_reconciliation(auth,p,initial.context,initial.store):
            self.reject(21,c.safe_pause,observed)
    def test_cancel_blocks_later_original_apply(self):
        r,d,st,g,p,old,before=setup_recovery('CANCEL');r.reconcile(p)
        self.assertEqual(self.reject(12,r.execute,'apply',old),'ORIGINAL_RUN_REVOKED')


class DetachedReadTests(unittest.TestCase):
    def rows(self,events):return [{'event':e} for e in events]
    def record(self):
        return [{'kind':'READ_PROBE_INTENT','read_id':'read-a'},
          {'kind':'READ_PROBE_STARTED','read_id':'read-a','witness':{'pid':5,'start':'x','job_name':'test'}}]
    def test_completed_read_removed(self):
        es=self.record();es.append({'kind':'READ_PROBE_RESULT','read_id':'read-a',
            'native_witness':es[1]['witness'],'tree_terminal':True})
        self.assertEqual(pending_reads(self.rows(es)),{})
    def test_process_exit_without_tree_terminal_not_proof(self):
        es=self.record();es.append({'kind':'READ_PROBE_RESULT','read_id':'read-a',
            'native_witness':es[1]['witness'],'tree_terminal':False,'native_exit':0})
        with self.assertRaises(P00Error):pending_reads(self.rows(es))
    def test_unresolved_retained(self):
        es=self.record();es.append({'kind':'READ_PROBE_UNRESOLVED','read_id':'read-a'})
        self.assertEqual(set(pending_reads(self.rows(es))),{'read-a'})
    def test_reused_counter_is_ambiguous(self):
        es=self.record();es.append({'kind':'READ_PROBE_INTENT','read_id':'read-a'})
        with self.assertRaises(P00Error):pending_reads(self.rows(es))
    def test_result_without_intent_rejected(self):
        with self.assertRaises(P00Error):pending_reads(self.rows([{'kind':'READ_PROBE_RESULT','read_id':'a'}]))
    def test_explicit_reconciliation_preserves_original_fence(self):
        r,d,st,g,p,old,before=setup_recovery()
        for e in self.record():st.append_event(e)
        initial,auth=r._fresh('verify',p);c=r.coordinator
        with c.acquire_bound_reconciliation(auth,p,initial.context,initial.store):
            system=SimpleNamespace(writer=lambda w:{'observed':'terminal','witness':w})
            self.assertEqual(len(reconcile_detached_reads(system,c)),1)
        self.assertEqual(pending_reads(st.read_events()),{});self.assertEqual(st.load_fence(),before)
    def test_missing_started_witness_not_guessed_away(self):
        r,d,st,g,p,old,before=setup_recovery();st.append_event(self.record()[0])
        initial,auth=r._fresh('verify',p);c=r.coordinator
        with c.acquire_bound_reconciliation(auth,p,initial.context,initial.store):
            with self.assertRaises(P00Error):reconcile_detached_reads(SimpleNamespace(),c)
        self.assertEqual(st.load_fence(),before)


class ConcretePauseTests(unittest.TestCase):
    def setup_case(self):
        r,d,st,g,request,old,before=setup_recovery('PAUSE')
        reader=SimpleNamespace(selected=lambda *a,**kw:{'ref':CP,'claim':{
            'revoked_plan_digest':old['plan_digest'],'revoked_run_id':old['semantic']['run_id'],
            'pending_operations':[],'servicing_queue_empty':True}})
        system=SimpleNamespace(all_writers=lambda w:[],pending_reboot=lambda:{'cbs':False})
        d=SimpleNamespace(source_kind='WORKSPACE_TEST',system=system,_reader=lambda f:reader)
        c=SimpleNamespace(held=True,admission=SimpleNamespace(purpose='RECONCILIATION_ONLY'),fence=before,storage=st)
        fresh=SimpleNamespace(context=SimpleNamespace(now=NOW),observed={'synthetic':True})
        return d,old,fresh,c,request,reader
    def test_concrete_pause_requires_both_actual_writer_and_authenticated_revocation(self):
        d,old,f,c,p,reader=self.setup_case()
        value=pause_observation(d,old,0,f,c,request=p,disposition='PAUSE')
        self.assertIsInstance(value,PauseObservation);self.assertTrue(value.no_pending_writer)
    def test_concrete_pending_reboot_blocks(self):
        d,old,f,c,p,reader=self.setup_case();d.system.pending_reboot=lambda:{'cbs':True}
        with self.assertRaises(P00Error):pause_observation(d,old,0,f,c,request=p,disposition='PAUSE')
    def test_concrete_writer_unknown_blocks(self):
        d,old,f,c,p,reader=self.setup_case();d.system.all_writers=lambda w:(_ for _ in ()).throw(P00Error(21,'UNKNOWN'))
        with self.assertRaises(P00Error):pause_observation(d,old,0,f,c,request=p,disposition='PAUSE')
    def test_concrete_unrevoked_queue_blocks(self):
        d,old,f,c,p,reader=self.setup_case();reader.selected=lambda *a,**kw:{'ref':CP,'claim':{}}
        with self.assertRaises(P00Error):pause_observation(d,old,0,f,c,request=p,disposition='PAUSE')
    def test_diagnose_records_unknown_not_terminal(self):
        d,old,f,c,p,reader=self.setup_case();d.system.service=lambda n:(_ for _ in ()).throw(P00Error(12,'DENIED'))
        result=diagnose(d,old,0,f,c);self.assertEqual(result['errors']['WslService']['exit'],12)
        self.assertFalse(result['postconditions_observed'])
