"""Workspace integration: explicit synthetic driver + real session/journal logic.

No Windows native call, qualified LAB registration, or native measurement is made.
"""
from copy import deepcopy
from dataclasses import replace
from datetime import timedelta
import unittest
from helpers import authority_case,MemoryGuard,host_resources,GIB,NOW,B,CP
from aifilm_p00.codec import digest,canonical,sha256,loads
from aifilm_p00.admission import Coordinator
from aifilm_p00.session import SessionRunner,Refresh,Completion
from aifilm_p00.errors import P00Error
from aifilm_p00.native.coordination import frame,replay
from aifilm_p00.resume import completed_steps

class Guard(MemoryGuard):
    def __init__(self):super().__init__();self.acquisitions=0;self.releases=0
    def acquire(self):self.acquisitions+=1;return super().acquire()
    def release(self):self.releases+=1;super().release()

class Storage:
    def __init__(self):
        self.raw=frame({'kind':'GENESIS','host_id':'synthetic-host','root_identity':{'file_id':'WORKSPACE'}},0,None)
        self.fail_clear=False;self.fail_after=False
    def read_events(self):return replay(self.raw)['rows']
    def load_fence(self):return deepcopy(replay(self.raw)['fence'])
    def append_event(self,e):
        if self.fail_after and e['kind']=='SESSION_OBSERVED':raise P00Error(18,'JOURNAL_IO')
        r=replay(self.raw);self.raw+=frame(deepcopy(e),len(r['rows']),r['previous'])
    def write_fence(self,f):self.append_event({'kind':'SET_FENCE','record':deepcopy(f)})
    def clear_fence(self):
        if self.fail_clear:raise P00Error(18,'JOURNAL_IO')
        self.append_event({'kind':'CLEAR_FENCE','fence_digest':digest(self.load_fence())})

class Driver:
    source_kind='WORKSPACE_TEST'
    def __init__(self,plan,ctx,store):
        self.plan=plan;self.ctx=ctx;self.store=store;self.calls=[];self.material=deepcopy(plan['semantic']['before'])
        self.refreshes=0;self.generation=1;self.hook=None;self.error=None;self.run_result=None
        self.pending_writer=False;self.post=True;self.kind='WORKSPACE_TEST';self.final_empty=False;self.bad_witness=False
    def refresh(self,plan,*,coordinator=None,step=None):
        self.refreshes+=1;self.calls.append(('refresh',step,coordinator is not None))
        if self.hook:self.hook(self,coordinator,step)
        return Refresh(self.ctx,self.store,{'material':deepcopy(self.material),'resources':host_resources(),
                     'free_bytes':{'volume1':100*GIB}},self.generation,self.kind)
    def preconditions(self,p,i,f,c):
        self.calls.append(('preconditions',i))
        if self.error=='precondition':raise P00Error(11,'MISSING_PREREQUISITE')
    def witness(self,p,i,f):return {'host_boot':'boot','controller_pid':1,'controller_start':'1','build_digest':B,'step_id':'step-'+str(i)}
    def run(self,p,i,f,c):
        self.calls.append(('run',i));c.native_started({'pid':100+i,'start':str(i),'action_id':p['semantic']['operations'][i]['action']})
        if self.error=='timeout':raise P00Error(17,'NATIVE_TIMEOUT')
        if self.error=='interrupt':raise KeyboardInterrupt()
        if self.run_result is not None:return deepcopy(self.run_result)
        self.material=deepcopy(p['semantic']['expected_after'])
        return {'state':'OBSERVED'}
    def observe(self,p,i,result,f,c):
        self.calls.append(('observe',i))
        return Completion(deepcopy(self.material),{'raw_result':result,'source_kind':'WORKSPACE_TEST'},
                          not self.pending_writer,self.post,None if self.bad_witness else deepcopy(c.fence['native']))
    def reconcile(self,p,i,f,c):return self.observe(p,i,{'state':'OBSERVED'},f,c)
    def final_assertions(self,p,f,c,done):
        self.calls.append(('final',len(done)))
        return {} if self.final_empty else {'material_digest':digest(self.material),'source_kind':'WORKSPACE_TEST'}

class SessionTests(unittest.TestCase):
    def setup(self,purpose='CREATE',omit=None):
        interface,plan,ctx,store=authority_case(purpose,omit=omit)
        d=Driver(plan,ctx,store);g=Guard();st=Storage();c=Coordinator(g,st)
        return SessionRunner(d,c),d,st,g,interface,plan
    def rejects(self,code,fn,*a):
        with self.assertRaises(P00Error) as e:fn(*a)
        self.assertEqual(int(e.exception.code),code)
        return e.exception.reason
    def test_full_create_one_guard_three_observed_commits(self):
        r,d,st,g,i,p=self.setup();out=r.execute(i,p)
        self.assertEqual(out['completed_steps'],[0,1,2]);self.assertEqual(g.acquisitions,1)
        self.assertEqual(g.releases,1);self.assertIsNone(st.load_fence());self.assertEqual(len(completed_steps(st.read_events(),p)),3)
        self.assertFalse(out['host_ready']);self.assertFalse(out['qualification_issued'])
    def test_missing_qualification_before_guard_or_run(self):
        r,d,st,g,i,p=self.setup(omit='qualification');self.rejects(11,r.execute,i,p)
        self.assertEqual(g.acquisitions,0);self.assertEqual([x for x in d.calls if x[0]=='run'],[])
    def test_refresh_occurs_between_every_step(self):
        r,d,st,g,i,p=self.setup();r.execute(i,p)
        for n in range(3):
            at=d.calls.index(('run',n));self.assertIn(('refresh',n,True),d.calls[:at])
    def test_authority_expiry_before_second_step(self):
        r,d,st,g,i,p=self.setup()
        def hook(d,c,step):
            if step==1:d.ctx=replace(d.ctx,now=d.ctx.now+timedelta(days=2))
        d.hook=hook;self.rejects(12,r.execute,i,p)
        self.assertEqual([x for x in d.calls if x[0]=='run'],[('run',0)])
        self.assertEqual(len(completed_steps(st.read_events(),p)),1)
    def test_authority_generation_cannot_roll_back(self):
        r,d,st,g,i,p=self.setup();d.generation=2
        def hook(d,c,step):
            if step==1:d.generation=1
        d.hook=hook;self.assertEqual(self.rejects(15,r.execute,i,p),'AUTHORITY_ROLLBACK')
    def test_wrong_principal_refresh_stops_before_step(self):
        r,d,st,g,i,p=self.setup()
        def hook(d,c,step):
            if c:d.ctx=replace(d.ctx,execution_sid='S-1-5-18')
        d.hook=hook;self.rejects(12,r.execute,i,p);self.assertFalse(any(x[0]=='run' for x in d.calls))
    def test_request_only_snapshot_not_accepted_under_guard(self):
        r,d,st,g,i,p=self.setup();d.kind='REQUEST_AUTHORITY_ONLY';self.rejects(11,r.execute,i,p)
    def test_production_driver_cannot_return_workspace_observation(self):
        r,d,st,g,i,p=self.setup();d.source_kind='SITE';self.rejects(12,r.execute,i,p)
    def test_wrong_before_no_intent(self):
        r,d,st,g,i,p=self.setup();d.material={'wrong':True};self.rejects(16,r.execute,i,p);self.assertIsNone(st.load_fence())
    def test_precondition_no_intent(self):
        r,d,st,g,i,p=self.setup();d.error='precondition';self.rejects(11,r.execute,i,p);self.assertIsNone(st.load_fence())
    def test_timeout_keeps_original_fence_and_no_commit(self):
        r,d,st,g,i,p=self.setup();d.error='timeout';self.rejects(17,r.execute,i,p)
        f=st.load_fence();self.assertEqual(f['plan_digest'],p['plan_digest']);self.assertEqual(f['state'],'UNCERTAIN')
        self.assertEqual(completed_steps(st.read_events(),p),{})
    def test_interrupt_keeps_fence(self):
        r,d,st,g,i,p=self.setup();d.error='interrupt'
        with self.assertRaises(KeyboardInterrupt):r.execute(i,p)
        self.assertEqual(st.load_fence()['state'],'UNCERTAIN')
    def test_service_pending_blocks_even_after_successful_process(self):
        r,d,st,g,i,p=self.setup();d.pending_writer=True;self.rejects(21,r.execute,i,p)
        self.assertEqual(st.load_fence()['state'],'UNCERTAIN');self.assertEqual(completed_steps(st.read_events(),p),{})
    def test_observed_postcondition_failure_never_committed(self):
        r,d,st,g,i,p=self.setup();d.post=False;self.rejects(19,r.execute,i,p);self.assertIsNotNone(st.load_fence())
    def test_process_witness_mismatch(self):
        r,d,st,g,i,p=self.setup();d.bad_witness=True;self.rejects(19,r.execute,i,p);self.assertIsNotNone(st.load_fence())
    def test_waiting_oobe_retains_fence(self):
        r,d,st,g,i,p=self.setup();d.run_result={'state':'AWAITING_USER_INIT'};out=r.execute(i,p)
        self.assertEqual(out['exit'],20);self.assertEqual(st.load_fence()['state'],'AWAITING_USER_INIT')
    def test_waiting_reboot_retains_fence(self):
        r,d,st,g,i,p=self.setup('ENGINE');d.run_result={'state':'AWAITING_REBOOT'};out=r.execute(i,p)
        self.assertEqual(out['exit'],20);self.assertEqual(st.load_fence()['state'],'AWAITING_REBOOT')
    def test_waiting_owner_does_not_call_observer(self):
        r,d,st,g,i,p=self.setup();d.run_result={'state':'AWAITING_OWNER_VERIFICATION'};self.assertEqual(r.execute(i,p)['exit'],20)
        self.assertFalse(any(x[0]=='observe' for x in d.calls))
    def test_committed_noop_revalidates_final_without_actuation(self):
        r,d,st,g,i,p=self.setup();r.execute(i,p);d.calls=[];out=r.execute(i,p)
        self.assertEqual(out['state'],'NOOP');self.assertFalse(any(x[0]=='run' for x in d.calls));self.assertIn(('final',3),d.calls)
    def test_noop_rejects_final_drift(self):
        r,d,st,g,i,p=self.setup();r.execute(i,p);d.material={'wrong':1};self.rejects(16,r.execute,i,p)
    def test_final_assertions_required(self):
        r,d,st,g,i,p=self.setup();d.final_empty=True;self.rejects(19,r.execute,i,p)
    def test_clear_failure_keeps_terminal_record_for_reconciliation(self):
        r,d,st,g,i,p=self.setup();st.fail_clear=True;self.rejects(18,r.execute,i,p)
        self.assertEqual(st.load_fence()['state'],'TERMINAL');self.assertEqual(completed_steps(st.read_events(),p),{})
    def test_new_run_does_not_read_actively_on_unresolved_fence(self):
        r,d,st,g,i,p=self.setup();d.error='timeout';self.rejects(17,r.execute,i,p);d.calls=[]
        self.rejects(21,r.execute,i,p);self.assertEqual(d.calls,[('refresh',None,False)])
    def test_final_journal_failure_not_success(self):
        r,d,st,g,i,p=self.setup();st.fail_after=True;self.rejects(18,r.execute,i,p)
    def test_completion_no_raw_evidence_rejected(self):
        self.rejects(19,Completion({}, {}, True,True,None).journal_record,'OBSERVE_HOST')
    def test_completion_pending_state_rejected(self):
        self.rejects(21,Completion({}, {'a':1}, True,True,None,'UNCERTAIN').journal_record,'OBSERVE_HOST')
    def test_verify_cannot_actuate_create(self):
        r,d,st,g,i,p=self.setup();self.rejects(10,r.execute,'verify',p);self.assertEqual(d.calls,[])
