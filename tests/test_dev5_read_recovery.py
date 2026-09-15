"""Workspace-only original-request integration. No Windows or network calls."""
from copy import deepcopy
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace
import unittest

from helpers import authority_case, canonical, sha256, digest, SID, NOW, CP, GIB
from test_session_integration import Driver, Guard, Storage
from test_dev4_recovery import extend
from aifilm_p00.admission import Coordinator
from aifilm_p00.plans import make_plan
from aifilm_p00.session import SessionRunner, Refresh
from aifilm_p00.read_recovery import ReadRecoveryRunner, ReadObservation, check_read_release
from aifilm_p00.native.read_recovery import pending_reads
from aifilm_p00.native.read_request_recovery import observe
from aifilm_p00.journal_budget import JournalBudget, RECOVERY_HEADROOM
from aifilm_p00.errors import P00Error


class ReadDriver(Driver):
    def __init__(self,*a):
        super().__init__(*a); self.observer_hook=None; self.budget_error=False; self.no_witness=False
    def refresh_read_recovery(self,p,c):
        self.calls.append(('read_recovery_refresh',None))
        return self.refresh(p,coordinator=c)
    def reserve_read_recovery(self,p,f,c,n):
        self.calls.append(('read_reserve',n))
        if self.budget_error:raise P00Error(13,'JOURNAL_CAPACITY')
    def read_run_revocation(self,old,p,f,mode):
        return {'ref':CP,'kind':'SYNTHETIC_REVOKED'}
    def observe_detached_read(self,e,f,diagnostic=False):
        self.calls.append(('observe_read',e['read_id']))
        if self.observer_hook:self.observer_hook(self)
        return ReadObservation({'SYNTHETIC':'terminal','secret':'not-public'},True,
                               digest(e['witness']) if 'witness' in e else None,
                               CP if 'witness' not in e else None)


def setup(mode='RECONCILE',count=1,witness=True):
    _,old,ctx,_=authority_case('PASSIVE')
    _,rp,_,store=authority_case('RECONCILIATION_ONLY')
    st=Storage()
    for i in range(count):
        st.append_event({'kind':'READ_PROBE_INTENT','read_id':'read-'+str(i),'plan_digest':old['plan_digest'],
                         'action_id':'HOST','origin':{k:old['semantic'][k] for k in ('run_id','host_id','owner_sid','execution_class')},
                         'command_digest':CP,'issued_at':NOW.isoformat()})
        if witness: st.append_event({'kind':'READ_PROBE_STARTED','read_id':'read-'+str(i),
                 'witness':{'pid':100+i,'start':str(i),'job_name':'Global\\AI-FILM-P00-JOB-'+'a'*32}})
    reads=pending_reads(st.read_events())
    store,ref=extend(store,'original_plan',{'plan':old})
    b={k:deepcopy(v) for k,v in rp['semantic'].items() if k!='operations'}
    b['refs']['original_plan']=ref;b['target']=deepcopy(old['semantic']['target'])
    store,ref=extend(store,'recovery_request',{'schema_version':1,'withdrawn':False,'mode':mode,
         'scope':{'host_id':old['semantic']['host_id'],'owner_sid':SID,
                  'original_plan_digest':old['plan_digest'],'original_reads_digest':digest(reads)}})
    b['refs']['recovery_request']=ref
    request=make_plan(b,NOW.isoformat())
    a=deepcopy(store.get('approval',rp['approval_ref']));a['plan_digest']=request['plan_digest']
    store,ref=extend(store,'approval',a);request['approval_ref']=ref
    d=ReadDriver(request,ctx,store);g=Guard();s=SessionRunner(d,Coordinator(g,st))
    return ReadRecoveryRunner(s),d,st,g,request,old


class ReadRecoveryTests(unittest.TestCase):
    def rejected(self,code,call,*a):
        with self.assertRaises(P00Error) as e:call(*a)
        self.assertEqual(int(e.exception.code),code);return e.exception.reason
    def test_original_no_fence_read_released_with_one_guard(self):
        r,d,st,g,p,old=setup();o=r.execute(p)
        self.assertEqual(o['state'],'READS_RECONCILED');self.assertEqual(g.acquisitions,1)
        self.assertEqual(pending_reads(st.read_events()),{});self.assertIsNone(st.load_fence())
        self.assertFalse(o['step_committed']);self.assertFalse(o['mutation_fence_created'])
        self.assertFalse(any(c[0]=='run' for c in d.calls))
    def test_no_secret_exposed_in_response(self):
        r,d,st,g,p,_=setup();out=r.execute(p)
        self.assertNotIn('not-public',str(out));self.assertNotIn('secret',str(out))
    def test_diagnose_retains_every_read(self):
        r,d,st,g,p,_=setup('DIAGNOSE',2);opening=deepcopy(pending_reads(st.read_events()))
        out=r.execute(p);self.assertEqual(out['exit'],21)
        self.assertEqual(pending_reads(st.read_events()),opening)
    def test_cancel_does_not_mark_step_complete(self):
        r,d,st,g,p,_=setup('CANCEL');out=r.execute(p)
        self.assertEqual(out['exit'],20);self.assertFalse(out['step_committed'])
        self.assertIsNone(st.load_fence())
    def test_pause_does_not_replay(self):
        r,d,st,g,p,_=setup('PAUSE');out=r.execute(p)
        self.assertEqual(out['exit'],20);self.assertFalse(out['mutation_replayed'])
    def test_cancel_blocks_original_plan_restart(self):
        from aifilm_p00.resume import completed_steps
        r,d,st,g,p,old=setup('CANCEL');r.execute(p)
        self.rejected(12,completed_steps,st.read_events(),old)
    def test_cancel_requires_revocation_not_intent(self):
        r,d,st,g,p,old=setup('CANCEL');d.read_run_revocation=lambda *a:None
        self.rejected(21,r.execute,p);self.assertEqual(len(pending_reads(st.read_events())),1)
    def test_no_old_progress_changed(self):
        from aifilm_p00.resume import completed_steps
        r,d,st,g,p,old=setup();r.execute(p);self.assertEqual(completed_steps(st.read_events(),old),{})
    def test_renewed_authority_expiry_blocks_release(self):
        r,d,st,g,p,_=setup();d.observer_hook=lambda d:setattr(d,'ctx',replace(d.ctx,now=NOW+timedelta(days=3)))
        self.rejected(12,r.execute,p);self.assertEqual(len(pending_reads(st.read_events())),1)
    def test_wrong_sid_blocks_before_guard(self):
        r,d,st,g,p,_=setup();d.ctx=replace(d.ctx,execution_sid='S-1-5-18')
        self.rejected(12,r.execute,p);self.assertEqual(g.acquisitions,0)
    def test_other_plan_read_not_in_authorized_set(self):
        r,d,st,g,p,_=setup();st.append_event({'kind':'READ_PROBE_INTENT','read_id':'read-other','plan_digest':CP})
        self.rejected(12,r.execute,p);self.assertEqual(len(pending_reads(st.read_events())),2)
    def test_set_drift_is_not_a_waiver(self):
        r,d,st,g,p,_=setup();st.append_event({'kind':'READ_PROBE_INTENT','read_id':'new','plan_digest':r.d.store.get('original_plan',p['semantic']['refs']['original_plan'])['plan']['plan_digest']})
        self.rejected(12,r.execute,p)
    def test_existing_mutation_fence_not_adopted(self):
        r,d,st,g,p,_=setup();st.write_fence({'state':'INTENT','plan_digest':CP})
        self.rejected(21,r.execute,p);self.assertEqual(st.load_fence()['state'],'INTENT')
    def test_second_recovery_without_reads_not_success(self):
        r,d,st,g,p,_=setup();r.execute(p)
        self.rejected(11,r.execute,p)
    def test_all_reads_observed_before_first_release(self):
        r,d,st,g,p,_=setup(count=3);original=st.append_event
        def append(e):
            if e['kind']=='READ_PROBE_RECOVERY_COMMITTED':
                self.assertEqual(len([c for c in d.calls if c[0]=='observe_read']),3)
            original(e)
        st.append_event=append;r.execute(p)
    def test_budget_failure_before_any_observer(self):
        r,d,st,g,p,_=setup();d.budget_error=True
        self.rejected(13,r.execute,p);self.assertFalse(any(c[0]=='observe_read' for c in d.calls))
    def test_missing_witness_release_requires_absence_ref(self):
        r,d,st,g,p,_=setup(witness=False)
        d.observe_detached_read=lambda *a:ReadObservation({'x':1},True,None,None)
        self.rejected(10,r.execute,p);self.assertEqual(len(pending_reads(st.read_events())),1)
    def test_witnessless_proof_is_linked_to_release(self):
        r,d,st,g,p,_=setup(witness=False);r.execute(p)
        releases=[e['event'] for e in st.read_events() if e['event']['kind']=='READ_PROBE_RECOVERY_COMMITTED']
        self.assertEqual(releases[0]['absence_proof_ref'],CP)
    def test_observer_pending_is_not_process_exit(self):
        r,d,st,g,p,_=setup();d.observe_detached_read=lambda *a:ReadObservation({'exit':0},False,None)
        self.rejected(21,r.execute,p);self.assertEqual(len(pending_reads(st.read_events())),1)
    def test_failed_release_write_retains_original(self):
        r,d,st,g,p,_=setup();append=st.append_event
        def fail(e):
            if e['kind']=='READ_PROBE_RECOVERY_COMMITTED':raise P00Error(18,'IO_FAILURE')
            append(e)
        st.append_event=fail;self.rejected(18,r.execute,p)
        self.assertEqual(len(pending_reads(st.read_events())),1)
    def test_wrong_witness_digest_blocked(self):
        r,d,st,g,p,_=setup();d.observe_detached_read=lambda *a:ReadObservation({'x':1},True,CP)
        self.rejected(19,r.execute,p)
    def test_authority_rollback_after_observation_blocks(self):
        r,d,st,g,p,_=setup();d.generation=3;d.observer_hook=lambda d:setattr(d,'generation',2)
        self.rejected(15,r.execute,p)
    def test_release_evidence_tampering_blocks_replay(self):
        r,d,st,g,p,_=setup();r.execute(p);rows=st.read_events()
        for row in rows:
            if row['event']['kind']=='READ_PROBE_RECOVERY_COMMITTED':row['event']['observations']={'bad':True}
        self.rejected(15,pending_reads,rows)
    def test_release_entry_tampering_blocks_replay(self):
        r,d,st,g,p,_=setup();r.execute(p);rows=st.read_events()
        rows[1]['event']['action_id']='OTHER';self.rejected(15,pending_reads,rows)
    def test_diagnostics_under_unknown_writer_keep_read(self):
        r,d,st,g,p,_=setup('DIAGNOSE');d.observe_detached_read=lambda *a:ReadObservation({'state':'UNKNOWN'},False,None)
        self.assertEqual(r.execute(p)['pending_read_count'],1)


class NativeReadObserverTests(unittest.TestCase):
    def test_writer_native_path_uses_real_helper_port(self):
        entry={'read_id':'r','witness':{'pid':1,'start':'1','job_name':'job'}}
        d=SimpleNamespace(system=SimpleNamespace(writer=lambda w:{'witness':w,'state':'TERMINAL'}))
        out=observe(d,entry,SimpleNamespace(context=SimpleNamespace(now=NOW)),False)
        self.assertTrue(out.terminal);self.assertEqual(out.witness_digest,digest(entry['witness']))
    def test_running_writer_error_not_cleared(self):
        def running(w):raise P00Error(21,'NATIVE_WRITER_RUNNING')
        d=SimpleNamespace(system=SimpleNamespace(writer=running));e={'read_id':'r','witness':{'pid':1}}
        with self.assertRaises(P00Error):observe(d,e,SimpleNamespace(),False)
    def test_running_writer_diagnostic_has_no_completion(self):
        def running(w):raise P00Error(21,'NATIVE_WRITER_RUNNING')
        d=SimpleNamespace(system=SimpleNamespace(writer=running));e={'read_id':'r','witness':{'pid':1}}
        self.assertFalse(observe(d,e,SimpleNamespace(),True).terminal)
    def test_legacy_missing_witness_cannot_invent_process(self):
        e={'read_id':'legacy'}
        with self.assertRaises(P00Error):observe(SimpleNamespace(),e,SimpleNamespace(),False)
    def test_access_error_not_downgraded_to_unavailable(self):
        def denied(w):raise P00Error(12,'DENIED')
        with self.assertRaises(P00Error):observe(SimpleNamespace(system=SimpleNamespace(writer=denied)),{'witness':{},'read_id':'r'},None,True)


class JournalBudgetTests(unittest.TestCase):
    def test_exact_remaining_plus_recovery_headroom(self):
        b=JournalBudget.reserve(1024*1024,100,1024*1024-100-RECOVERY_HEADROOM)
        b.check(100,4096);b.committed(100,4196,4096);self.assertEqual(b.spent,4096)
    def test_insufficient_capacity_blocks_before_write(self):
        with self.assertRaises(P00Error):JournalBudget.reserve(1024*1024,600000,4096)
    def test_recovery_can_use_retained_headroom(self):
        b=JournalBudget.reserve(1024*1024,600000,4096,recovery=True);b.check(600000,4096)
    def test_cannot_spend_more_than_plan_allowance(self):
        b=JournalBudget.reserve(1024*1024,100,4096)
        with self.assertRaises(P00Error):b.check(100,4097)
    def test_external_append_not_mistaken_for_own_usage(self):
        b=JournalBudget.reserve(1024*1024,100,4096)
        with self.assertRaises(P00Error):b.check(101,100)
    def test_failed_readback_not_committed(self):
        b=JournalBudget.reserve(1024*1024,100,4096)
        with self.assertRaises(P00Error):b.committed(100,110,100)
        self.assertEqual(b.spent,0)
    def test_negative_budget_rejected(self):
        with self.assertRaises(P00Error):JournalBudget.reserve(1000000,0,-1)
    def test_boolean_budget_rejected(self):
        with self.assertRaises(P00Error):JournalBudget.reserve(1000000,0,True)
    def test_read_diagnostics_use_headroom_not_overflow(self):
        b=JournalBudget.reserve(1024*1024,900000,8192,recovery=True)
        b.committed(900000,908192,8192)
        with self.assertRaises(P00Error):b.check(908192,1)

if __name__=='__main__':unittest.main()
