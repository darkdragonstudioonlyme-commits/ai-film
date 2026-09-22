#!/usr/bin/env python3
"""Adversarial regression for previously unguarded current-task/target scope."""
import copy
import tempfile
from pathlib import Path
import unittest
from check_current_work import check_projection, check_audit_scope, check_test_targets

class CurrentWorkTests(unittest.TestCase):
    def setUp(self):
        self.work = dict(work_item='REVIEW-A',mode='DESIGN_REVIEW',status='READY',parent_run_id='RUN-A',
                         baseline_source_commit='a'*40,author_complete=False,code_review_handoff_ready=False,code_review_pass=False)
        self.state = dict(current_work=self.work,current_mode='DESIGN_REVIEW',active_run={'run_id':'RUN-A','status':'BLOCKED'},
                          accepted_code_candidate={'source_commit':'a'*40},readiness_scope='ACCEPTED_CODE_CANDIDATE')
        self.md = 'CURRENT_TASK: REVIEW-A\nCURRENT_MODE: DESIGN_REVIEW\nCURRENT_WORK_STATUS: READY\nREADINESS_SCOPE: ACCEPTED_CODE_CANDIDATE\n'
        self.nxt = 'WORK_ITEM: REVIEW-A\nMODE: DESIGN_REVIEW\nSTATUS: READY\nRUN_ID: RUN-A\n'
        self.receipt = dict(schema_version=1,population_kind='EXACT_REPOSITORY_BOUNDARIES',session_denominator=None,
                            improvement_status='IMPROVEMENT_NOT_PROVEN',historical_semantic_review_complete=False,
                            native_revalidated=False,historical_sessions_reconstructed=False,main_commits_in_window=25,
                            active_control_documents_read=20,input_refs={'main':'a'*40})
    def run_check(self):return check_projection(self.state,self.md,self.nxt)
    def test_authorized_correction_under_blocked_parent(self):self.assertEqual(self.run_check(),[])
    def test_stale_task(self):
        self.md=self.md.replace('REVIEW-A','OLD');self.assertIn('current-work-parity:work_item',self.run_check())
    def test_duplicate_task(self):
        self.md+='CURRENT_TASK: REVIEW-A\n';self.assertTrue(self.run_check())
    def test_mode_drift(self):
        self.state['current_mode']='IMPLEMENTATION';self.assertTrue(self.run_check())
    def test_next_status_drift(self):
        self.nxt=self.nxt.replace('READY','COMPLETE');self.assertTrue(self.run_check())
    def test_parent_drift(self):
        self.work['parent_run_id']='RUN-B';self.assertTrue(self.run_check())
    def test_baseline_drift(self):
        self.work['baseline_source_commit']='b'*40;self.assertTrue(self.run_check())
    def test_unscoped_flags(self):
        self.state['readiness_scope']='CURRENT_WORK';self.assertTrue(self.run_check())
    def test_old_readiness_not_inherited(self):
        self.work['code_review_pass']=True;self.assertTrue(self.run_check())
    def test_boolean_not_integer(self):
        self.work['author_complete']=1;self.assertTrue(self.run_check())
    def test_superseded_ready(self):
        self.state['test_design']={'work_item_id':'OLD','status':'READY'};self.assertTrue(self.run_check())
    def test_superseded_nonactionable(self):
        self.state['test_design']={'work_item_id':'OLD','status':'SUPERSEDED'};self.assertEqual(self.run_check(),[])
    def test_missing_work(self):
        self.state.pop('current_work');self.assertTrue(self.run_check())
    def test_unknowns_are_not_successes(self):self.assertEqual(check_audit_scope(self.receipt),[])
    def test_commit_not_session_denominator(self):
        self.receipt['session_denominator']=25;self.assertTrue(check_audit_scope(self.receipt))
    def test_native_overclaim(self):
        self.receipt['native_revalidated']=True;self.assertTrue(check_audit_scope(self.receipt))
    def test_false_effectiveness(self):
        self.receipt['improvement_status']='EFFECTIVE';self.assertTrue(check_audit_scope(self.receipt))
    def test_bool_metric(self):
        self.receipt['main_commits_in_window']=True;self.assertTrue(check_audit_scope(self.receipt))
    def test_mutable_ref(self):
        self.receipt['input_refs']={'main':'main'};self.assertTrue(check_audit_scope(self.receipt))
    def test_target_alias_missing(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);g=root/'test-governance';g.mkdir()
            for alias in ('TARGET_TEST_CHANGE','TEST_CHANGE_ID','TARGET_TEST_CHANGE_ID'):
                (g/'TEST_REVIEW-A.md').write_text(alias+': TEST_CHANGE-A\n')
                self.assertTrue(check_test_targets(root),alias)
            (g/'TEST_CHANGE-A.md').write_text('evidence')
            self.assertEqual(check_test_targets(root),[])
    def test_conflicting_targets(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);g=root/'test-governance';g.mkdir()
            (g/'TEST_REVIEW-A.md').write_text('TARGET_TEST_CHANGE: TEST_CHANGE-A\nTEST_CHANGE_ID: TEST_CHANGE-B\n')
            self.assertTrue(check_test_targets(root))
    def test_root_machine_task_drift(self):
        self.state['current_task']='OLD';self.assertIn('current-task-machine-parity',self.run_check())
    def test_root_machine_task_matches(self):
        self.state['current_task']=self.work['work_item'];self.assertEqual(self.run_check(),[])
    def test_boolean_receipt_version(self):
        self.receipt['schema_version']=True;self.assertTrue(check_audit_scope(self.receipt))
    def test_nonobject_receipt(self):
        self.assertTrue(check_audit_scope([]))
    def test_gap_alias(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);g=root/'test-governance';g.mkdir()
            (g/'TEST_REVIEW-A.md').write_text('TARGET_TEST_GAP: TEST_GAP-A\n')
            self.assertTrue(check_test_targets(root))
            (g/'TEST_GAP-A.md').write_text('evidence');self.assertEqual(check_test_targets(root),[])

if __name__=='__main__':unittest.main(verbosity=2)
