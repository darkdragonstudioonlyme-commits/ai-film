"""Synthetic ports exercise rerun control flow, not native verification evidence."""
from copy import deepcopy
from dataclasses import replace
from types import SimpleNamespace
from unittest.mock import patch
import unittest
from helpers import *
from test_session_integration import Driver, Guard, Storage
from aifilm_p00.admission import Coordinator
from aifilm_p00.session import SessionRunner, Completion, Refresh
from aifilm_p00.resume import completed_steps, progress_digest
from aifilm_p00.errors import P00Error
from aifilm_p00.native import noop

class RevalidateDriver(Driver):
    noop_fail=False;noop_post=True;noop_error=None
    def pre_noop(self,p,f,c,done):
        self.calls.append(('pre_noop',len(done)))
        if self.noop_fail:raise P00Error(13,'NOOP_OUTPUT_BUDGET')
    def revalidate_committed(self,p,f,c,done):
        self.calls.append(('live_noop',len(done)))
        c.native_started({'pid':333,'start':'fresh','action_id':'GUEST_ASSERT_CONTENT'})
        if self.noop_error:raise P00Error(*self.noop_error)
        raw={'kind':'NATIVE_LIVE_REVALIDATION','baseline_digest':progress_digest(done),
             'assertions':{'current_material':digest(self.material),'host_ready':False}}
        return Completion(deepcopy(self.material),raw,True,self.noop_post,deepcopy(c.fence['native']))

class NoopSessionTests(unittest.TestCase):
    def setup_case(self):
        interface,p,ctx,store=authority_case('ADOPT');d=RevalidateDriver(p,ctx,store)
        st=Storage();g=Guard();runner=SessionRunner(d,Coordinator(g,st));runner.execute(interface,p)
        d.calls=[]
        return runner,d,st,g,interface,p
    def reject(self,code,function,*a):
        with self.assertRaises(P00Error) as caught:function(*a)
        self.assertEqual(int(caught.exception.code),code);return caught.exception.reason
    def test_live_reads_have_intent_but_original_progress_is_not_duplicated(self):
        r,d,st,g,i,p=self.setup_case();before=completed_steps(st.read_events(),p)
        out=r.execute(i,p)
        self.assertEqual(out['state'],'NOOP');self.assertFalse(out['host_ready'])
        self.assertEqual(completed_steps(st.read_events(),p),before)
        self.assertFalse(any(k[0]=='run' for k in d.calls))
        frames=[e['event']['record'] for e in st.read_events() if e['event']['kind']=='SET_FENCE']
        self.assertTrue(any(f['witness'].get('execution_phase')=='LIVE_REVALIDATION' for f in frames))
    def test_repeat_noop_still_reads_live(self):
        r,d,st,g,i,p=self.setup_case();r.execute(i,p);d.calls=[]
        self.assertEqual(r.execute(i,p)['state'],'NOOP');self.assertIn(('live_noop',1),d.calls)
        self.assertEqual(len(completed_steps(st.read_events(),p)),1)
    def test_noop_failure_retains_separate_fence(self):
        r,d,st,g,i,p=self.setup_case();d.noop_error=(19,'CONTENT_CHANGED')
        self.reject(19,r.execute,i,p);f=st.load_fence()
        self.assertEqual(f['state'],'UNCERTAIN');self.assertEqual(f['witness']['execution_phase'],'LIVE_REVALIDATION')
        self.assertEqual(len(completed_steps(st.read_events(),p)),1)
    def test_noop_native_pending_not_success(self):
        r,d,st,g,i,p=self.setup_case();d.noop_error=(21,'WRITER_PENDING')
        self.reject(21,r.execute,i,p);self.assertIsNotNone(st.load_fence())
    def test_budget_missing_before_fence(self):
        r,d,st,g,i,p=self.setup_case();d.noop_fail=True
        self.reject(13,r.execute,i,p);self.assertIsNone(st.load_fence());self.assertNotIn(('live_noop',1),d.calls)
    def test_failed_postcondition_never_commits_revalidation(self):
        r,d,st,g,i,p=self.setup_case();d.noop_post=False
        self.reject(19,r.execute,i,p);self.assertEqual(st.load_fence()['state'],'UNCERTAIN')
    def test_clear_failure_keeps_revalidation_terminal(self):
        r,d,st,g,i,p=self.setup_case();st.fail_clear=True
        self.reject(18,r.execute,i,p);self.assertEqual(st.load_fence()['state'],'TERMINAL')
    def test_wrong_baseline_blocks(self):
        r,d,st,g,i,p=self.setup_case();orig=d.revalidate_committed
        def changed(*a):
            result=orig(*a);result.raw_evidence['baseline_digest']='0'*64;return result
        d.revalidate_committed=changed;self.reject(15,r.execute,i,p)
    def test_authority_expiring_during_noop_blocks_commit(self):
        r,d,st,g,i,p=self.setup_case();orig=d.revalidate_committed
        def changed(*a):
            result=orig(*a);d.ctx=replace(d.ctx,now=NOW.replace(year=2027));return result
        d.revalidate_committed=changed;self.reject(12,r.execute,i,p)
    def test_no_fake_completion_dictionary(self):
        r,d,st,g,i,p=self.setup_case();d.revalidate_committed=lambda *a:{'postconditions_observed':True}
        self.reject(19,r.execute,i,p)


class ConcreteNoopTests(unittest.TestCase):
    def setUp(self):
        self.snapshot_patcher=patch('aifilm_p00.native.evidence_pipeline.NativeEvidencePipeline')
        self.pipeline=self.snapshot_patcher.start();self.addCleanup(self.snapshot_patcher.stop)
        self.pipeline.return_value.capture.return_value={'index_digest':CP,'record_count':15}
    def setup_case(self,purpose='ADOPT'):
        i,p,ctx,store=authority_case(purpose)
        material=deepcopy(p['semantic']['expected_after'])
        obs={'material':material,'target':{'registration_id':'reg','wsl_version':2},
             'running':[p['semantic']['target']['name']],'resources':host_resources(),
             'remaining_budgets':p['semantic']['budgets'],'free_bytes':{'volume1':100*GIB}}
        fresh=Refresh(ctx,store,obs,1,'WORKSPACE_TEST')
        details={};closed={'sha256':CP,'file_identity':{'file_id':1},'volume_id':'volume1'}
        if purpose in ('RESTORE_IMPORT','RESTORE_VERIFY','RESTORE_EXPORT'):
            obs['running']=[];details['vhd']=closed;details['source_vhd']=closed;details['checkpoint']={'sha256':CP,'bytes':100}
        if purpose=='SUPPORT_BUNDLE':
            details['bundle']={'exit':23,'outcome':'BLOCKED_REDACTION','published':False}
        completed={}
        for ix,operation in enumerate(p['semantic']['operations']):
            raw={'kind':'NATIVE_OPERATION_AFTER','details':deepcopy(details)}
            completed[ix]=Completion(material,raw,True,True,None).journal_record(operation['action'])
        calls=[];system=SimpleNamespace(all_writers=lambda w:[],installer_idle=lambda a:{'service':a},pending_reboot=lambda:{'pending':False})
        def guest(plan,op,c,extra=None):
            calls.append(op);return {'capture':{'actual':{'synthetic_asserted_content':True},'operation':op}}
        d=SimpleNamespace(binding={'final_captures':[],'critical_files':[{'path':'fixture'}],'export_path':'file'},
            source_kind='WORKSPACE_TEST',system=system,proofs={},
            _source=lambda *a:{'claim':{'critical_files':[{'path':'fixture'}]}},
            _eligible_guest=lambda *a:{'inventory':{'actual':{}}},_guest=guest,
            _post_c3=lambda *a:{'actual_postchecks':'synthetic'},_vhd_closed=lambda row:deepcopy(closed),
            _checkpoint=lambda path:{'sha256':CP,'bytes':100},refresh=lambda *a,**kw:fresh)
        c=SimpleNamespace(held=True,fence={'witness':{'execution_phase':'LIVE_REVALIDATION'},'native':None})
        return d,p,fresh,c,completed,calls
    def run_case(self,*items):
        d,p,f,c,completed,calls=items
        return noop.revalidate(d,p,f,c,completed)
    def test_adopt_reads_content_without_workspace_mutation(self):
        case=self.setup_case();out=self.run_case(*case)
        self.assertEqual(case[-1],['ASSERT_CONTENT']);self.assertTrue(out.postconditions_observed)
        self.assertFalse(out.raw_evidence['assertions']['host_ready'])
    def test_create_reads_without_user_creation(self):
        case=self.setup_case('CREATE');self.run_case(*case);self.assertEqual(case[-1],['ASSERT_CONTENT'])
    def test_discovery_no_workspace_action(self):
        case=self.setup_case('DISCOVERY');self.run_case(*case);self.assertEqual(case[-1],[])
    def test_target_lifecycle_does_not_stop_restart_again(self):
        case=self.setup_case('TARGET_LIFECYCLE');self.run_case(*case);self.assertEqual(case[-1],['ASSERT_CONTENT'])
    def test_host_restart_does_not_request_reboot(self):
        case=self.setup_case('HOST_RESTART');out=self.run_case(*case)
        self.assertIn('affected_resources',out.raw_evidence['details'])
    def test_engine_checks_services_without_installer(self):
        case=self.setup_case('ENGINE');out=self.run_case(*case)
        self.assertEqual(set(out.raw_evidence['details']['servicing']),{'ENABLE_PREREQUISITES','INSTALL_RUNTIME'})
    def test_import_checks_stopped_vhd_without_boot(self):
        case=self.setup_case('RESTORE_IMPORT');self.run_case(*case);self.assertEqual(case[-1],[])
    def test_restore_verify_stays_stopped(self):
        case=self.setup_case('RESTORE_VERIFY');self.run_case(*case);self.assertEqual(case[-1],[])
    def test_export_reads_existing_checkpoint_not_export_command(self):
        case=self.setup_case('RESTORE_EXPORT');out=self.run_case(*case)
        self.assertEqual(out.raw_evidence['details']['checkpoint']['sha256'],CP)
    def test_redaction_failure_not_turned_into_noop_success(self):
        case=self.setup_case('SUPPORT_BUNDLE');out=self.run_case(*case)
        self.assertEqual(out.raw_evidence['assertions']['interface_outcome'],{'exit':23,'state':'BLOCKED_REDACTION'})
    def test_passive_metadata_no_guest(self):
        case=self.setup_case('PASSIVE');self.run_case(*case);self.assertEqual(case[-1],[])
    def test_vhd_changed_rejected_without_boot(self):
        case=self.setup_case('RESTORE_IMPORT');case[0]._vhd_closed=lambda row:{'sha256':'0'*64,'file_identity':{'file_id':1},'volume_id':'volume1'}
        with self.assertRaises(P00Error):self.run_case(*case)
        self.assertEqual(case[-1],[])
    def test_legacy_missing_vhd_hash_is_not_silently_adopted(self):
        case=self.setup_case('RESTORE_IMPORT');case[4][0]['observations']['details']['vhd'].pop('sha256')
        case[4][0]['evidence_digest']=digest(case[4][0]['observations'])
        with self.assertRaises(P00Error):self.run_case(*case)
    def test_changed_checkpoint_rejected(self):
        case=self.setup_case('RESTORE_EXPORT');case[0]._checkpoint=lambda path:{'sha256':'0'*64,'bytes':100}
        with self.assertRaises(P00Error):self.run_case(*case)
    def test_stopped_at_end_rejected(self):
        case=self.setup_case();case[2].observed['running']=[]
        with self.assertRaises(P00Error):self.run_case(*case)
    def test_snapshot_failure_prevents_completed_observation(self):
        case=self.setup_case();self.pipeline.return_value.capture.side_effect=P00Error(18,'SNAPSHOT_IO')
        with self.assertRaises(P00Error):self.run_case(*case)
    def test_no_fence_no_guest(self):
        case=self.setup_case();case[3].fence=None
        with self.assertRaises(P00Error):self.run_case(*case)
        self.assertEqual(case[-1],[])
    def test_tampered_original_evidence_rejected(self):
        case=self.setup_case();case[4][0]['observations']['unexpected']=True
        with self.assertRaises(P00Error):self.run_case(*case)
    def test_site_verify_uses_new_terminal_sweep_not_lifecycle(self):
        case=self.setup_case('SITE_VERIFY')
        with patch('aifilm_p00.native.terminal_sweep.NativeTerminalSweep') as sweep:
            sweep.return_value.run.return_value={'terminal':{'synthetic':True}}
            out=self.run_case(*case);self.assertEqual(sweep.return_value.run.call_count,1)
        self.assertIn('terminal',out.raw_evidence['details'])
