"""Route oracles tested on explicit synthetic journal data; never native fixtures."""
from copy import deepcopy
from pathlib import Path
import subprocess,sys,unittest
from helpers import authority_case,B
from test_session_integration import Driver,Guard,Storage
from aifilm_p00.admission import Coordinator
from aifilm_p00.session import SessionRunner
from aifilm_p00.errors import P00Error
from aifilm_p00.route_observation import route_observation

ROOT=Path(__file__).resolve().parents[1]

class RouteHarnessTests(unittest.TestCase):
    def setup(self,purpose='CREATE',wait=False):
        i,p,ctx,store=authority_case(purpose,'LAB')
        d=Driver(p,ctx,store);g=Guard();st=Storage();s=SessionRunner(d,Coordinator(g,st))
        if wait:d.run_result={'state':'AWAITING_USER_INIT'}
        out=s.execute(i,p)
        # This declaration is only a synthetic oracle fixture; not a change to
        # the Driver and never submitted to the native factory or its HKLM store.
        out['source_kind']='LAB'
        return p,out,st.read_events(),st.load_fence()
    def reject(self,fn,*a,**kw):
        with self.assertRaises(P00Error):fn(*a,**kw)
    def test_commit_requires_actual_journal_completion(self):
        p,r,rows,f=self.setup();o=route_observation(p,r,rows,f,'COMMIT')
        self.assertEqual(o['completed_step_count'],3);self.assertFalse(o['qualification_issued']);self.assertFalse(o['closes_parent_T_or_F'])
    def test_exit_alone_not_execution(self):
        p,r,rows,f=self.setup();self.reject(route_observation,p,r,rows[:1],f,'COMMIT')
    def test_expected_body_not_actual(self):
        p,r,rows,f=self.setup();r['source_kind']='DOCUMENT';self.reject(route_observation,p,r,rows,f,'COMMIT')
    def test_missing_final_record_fails(self):
        p,r,rows,f=self.setup();rows=[x for x in rows if x['event']['kind']!='SESSION_OBSERVED']
        self.reject(route_observation,p,r,rows,f,'COMMIT')
    def test_wait_is_not_commit(self):
        p,r,rows,f=self.setup(wait=True);self.reject(route_observation,p,r,rows,f,'COMMIT')
    def test_wait_requires_its_fence(self):
        p,r,rows,f=self.setup(wait=True);self.assertTrue(route_observation(p,r,rows,f,'PAUSE')['fence_retained'])
        self.reject(route_observation,p,r,rows,None,'PAUSE')
    def test_noop_must_have_live_revalidation(self):
        p,r,rows,f=self.setup();r['state']='NOOP';self.reject(route_observation,p,r,rows,f,'NOOP')
    def test_unknown_expectation(self):
        p,r,rows,f=self.setup();self.reject(route_observation,p,r,rows,f,'FORCE_PASS')
    def test_qualification_flag_rejected(self):
        p,r,rows,f=self.setup();r['qualification_issued']=True;self.reject(route_observation,p,r,rows,f,'COMMIT')
    def test_parent_gate_flag_rejected(self):
        p,r,rows,f=self.setup();r['host_ready']=True;self.reject(route_observation,p,r,rows,f,'COMMIT')
    def test_list_imports_without_native_execution(self):
        proc=subprocess.run([sys.executable,str(ROOT/'tools/run_native_route_tests.py'),'--list'],capture_output=True,timeout=10)
        self.assertEqual(proc.returncode,0,proc.stderr);self.assertIn(b'NOT_RUN',proc.stdout);self.assertIn(b'RESTORE_IMPORT',proc.stdout)
    def test_native_suite_is_blocked_on_posix(self):
        proc=subprocess.run([sys.executable,str(ROOT/'tools/run_native_route_tests.py'),'--suite-ref',B,'--case-id','NR-CREATE'],capture_output=True,timeout=10)
        self.assertEqual(proc.returncode,11,proc.stderr);self.assertIn(b'WINDOWS_X64_REQUIRED',proc.stdout)

class PauseIdentityOracleTests(unittest.TestCase):
    """Explicit synthetic recovery journal; no native authority is generated."""
    def paused(self):
        from test_dev4_recovery import setup_recovery
        runner,driver,storage,guard,request,original,_=setup_recovery('PAUSE')
        result=runner.reconcile(request)
        result['source_kind']='LAB'  # Oracle fixture only, never factory input.
        return request,original,result,storage.read_events()
    def check(self,request,original,result,rows):
        return route_observation(request,result,rows,None,'PAUSE',original_plan=original)
    def test_exact_safe_pause_and_clear_observed(self):
        request,original,result,rows=self.paused()
        self.assertTrue(self.check(request,original,result,rows)['expectation_observed'])
    def test_safe_pause_another_original_run_rejected(self):
        request,original,result,rows=self.paused()
        for row in rows:
            if row['event']['kind']=='SET_FENCE' and row['event']['record']['state']=='SAFE_PAUSE':
                row['event']['record']['plan_digest']=B
        with self.assertRaises(P00Error):self.check(request,original,result,rows)
    def test_safe_pause_another_request_rejected(self):
        request,original,result,rows=self.paused()
        for row in rows:
            if row['event']['kind']=='SET_FENCE' and row['event']['record']['state']=='SAFE_PAUSE':
                row['event']['record']['pause_observation']['request_digest']=B
        with self.assertRaises(P00Error):self.check(request,original,result,rows)
    def test_safe_pause_evidence_digest_mismatch_rejected(self):
        request,original,result,rows=self.paused()
        for row in rows:
            if row['event']['kind']=='SET_FENCE' and row['event']['record']['state']=='SAFE_PAUSE':
                row['event']['record']['pause_observation']['evidence_digest']=B
        with self.assertRaises(P00Error):self.check(request,original,result,rows)
    def test_safe_pause_missing_matching_clear_rejected(self):
        request,original,result,rows=self.paused()
        rows=[row for row in rows if row['event']['kind']!='CLEAR_FENCE']
        with self.assertRaises(P00Error):self.check(request,original,result,rows)
