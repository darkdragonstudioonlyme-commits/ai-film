#!/usr/bin/env python3
"""Synthetic no-execution tests; not real dispatch, model review or sandbox proof."""
from copy import deepcopy
import unittest
from check_dual_ai_contract import (ContractError, digest, validate_task, validate_result,
                                    idempotency_key, next_transport_state, validate_capability_declaration)


def task():
    return {'schema_version': 1, 'task_id': 'DEMO-001', 'parent_run_id': 'RUN-DEMO',
            'work_item': 'REVIEW-DEMO', 'role': 'REVIEW', 'author_actor': 'CHATGPT',
            'actor': 'CLAUDE_CODE', 'consumer_actor': 'CHATGPT', 'profile': 'TEXT_REVIEW',
            'control_commit': 'a'*40, 'source_commit': 'b'*40,
            'input_files': [{'path': 'SELF_LEARNING.md', 'commit': 'a'*40, 'sha256': 'c'*64},
                            {'path': 'learning/LEARNING_STATE.json', 'commit': 'a'*40, 'sha256': 'd'*64},
                            {'path': 'learning/LEARNING-DEMO.md', 'commit': 'a'*40, 'sha256': 'e'*64}],
            'knowledge': {'register_sha256': 'd'*64, 'policy_sha256': 'c'*64,
                          'required_learning_ids': ['LEARNING-DEMO'],
                          'record_refs': {'LEARNING-DEMO': {'path': 'learning/LEARNING-DEMO.md', 'sha256': 'e'*64}}},
            'permissions': {'native': False, 'signing': False, 'publish': False, 'escalate': False},
            'limits': {'max_turns': 4, 'max_seconds': 300, 'max_input_bytes': 10000,
                       'max_output_bytes': 10000, 'max_cost_usd': None},
            'output_scope': {'worktree_rel': 'worktrees/review-demo', 'files_allowed': []},
            'return_to': 'RUN-DEMO/STEP', 'acceptance': ['Check identity and known findings']}


def result(t):
    return {'task_digest': digest(t), 'actor': 'CLAUDE_CODE', 'transport_status': 'RESULT_UNREVIEWED',
            'assessment': 'FINDINGS', 'execution_scope': 'STATIC_ONLY', 'executed_commands': [],
            'knowledge_read_ids': ['LEARNING-DEMO'],
            'learning': {'disposition': 'REUSE_EXISTING', 'applied_ids': ['LEARNING-DEMO'],
                         'proposals': [], 'effectiveness_claim': 'NOT_PROVEN'},
            'output_identity': {'report_sha256': 'e'*64}}


class HandoffTests(unittest.TestCase):
    def test_register_summary_is_not_record_read(self):
        t=task();r=result(t);r['knowledge_read_ids'].append('LEARNING-NOT-SUPPLIED')
        with self.assertRaisesRegex(ContractError,'UNSUPPLIED_KNOWLEDGE_READ_CLAIM'):
            validate_result(t,r)
    def test_valid_task_and_result(self):
        t=task();self.assertEqual(len(validate_task(t)),64);self.assertTrue(validate_result(t,result(t)))
    def test_stable_digest(self):
        t=task();self.assertEqual(idempotency_key(t),idempotency_key(deepcopy(t)))
    def test_new_acceptance_new_identity(self):
        t=task();u=deepcopy(t);u['acceptance'].append('Check newly discovered recurrence')
        self.assertNotEqual(idempotency_key(t),idempotency_key(u))
    def test_author_assignment(self):
        t=task();t.update(role='AUTHOR',profile='WSL_IMPLEMENT',author_actor='CLAUDE_CODE')
        t['output_scope']['files_allowed']=['src/example.py']
        validate_task(t)
    def test_no_new_learning_valid(self):
        t=task();r=result(t);r['learning'].update(disposition='NO_NEW_LEARNING',applied_ids=[])
        self.assertTrue(validate_result(t,r))
    def test_default_capability_blocks(self):
        with self.assertRaises(ContractError):next_transport_state('PREPARED','admit')
    def test_requires_writer_lock(self):
        with self.assertRaises(ContractError):next_transport_state('READY','start',ready=True)
    def test_model_happy_path(self):
        s=next_transport_state('PREPARED','admit',ready=True)
        s=next_transport_state(s,'start',ready=True,locked=True)
        s=next_transport_state(s,'recover_result',verified=True)
        s=next_transport_state(s,'non_author_accept',verified=True)
        self.assertEqual(next_transport_state(s,'consume',verified=True),'CONSUMED')
    def test_timeout_no_relaunch(self):
        s=next_transport_state('RUNNING','interrupted')
        with self.assertRaises(ContractError):next_transport_state(s,'start',ready=True,locked=True)
    def test_reconcile_reuses_result(self):
        self.assertEqual(next_transport_state('RECONCILE_REQUIRED','recover_result',verified=True),'RESULT_UNREVIEWED')
    def test_duplicate_consumption_forbidden(self):
        with self.assertRaises(ContractError):next_transport_state('CONSUMED','start',ready=True,locked=True)
    def test_self_review_event_forbidden(self):
        with self.assertRaises(ContractError):next_transport_state('RESULT_UNREVIEWED','self_accept',verified=True)


def bad_task(path,value):
    def run(self):
        t=task();x=t
        for p in path[:-1]:x=x[p]
        x[path[-1]]=value
        with self.assertRaises(ContractError):validate_task(t)
    return run

for name,path,value in [
 ('version_bool',['schema_version'],True),('version_unknown',['schema_version'],2),
 ('self_review',['actor'],'CHATGPT'),('unknown_actor',['actor'],'OTHER'),
 ('raw_command_field',['command'],'echo unsafe'),('unbounded_turns',['limits','max_turns'],0),
 ('bool_turns',['limits','max_turns'],True),('negative_cost',['limits','max_cost_usd'],-1),
 ('nan_cost',['limits','max_cost_usd'],float('nan')),('bool_cost',['limits','max_cost_usd'],True),
 ('unbounded_time',['limits','max_seconds'],999999),('floating_ref',['control_commit'],'main'),
 ('traversal',['input_files',0,'path'],'../key'),('private_path',['input_files',0,'path'],'.env'),
 ('git_path',['input_files',0,'path'],'.git/config'),('shell_path',['input_files',0,'path'],'docs/x\nsh'),
 ('glob_path',['input_files',0,'path'],'docs/*.md'),('native_permission',['permissions','native'],True),
 ('sign_permission',['permissions','signing'],True),('publish_permission',['permissions','publish'],True),
 ('escalate_permission',['permissions','escalate'],True),('permission_bool',['permissions','native'],0),
 ('stale_register',['knowledge','register_sha256'],'f'*64),('empty_acceptance',['acceptance'],[]),
 ('duplicate_learning',['knowledge','required_learning_ids'],['X','X']),
 ('missing_knowledge',['input_files'],[]),('unknown_profile',['profile'],'UNRESTRICTED')]:
    setattr(HandoffTests,'test_reject_'+name,bad_task(path,value))


def bad_result(path,value):
    def run(self):
        t=task();r=result(t);x=r
        for p in path[:-1]:x=x[p]
        x[path[-1]]=value
        with self.assertRaises(ContractError):validate_result(t,r)
    return run

for name,path,value in [
 ('foreign_task',['task_digest'],'f'*64),('false_actor',['actor'],'CHATGPT'),
 ('self_promote',['transport_status'],'CONSUMED'),('invented_tests',['executed_commands'],['pytest']),
 ('false_execution',['execution_scope'],'COMMAND_EVIDENCE'),('missing_lesson',['knowledge_read_ids'],[]),
 ('unread_application',['learning','applied_ids'],['UNKNOWN']),
 ('self_effective',['learning','effectiveness_claim'],'EFFECTIVE'),('missing_output',['output_identity'],{})]:
    setattr(HandoffTests,'test_result_reject_'+name,bad_result(path,value))

def source_identity_key(self):
    t=task();u=deepcopy(t);u['source_commit']='f'*40
    self.assertNotEqual(idempotency_key(t),idempotency_key(u))
HandoffTests.test_source_identity_changes_key=source_identity_key
HandoffTests.test_undeclared_input_base=bad_task(['input_files',0,'commit'],'f'*40)
HandoffTests.test_invalid_output_hash=bad_result(['output_identity'],{'report_sha256':'PASS'})
HandoffTests.test_unknown_output_identity=bad_result(['output_identity'],{'approved':True})
HandoffTests.test_missing_new_proposal=bad_result(['learning','disposition'],'PROPOSE_NEW')

def reject_self_activated_proposal(self):
    t=task();r=result(t);r['learning'].update(disposition='PROPOSE_NEW',proposals=[{
        'id':'LESSON-NEW','summary':'Synthetic','evidence_sha256':'f'*64,
        'metric':'next real eligible sample','status':'ACTIVE'}])
    with self.assertRaises(ContractError):validate_result(t,r)
HandoffTests.test_reject_self_activated_proposal=reject_self_activated_proposal

class CapabilityTests(unittest.TestCase):
    def test_disabled_unavailable_is_honest(self):
        self.assertTrue(validate_capability_declaration({'runtime_enabled':False,'cross_model_acceptance':'NOT_RUN'}))
    def test_boolean_runtime_required(self):
        with self.assertRaises(ContractError):validate_capability_declaration({'runtime_enabled':1,'cross_model_acceptance':'NOT_RUN'})
    def test_false_cross_model_pass(self):
        with self.assertRaises(ContractError):validate_capability_declaration({'runtime_enabled':False,'cross_model_acceptance':'PASS'})
    def test_activation_without_acceptance(self):
        with self.assertRaises(ContractError):validate_capability_declaration({'runtime_enabled':True,'cross_model_acceptance':'NOT_RUN'})
    def test_self_review_cannot_activate(self):
        with self.assertRaises(ContractError):validate_capability_declaration({
            'runtime_enabled':True,'cross_model_acceptance':'PASS',
            'cross_model_review':{'author_actor':'CHATGPT','reviewer_actor':'CHATGPT',
                                 'target_commit':'a'*40,'record_sha256':'c'*64}})

HandoffTests.test_numeric_policy_hash=bad_task(['knowledge','policy_sha256'],int('1'*64))
HandoffTests.test_numeric_file_hash=bad_task(['input_files',2,'sha256'],int('1'*64))
HandoffTests.test_missing_output_scope=bad_task(['output_scope'],{})
HandoffTests.test_review_cannot_write=bad_task(['output_scope','files_allowed'],['README.md'])
HandoffTests.test_missing_lesson_record=bad_task(['knowledge','record_refs'],{})
HandoffTests.test_changed_lesson_bytes=bad_task(['knowledge','record_refs','LEARNING-DEMO','sha256'],'f'*64)
HandoffTests.test_unsafe_writer_worktree=bad_task(['output_scope','worktree_rel'],'../other')
HandoffTests.test_role_type=bad_task(['role'],[])
HandoffTests.test_profile_type=bad_task(['profile'],{})

def empty_author_scope(self):
    t=task();t.update(role='AUTHOR',profile='WSL_IMPLEMENT',author_actor='CLAUDE_CODE')
    with self.assertRaises(ContractError):validate_task(t)
HandoffTests.test_author_needs_write_scope=empty_author_scope

HandoffTests.test_attempt_is_transport_not_task=bad_task(['attempt'],2)

if __name__=='__main__':unittest.main(verbosity=2)
