#!/usr/bin/env python3
"""Adversarial pure-model tests; not Claude/native/dispatcher integration."""
from copy import deepcopy
import json
from pathlib import Path
import unittest
from check_shared_workflow import (SharedError, knowledge_view, validate_selection,
    check_actor_projection, next_action, seal_static_review, verify_report_bytes,
    check_capabilities, CAPABILITY_GATES, check_governance_runtime_scope)

H='a'*64; J='b'*64

def registry():
    active={'activation_status':'ACTIVE','review_status':'PASS','effectiveness_status':'EFFECTIVE','successor':None}
    return {'records':{'OLD':{**active,'effectiveness_status':'INEFFECTIVE','successor':'NEW'},
                       'NEW':active,'PENDING':{**active,'effectiveness_status':'PENDING_MEASUREMENT'}}}

def routing(**kw):
    f={'identities_match':True,'permission_denied':False,'design_hold':False,
       'knowledge_invalidated':False,'context_current':True,'transport':'IDLE',
       'work_complete':False,'output_verified':False,'profile_ready':True,
       'prerequisites_satisfied':True}
    f.update(kw);return f

def projection():
    w={'mode':'DOC_REVIEW','assignee':'CLAUDE_CODE','author_actor':'CHATGPT','role':'REVIEW','profile':'TEXT_REVIEW',
       'return_to':'PARENT/V02B','next_on_success':'REVIEW_RESULT'}
    md='CURRENT_ASSIGNEE: CLAUDE_CODE\nCURRENT_AUTHOR_ACTOR: CHATGPT\n'
    nxt='ASSIGNEE: CLAUDE_CODE\nAUTHOR_ACTOR: CHATGPT\nRETURN_TO: PARENT/V02B\nON_SUCCESS: REVIEW_RESULT\n'
    return {'current_work':w},md,nxt

def body():
    return {'assessment':'PASS','covered':['R1'],'not_evaluated':[],'findings':[],
            'execution_scope':'STATIC_ONLY','executed_commands':[]}

def caps():
    return {'runtime_enabled':False,'operational_gates':{k:'NOT_VERIFIED' for k in CAPABILITY_GATES},
            'learning_effectiveness':'IMPROVEMENT_NOT_PROVEN'}

class SharedWorkflowTests(unittest.TestCase):
    def test_unknown_acceptance_enum_is_rejected(self):
        for value in (None,'PENDING','SELF_REVIEWED'):
            with self.assertRaisesRegex(SharedError,'CROSS_MODEL_STATE'):
                check_governance_runtime_scope({'documentation_governance':{'promotion_state':'PROMOTED'},'collaboration':{'cross_model_acceptance':value}})
    def test_boolean_acceptance_enum_is_rejected(self):
        with self.assertRaisesRegex(SharedError,'CROSS_MODEL_STATE'):
            check_governance_runtime_scope({'collaboration':{'cross_model_acceptance':True}})
    def test_acceptance_rule_md_parity(self):
        d={'documentation_governance':{'projection_semantics':'S','acceptance_rule':'R'},'collaboration':{'cross_model_acceptance':'NOT_RUN'}}
        with self.assertRaisesRegex(SharedError,'GOVERNANCE_SCOPE_PROJECTION'):
            check_governance_runtime_scope(d,'  PROJECTION_SEMANTICS: S\n  ACCEPTANCE_RULE: WRONG\n')
    def test_projection_semantics_md_parity(self):
        d={'documentation_governance':{'projection_semantics':'S','acceptance_rule':'R'},'collaboration':{'cross_model_acceptance':'NOT_RUN'}}
        with self.assertRaisesRegex(SharedError,'GOVERNANCE_SCOPE_PROJECTION'):
            check_governance_runtime_scope(d,'  PROJECTION_SEMANTICS: WRONG\n  ACCEPTANCE_RULE: R\n')
    def test_legitimate_population_growth(self):
        r=registry();r['records']['ADDED']=dict(r['records']['NEW'])
        self.assertEqual(set(knowledge_view(r)['operative']),{'NEW','PENDING','ADDED'})
    def test_unscoped_promotion_not_runtime_acceptance(self):
        with self.assertRaisesRegex(SharedError,'POLICY_RUNTIME_ACCEPTANCE_CONFLATION'):
            check_governance_runtime_scope({'documentation_governance':{'promotion_state':'PROMOTED'},'collaboration':{'cross_model_acceptance':'NOT_RUN'}})
    def test_policy_and_executor_acceptance_are_distinct(self):
        g={'promotion_state':'PROMOTED','projection_semantics':'INTENDED_CANONICAL_CONTENT_NOT_PUBLICATION_PROOF','acceptance_rule':'MATCHED_POLICY_VERDICTS_NOT_LOCAL_MARKER'}
        self.assertTrue(check_governance_runtime_scope({'documentation_governance':g,'collaboration':{'cross_model_acceptance':'NOT_RUN','acceptance_scope':'EXECUTOR_RUNTIME_PROFILE'}}))
    def test_unusable_terminal_holds_predecessor(self):
        r=registry();r['records']['NEW']['activation_status']='PENDING_ACTIVATION'
        self.assertIn('OLD',knowledge_view(r)['blocked'])
    def test_withdrawn_terminal_holds_predecessor(self):
        self.assertIn('OLD',knowledge_view(registry(),['NEW'])['blocked'])
    def test_pending_terminal_remains_usable(self):
        r=registry();r['records']['NEW']['effectiveness_status']='PENDING_MEASUREMENT'
        self.assertNotIn('OLD',knowledge_view(r)['blocked'])
    def test_author_cannot_use_text_review_profile(self):
        s,m,n=projection();w=s['current_work'];w.update(role='AUTHOR',mode='DOC_DESIGN',assignee='CHATGPT')
        with self.assertRaisesRegex(SharedError,'AUTHOR_PROFILE'):
            check_actor_projection(s,m.replace('CLAUDE_CODE','CHATGPT'),n.replace('CLAUDE_CODE','CHATGPT'))
    def test_current_and_warning_separate(self):
        v=knowledge_view(registry());self.assertEqual(set(v['operative']),{'NEW','PENDING'});self.assertEqual(v['warnings']['OLD'],'HISTORICAL_WARNING')
    def test_pending_not_effective(self):
        self.assertEqual(knowledge_view(registry())['operative']['PENDING'],'UNMEASURED')
    def test_register_not_mutated(self):
        r=registry();before=deepcopy(r);knowledge_view(r);self.assertEqual(r,before)
    def test_unknown_successor(self):
        r=registry();r['records']['NEW']['successor']='MISSING'
        with self.assertRaisesRegex(SharedError,'SUCCESSOR_MISSING'):knowledge_view(r)
    def test_self_cycle(self):
        r=registry();r['records']['NEW']['successor']='NEW'
        with self.assertRaisesRegex(SharedError,'SUCCESSOR_CYCLE'):knowledge_view(r)
    def test_indirect_cycle(self):
        r=registry();r['records']['NEW']['successor']='OLD'
        with self.assertRaisesRegex(SharedError,'SUCCESSOR_CYCLE'):knowledge_view(r)
    def test_invalidated_not_selected(self):
        v=knowledge_view(registry(),['NEW']);self.assertNotIn('NEW',v['operative']);self.assertIn('NEW',v['blocked'])
    def test_unknown_invalidation(self):
        with self.assertRaisesRegex(SharedError,'UNKNOWN_INVALIDATION'):knowledge_view(registry(),['MISSING'])
    def test_ineffective_without_successor(self):
        r=registry();r['records']['NEW']['effectiveness_status']='INEFFECTIVE';self.assertIn('NEW',knowledge_view(r)['blocked'])
    def test_pending_review_not_operative(self):
        r=registry();r['records']['NEW']['review_status']='PENDING';self.assertNotIn('NEW',knowledge_view(r)['operative'])
    def test_inactive_not_operative(self):
        r=registry();r['records']['NEW']['activation_status']='RETIRED';self.assertNotIn('NEW',knowledge_view(r)['operative'])
    def test_selection_valid(self):
        self.assertTrue(validate_selection(registry(),['NEW'],['NEW'],['NEW'],H,H))
    def test_old_lesson_rejected(self):
        with self.assertRaisesRegex(SharedError,'NONOPERATIVE'):validate_selection(registry(),['OLD'],['OLD'],['OLD'],H,H)
    def test_stale_context(self):
        with self.assertRaisesRegex(SharedError,'STALE_CONTEXT'):validate_selection(registry(),['NEW'],['NEW'],[],H,J)
    def test_unread_lesson(self):
        with self.assertRaisesRegex(SharedError,'MISSING_CONTEXT_ACK'):validate_selection(registry(),['NEW'],[],[],H,H)
    def test_unselected_application(self):
        with self.assertRaisesRegex(SharedError,'UNSELECTED_APPLICATION'):validate_selection(registry(),['NEW'],['NEW','PENDING'],['PENDING'],H,H)
    def test_duplicate_ids(self):
        with self.assertRaisesRegex(SharedError,'KNOWLEDGE_IDS'):validate_selection(registry(),['NEW','NEW'],['NEW'],[],H,H)
    def test_no_new_lesson_allowed(self):
        self.assertTrue(validate_selection(registry(),[],[],[],H,H))
    def test_actor_projection_valid(self):
        self.assertTrue(check_actor_projection(*projection()))
    def test_actor_projection_drift(self):
        s,m,n=projection();s['current_work']['assignee']='CHATGPT'
        with self.assertRaisesRegex(SharedError,'ACTOR_PROJECTION'):check_actor_projection(s,m,n)
    def test_consistent_self_review_rejected(self):
        s,m,n=projection();s['current_work']['assignee']='CHATGPT';m=m.replace('CLAUDE_CODE','CHATGPT');n=n.replace('CLAUDE_CODE','CHATGPT')
        with self.assertRaisesRegex(SharedError,'SELF_ACCEPTANCE'):check_actor_projection(s,m,n)
    def test_return_cursor_drift(self):
        s,m,n=projection();s['current_work']['return_to']='OTHER'
        with self.assertRaisesRegex(SharedError,'RETURN_CURSOR'):check_actor_projection(s,m,n)
    def test_next_cursor_drift(self):
        s,m,n=projection();s['current_work']['next_on_success']='OTHER'
        with self.assertRaisesRegex(SharedError,'NEXT_CURSOR'):check_actor_projection(s,m,n)
    def test_duplicate_assignee(self):
        s,m,n=projection()
        with self.assertRaisesRegex(SharedError,'ACTOR_PROJECTION'):check_actor_projection(s,m,n+'ASSIGNEE: CLAUDE_CODE\n')
    def test_review_write_profile(self):
        s,m,n=projection();s['current_work']['profile']='WSL_IMPLEMENT'
        with self.assertRaisesRegex(SharedError,'REVIEW_PROFILE'):check_actor_projection(s,m,n)
    def test_route_equivalent_for_both_actors(self):
        self.assertEqual(next_action(routing()),next_action(deepcopy(routing())))
    def test_identity_conflict(self):
        self.assertEqual(next_action(routing(identities_match=False)),'RECONCILE_IDENTITIES')
    def test_permission_overrides_ready(self):
        self.assertEqual(next_action(routing(permission_denied=True)),'BLOCKED_PERMISSION')
    def test_design_gap_holds(self):
        self.assertEqual(next_action(routing(design_hold=True)),'APPLICABILITY_HOLD')
    def test_knowledge_reopened_holds(self):
        self.assertEqual(next_action(routing(knowledge_invalidated=True)),'APPLICABILITY_HOLD')
    def test_running_never_relaunch(self):
        self.assertEqual(next_action(routing(transport='RUNNING')),'RECONCILE_EXISTING_ATTEMPT')
    def test_timeout_never_relaunch(self):
        self.assertEqual(next_action(routing(transport='RECONCILE_REQUIRED')),'RECONCILE_EXISTING_ATTEMPT')
    def test_pending_result_before_call(self):
        self.assertEqual(next_action(routing(transport='RESULT_UNREVIEWED',profile_ready=False)),'VERIFY_EXISTING_RESULT')
    def test_stale_result_not_consumed(self):
        self.assertEqual(next_action(routing(transport='RESULT_UNREVIEWED',context_current=False)),'RECONCILE_STALE_CONTEXT')
    def test_complete_without_output(self):
        self.assertEqual(next_action(routing(work_complete=True)),'BLOCKED_MISSING_OUTPUT')
    def test_complete_selects_next(self):
        self.assertEqual(next_action(routing(work_complete=True,output_verified=True)),'SELECT_DECLARED_NEXT')
    def test_missing_profile(self):
        self.assertEqual(next_action(routing(profile_ready=False)),'BLOCKED_CAPABILITY')
    def test_missing_prerequisite(self):
        self.assertEqual(next_action(routing(prerequisites_satisfied=False)),'BLOCKED_PREREQUISITES')
    def test_route_bool_strict(self):
        with self.assertRaisesRegex(SharedError,'ROUTE_BOOL'):next_action(routing(profile_ready=1))
    def test_body_host_hash_verified(self):
        raw,e=seal_static_review(H,J,'CLAUDE_CODE',body(),['R1']);self.assertTrue(verify_report_bytes(raw,e,H,J,'CLAUDE_CODE',['R1']))
    def test_report_self_hash_forbidden(self):
        b=body();b['report_sha256']=H
        with self.assertRaisesRegex(SharedError,'REPORT_SCHEMA'):seal_static_review(H,J,'CLAUDE_CODE',b,['R1'])
    def test_toolless_command_claim(self):
        b=body();b['executed_commands']=['test']
        with self.assertRaisesRegex(SharedError,'STATIC_EXECUTION'):seal_static_review(H,J,'CLAUDE_CODE',b,['R1'])
    def test_pass_missing_required_scope(self):
        b=body();b['covered']=[];b['not_evaluated']=['R1']
        with self.assertRaisesRegex(SharedError,'UNSUPPORTED_PASS'):seal_static_review(H,J,'CLAUDE_CODE',b,['R1'])
    def test_pass_open_high(self):
        b=body();b['findings']=[{'id':'F1','severity':'HIGH','status':'OPEN','evidence':'counterexample'}]
        with self.assertRaisesRegex(SharedError,'UNSUPPORTED_PASS'):seal_static_review(H,J,'CLAUDE_CODE',b,['R1'])
    def test_pass_pending_high(self):
        b=body();b['findings']=[{'id':'F1','severity':'HIGH','status':'FIX_PENDING_REVIEW','evidence':'patch'}]
        with self.assertRaisesRegex(SharedError,'UNSUPPORTED_PASS'):seal_static_review(H,J,'CLAUDE_CODE',b,['R1'])
    def test_incomplete_findings_report_valid(self):
        b=body();b.update(assessment='BLOCKED',covered=[],not_evaluated=['R1']);seal_static_review(H,J,'CLAUDE_CODE',b,['R1'])
    def test_unknown_acceptance_scope(self):
        b=body();b['covered']=['OTHER']
        with self.assertRaisesRegex(SharedError,'COVERAGE_PARTITION'):seal_static_review(H,J,'CLAUDE_CODE',b,['R1'])
    def test_tampered_body(self):
        raw,e=seal_static_review(H,J,'CLAUDE_CODE',body(),['R1'])
        with self.assertRaisesRegex(SharedError,'REPORT_HASH'):verify_report_bytes(raw+b' ',e,H,J,'CLAUDE_CODE',['R1'])
    def test_report_wrong_actor(self):
        raw,e=seal_static_review(H,J,'CLAUDE_CODE',body(),['R1'])
        with self.assertRaisesRegex(SharedError,'REPORT_IDENTITY'):verify_report_bytes(raw,e,H,J,'CHATGPT',['R1'])
    def test_report_old_context(self):
        raw,e=seal_static_review(H,J,'CLAUDE_CODE',body(),['R1'])
        with self.assertRaisesRegex(SharedError,'REPORT_IDENTITY'):verify_report_bytes(raw,e,H,H,'CLAUDE_CODE',['R1'])
    def test_self_promotion_rejected(self):
        raw,e=seal_static_review(H,J,'CLAUDE_CODE',body(),['R1']);e['transport_status']='CONSUMED'
        with self.assertRaisesRegex(SharedError,'REPORT_SELF_PROMOTION'):verify_report_bytes(raw,e,H,J,'CLAUDE_CODE',['R1'])
    def test_disabled_runtime_valid(self):
        self.assertTrue(check_capabilities(caps()))
    def test_connectivity_does_not_activate(self):
        c=caps();c['runtime_enabled']=True;c['connectivity']='PASS'
        with self.assertRaisesRegex(SharedError,'AUTOMATION_NOT_QUALIFIED'):check_capabilities(c)
    def test_bool_capability_status(self):
        c=caps();c['operational_gates']['context_loading']=True
        with self.assertRaisesRegex(SharedError,'CAPABILITY_STATE'):check_capabilities(c)
    def test_measurement_required_for_improvement(self):
        c=caps();c['learning_effectiveness']='MEASURED_SCOPE_ONLY'
        with self.assertRaisesRegex(SharedError,'MEASUREMENT_REQUIRED'):check_capabilities(c)
    def test_scoped_future_measurement_not_banned(self):
        c=caps();c['learning_effectiveness']='MEASURED_SCOPE_ONLY';c['effectiveness_receipt']={'path':'learning/measurements/example.json','sha256':H};self.assertTrue(check_capabilities(c))
    def test_mode_role_mismatch(self):
        s,m,n=projection();s['current_work']['mode']='IMPLEMENTATION'
        with self.assertRaisesRegex(SharedError,'MODE_ROLE_CONFLICT'):check_actor_projection(s,m,n)
    def test_current_invalidation_rejected_at_selection(self):
        with self.assertRaisesRegex(SharedError,'NONOPERATIVE_SELECTION'):validate_selection(registry(),['NEW'],['NEW'],['NEW'],H,H,invalidated_ids=['NEW'])
    def test_nonjson_body_rejected_at_consumption(self):
        from check_shared_workflow import sha
        raw=b'not-json';e={'task_digest':H,'context_digest':J,'actor':'CLAUDE_CODE','report_sha256':sha(raw),'transport_status':'RESULT_UNREVIEWED'}
        with self.assertRaisesRegex(SharedError,'REPORT_INVALID_JSON'):verify_report_bytes(raw,e,H,J,'CLAUDE_CODE',['R1'])
    def test_consumption_rechecks_required_scope(self):
        raw,e=seal_static_review(H,J,'CLAUDE_CODE',body(),['R1'])
        with self.assertRaisesRegex(SharedError,'COVERAGE_PARTITION'):verify_report_bytes(raw,e,H,J,'CLAUDE_CODE',['R1','R2'])
    def test_consumption_rechecks_open_high(self):
        from check_shared_workflow import canonical,sha
        b=body();b['findings']=[{'id':'F1','severity':'HIGH','status':'OPEN','evidence':'current counterexample'}]
        raw=canonical(b);e={'task_digest':H,'context_digest':J,'actor':'CLAUDE_CODE','report_sha256':sha(raw),'transport_status':'RESULT_UNREVIEWED'}
        with self.assertRaisesRegex(SharedError,'UNSUPPORTED_PASS'):verify_report_bytes(raw,e,H,J,'CLAUDE_CODE',['R1'])
    def test_consumption_duplicate_key(self):
        from check_shared_workflow import sha
        raw=b'{"assessment":"PASS","assessment":"BLOCKED"}';e={'task_digest':H,'context_digest':J,'actor':'CLAUDE_CODE','report_sha256':sha(raw),'transport_status':'RESULT_UNREVIEWED'}
        with self.assertRaisesRegex(SharedError,'REPORT_DUPLICATE_KEY'):verify_report_bytes(raw,e,H,J,'CLAUDE_CODE',['R1'])
    def test_repository_view_has_no_fixed_population(self):
        p=Path(__file__).resolve().parents[1]/'learning/LEARNING_STATE.json'
        r=json.loads(p.read_text());v=knowledge_view(r)
        expected={k for k,x in r['records'].items() if x.get('successor') is None and x.get('activation_status')=='ACTIVE' and x.get('review_status')=='PASS' and x.get('effectiveness_status') in {'EFFECTIVE','PENDING_MEASUREMENT','NOT_MEASURED'}}
        self.assertEqual(set(v['operative']),expected)
        self.assertEqual(set(v['warnings']),set(r['records'])-expected)

if __name__=='__main__':unittest.main(verbosity=2)
