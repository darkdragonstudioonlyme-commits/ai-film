#!/usr/bin/env python3
"""Pure handoff contract/reference model. Never launches an agent or grants authority.

A valid capsule/capability declaration is only schema/model evidence. Real dispatcher
activation must independently authenticate policy, process isolation and account data.
"""
from __future__ import annotations
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import re
import sys
from check_state_contract import load_selected_state

ACTORS = {'CHATGPT', 'CLAUDE_CODE'}
PROFILES = {'TEXT_REVIEW', 'WSL_IMPLEMENT'}
HEX40 = re.compile(r'[0-9a-f]{40}')
HEX64 = re.compile(r'[0-9a-f]{64}')
TOKEN = re.compile(r'[A-Z][A-Z0-9_-]{0,100}')
REQUIRED_KNOWLEDGE_FILES = {'SELF_LEARNING.md', 'learning/LEARNING_STATE.json'}


class ContractError(ValueError):
    pass


def require(condition, reason):
    if not condition:
        raise ContractError(reason)


def exact_keys(value, names, reason):
    require(type(value) is dict and set(value) == set(names), reason)


def integer(value, minimum, maximum, reason):
    require(type(value) is int and minimum <= value <= maximum, reason)


def text(value, reason):
    require(type(value) is str and bool(value.strip()), reason)


def unique_strings(value, reason):
    require(type(value) is list and all(type(v) is str and v for v in value), reason)
    require(len(value) == len(set(value)), reason)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode('utf-8')


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def relative_path(value):
    text(value, 'PATH_SCHEMA')
    p = PurePosixPath(value)
    require(not p.is_absolute() and '..' not in p.parts and '\\' not in value
            and not any(c in value for c in '\x00\r\n*?[]'), 'PATH_SCOPE')
    require(str(p) == value and value not in ('.', ''), 'PATH_CANONICAL')
    require(not any(part in {'.git', '.ssh', '.env', 'local-authority', 'credentials'}
                    or part.startswith('.env.') for part in p.parts), 'SENSITIVE_PATH')
    return value


def validate_task(t):
    fields = {'schema_version', 'task_id', 'parent_run_id', 'work_item', 'role',
              'author_actor', 'actor', 'consumer_actor', 'profile',
              'control_commit', 'source_commit', 'input_files', 'knowledge',
              'permissions', 'limits', 'return_to', 'acceptance', 'output_scope'}
    exact_keys(t, fields, 'TASK_SCHEMA')
    require(type(t['schema_version']) is int and t['schema_version'] == 1, 'TASK_VERSION')
    for name in ('task_id', 'parent_run_id', 'work_item'):
        require(type(t[name]) is str and TOKEN.fullmatch(t[name]), 'TASK_ID')
    require(type(t['role']) is str and t['role'] in {'AUTHOR', 'REVIEW', 'AUDIT'}, 'TASK_ROLE')
    require(type(t['profile']) is str and t['profile'] in PROFILES, 'TASK_PROFILE')
    for name in ('author_actor', 'actor', 'consumer_actor'):
        require(type(t[name]) is str and t[name] in ACTORS, 'TASK_ACTOR')
    if t['role'] in {'REVIEW', 'AUDIT'}:
        require(t['actor'] != t['author_actor'], 'SELF_ACCEPTANCE')
    else:
        require(t['actor'] == t['author_actor'] and t['consumer_actor'] != t['actor'],
                'AUTHOR_REVIEWER_SCOPE')
    require(t['profile'] != 'TEXT_REVIEW' or t['role'] in {'REVIEW', 'AUDIT'},
            'TEXT_PROFILE_AUTHORING')
    scope = t['output_scope']
    exact_keys(scope, {'worktree_rel', 'files_allowed'}, 'OUTPUT_SCOPE_SCHEMA')
    relative_path(scope['worktree_rel'])
    unique_strings(scope['files_allowed'], 'WRITE_SCOPE_SCHEMA')
    for path in scope['files_allowed']:
        relative_path(path)
    if t['profile'] == 'TEXT_REVIEW':
        require(scope['files_allowed'] == [], 'REVIEW_WRITE_FORBIDDEN')
    else:
        require(t['role'] == 'AUTHOR' and bool(scope['files_allowed']), 'WRITER_SCOPE_REQUIRED')
    for name in ('control_commit', 'source_commit'):
        require(type(t[name]) is str and HEX40.fullmatch(t[name]), 'INPUT_COMMIT')
    exact_keys(t['permissions'], {'native', 'signing', 'publish', 'escalate'}, 'PERMISSION_SCHEMA')
    require(all(v is False for v in t['permissions'].values()), 'PERMISSION_ESCALATION')
    files = t['input_files']
    require(type(files) is list and files, 'INPUT_FILES')
    seen = set()
    for row in files:
        exact_keys(row, {'path', 'commit', 'sha256'}, 'INPUT_FILE_SCHEMA')
        relative_path(row['path'])
        require(type(row['commit']) is str and HEX40.fullmatch(row['commit']) and type(row['sha256']) is str and HEX64.fullmatch(row['sha256']),
                'INPUT_FILE_IDENTITY')
        require(row['commit'] in {t['control_commit'], t['source_commit']}, 'UNDECLARED_INPUT_BASE')
        key = (row['commit'], row['path'])
        require(key not in seen, 'INPUT_FILE_DUPLICATE')
        seen.add(key)
    k = t['knowledge']
    exact_keys(k, {'register_sha256', 'policy_sha256', 'required_learning_ids', 'record_refs'}, 'KNOWLEDGE_SCHEMA')
    require(type(k['register_sha256']) is str and HEX64.fullmatch(k['register_sha256']) and type(k['policy_sha256']) is str and HEX64.fullmatch(k['policy_sha256']),
            'KNOWLEDGE_IDENTITY')
    unique_strings(k['required_learning_ids'], 'KNOWLEDGE_IDS')
    for filename in REQUIRED_KNOWLEDGE_FILES:
        matches = [r for r in files if r['path'] == filename and r['commit'] == t['control_commit']]
        require(len(matches) == 1, 'KNOWLEDGE_INPUT_MISSING')
        expected = k['register_sha256'] if filename.endswith('.json') else k['policy_sha256']
        require(matches[0]['sha256'] == expected, 'KNOWLEDGE_INPUT_DRIFT')
    require(type(k['record_refs']) is dict and set(k['record_refs']) == set(k['required_learning_ids']),
            'LEARNING_RECORD_COVERAGE')
    for lesson, record in k['record_refs'].items():
        exact_keys(record, {'path', 'sha256'}, 'LEARNING_RECORD_SCHEMA')
        relative_path(record['path'])
        require(record['path'].startswith('learning/') and record['path'].endswith('.md'),
                'LEARNING_RECORD_PATH')
        require(type(record['sha256']) is str and HEX64.fullmatch(record['sha256']), 'LEARNING_RECORD_HASH')
        require(any(r['commit'] == t['control_commit'] and r['path'] == record['path']
                    and r['sha256'] == record['sha256'] for r in files), 'LEARNING_BYTES_NOT_IN_PACKET')
    limits = t['limits']
    exact_keys(limits, {'max_turns', 'max_seconds', 'max_input_bytes', 'max_output_bytes',
                        'max_cost_usd'}, 'LIMIT_SCHEMA')
    for name, maximum in [('max_turns', 100), ('max_seconds', 3600),
                          ('max_input_bytes', 1048576), ('max_output_bytes', 1048576)]:
        integer(limits[name], 1, maximum, 'LIMIT_INTEGER')
    cost = limits['max_cost_usd']
    require(cost is None or type(cost) in (float, int) and math.isfinite(cost) and cost > 0,
            'BUDGET_SCHEMA')
    text(t['return_to'], 'RETURN_PATH')
    unique_strings(t['acceptance'], 'ACCEPTANCE_SCHEMA')
    require(t['acceptance'], 'ACCEPTANCE_EMPTY')
    return digest(t)


def idempotency_key(t):
    validate_task(t)
    # Capsule has no attempt/time/digest fields; all allowed fields affect identity.
    return digest({'domain': 'DUAL_AI_TASK_IDEMPOTENCY_V1', 'task': t})


def validate_result(t, r):
    target = validate_task(t)
    exact_keys(r, {'task_digest', 'actor', 'transport_status', 'assessment', 'execution_scope',
                   'executed_commands', 'knowledge_read_ids', 'learning', 'output_identity'},
               'RESULT_SCHEMA')
    require(r['task_digest'] == target and r['actor'] == t['actor'], 'RESULT_INPUT_DRIFT')
    require(r['transport_status'] == 'RESULT_UNREVIEWED', 'RESULT_SELF_PROMOTION')
    require(r['assessment'] in {'PASS', 'FINDINGS', 'BLOCKED', 'NOT_EVALUATED'}, 'ASSESSMENT_SCHEMA')
    require(r['execution_scope'] in {'STATIC_ONLY', 'COMMAND_EVIDENCE'}, 'EXECUTION_SCOPE')
    require(type(r['executed_commands']) is list, 'COMMAND_SCHEMA')
    if t['profile'] == 'TEXT_REVIEW':
        require(r['execution_scope'] == 'STATIC_ONLY' and r['executed_commands'] == [],
                'TEXT_REVIEW_EXECUTION_OVERCLAIM')
    unique_strings(r['knowledge_read_ids'], 'READ_KNOWLEDGE_IDS')
    require(set(r['knowledge_read_ids']) <= set(t['knowledge']['record_refs']),
            'UNSUPPLIED_KNOWLEDGE_READ_CLAIM')
    require(set(t['knowledge']['required_learning_ids']) <= set(r['knowledge_read_ids']),
            'REQUIRED_LEARNING_NOT_REPORTED')
    learn = r['learning']
    exact_keys(learn, {'disposition', 'applied_ids', 'proposals', 'effectiveness_claim'}, 'LEARNING_SCHEMA')
    require(learn['disposition'] in {'NO_NEW_LEARNING', 'REUSE_EXISTING', 'PROPOSE_NEW', 'REOPEN'},
            'LEARNING_DISPOSITION')
    unique_strings(learn['applied_ids'], 'APPLIED_IDS')
    require(set(learn['applied_ids']) <= set(r['knowledge_read_ids']), 'UNREAD_LEARNING_CLAIM')
    require(type(learn['proposals']) is list and learn['effectiveness_claim'] == 'NOT_PROVEN',
            'SELF_EFFECTIVENESS')
    require(learn['disposition'] != 'NO_NEW_LEARNING' or learn['proposals'] == [],
            'LEARNING_DISPOSITION_CONFLICT')
    require(type(r['output_identity']) is dict and r['output_identity'], 'OUTPUT_IDENTITY_MISSING')
    for kind, ref in r['output_identity'].items():
        require(kind in {'commit', 'tree', 'report_sha256', 'patch_sha256'}, 'OUTPUT_IDENTITY_KIND')
        pattern = HEX40 if kind in {'commit', 'tree'} else HEX64
        require(type(ref) is str and pattern.fullmatch(ref), 'OUTPUT_IDENTITY_HASH')
    for proposal in learn['proposals']:
        exact_keys(proposal, {'id', 'summary', 'evidence_sha256', 'metric', 'status'}, 'PROPOSAL_SCHEMA')
        require(proposal['status'] == 'PROPOSED_REVIEW_REQUIRED', 'PROPOSAL_SELF_ACTIVATION')
        require(type(proposal['evidence_sha256']) is str and HEX64.fullmatch(proposal['evidence_sha256']), 'PROPOSAL_EVIDENCE')
        for field in ('id', 'summary', 'metric'):
            text(proposal[field], 'PROPOSAL_CONTENT')
    if learn['disposition'] in {'NO_NEW_LEARNING', 'REUSE_EXISTING'}:
        require(learn['proposals'] == [], 'LEARNING_DISPOSITION_CONFLICT')
    if learn['disposition'] == 'PROPOSE_NEW':
        require(bool(learn['proposals']), 'LEARNING_PROPOSAL_MISSING')
    return True


def next_transport_state(state, event, *, ready=False, locked=False, verified=False):
    # Pure model booleans, NOT authentication or real runtime proof.
    table = {('PREPARED', 'capability_missing'): 'BLOCKED_CAPABILITY',
             ('PREPARED', 'permission_denied'): 'BLOCKED_PERMISSION',
             ('RUNNING', 'interrupted'): 'RECONCILE_REQUIRED',
             ('RUNNING', 'failed'): 'FAILED'}
    if (state, event) in table:
        return table[(state, event)]
    if state in {'PREPARED', 'BLOCKED_CAPABILITY', 'BLOCKED_PERMISSION'} and event == 'admit':
        require(ready is True, 'NOT_READY'); return 'READY'
    if state == 'READY' and event == 'start':
        require(locked is True and ready is True, 'WRITER_OR_CAPABILITY_MISSING'); return 'RUNNING'
    if state in {'RUNNING', 'RECONCILE_REQUIRED'} and event == 'recover_result':
        require(verified is True, 'RESULT_NOT_VERIFIED'); return 'RESULT_UNREVIEWED'
    if state == 'RESULT_UNREVIEWED' and event == 'non_author_accept':
        require(verified is True, 'REVIEW_NOT_VERIFIED'); return 'REVIEWED'
    if state == 'REVIEWED' and event == 'consume':
        require(verified is True, 'CONSUMPTION_NOT_VERIFIED'); return 'CONSUMED'
    raise ContractError('TRANSITION_FORBIDDEN')


def validate_capability_declaration(c):
    require(type(c) is dict and type(c.get('runtime_enabled')) is bool, 'RUNTIME_FLAG')
    require(c.get('cross_model_acceptance') in {'NOT_RUN', 'PASS', 'FAIL'}, 'CROSS_MODEL_STATUS')
    if c['cross_model_acceptance'] == 'PASS':
        review = c.get('cross_model_review')
        require(type(review) is dict and review.get('author_actor') in ACTORS
                and review.get('reviewer_actor') in ACTORS
                and review['author_actor'] != review['reviewer_actor']
                and type(review.get('target_commit')) is str and HEX40.fullmatch(review['target_commit'])
                and type(review.get('record_sha256')) is str and HEX64.fullmatch(review['record_sha256']), 'CROSS_MODEL_EVIDENCE')
    if c['runtime_enabled']:
        require(c.get('cross_model_acceptance') == 'PASS' and c.get('capability_status') == 'READY',
                'UNACCEPTED_RUNTIME')
        require(all(c.get(k) is True for k in ('auth_verified', 'budget_authorized', 'deployment_verified')),
                'ACTIVATION_PREREQUISITE')
        e = c.get('activation_evidence')
        require(type(e) is dict and set(e) == {'path', 'sha256'}
                and type(e['sha256']) is str and HEX64.fullmatch(e['sha256']), 'ACTIVATION_EVIDENCE')
    return True


def main():
    root = Path(__file__).resolve().parents[1]
    _, _, state = load_selected_state(root)
    c = state.get('collaboration', {})
    require(c.get('learning_register') == 'learning/LEARNING_STATE.json', 'REGISTER_OWNER')
    validate_capability_declaration(c)
    from check_current_work import scalar
    md = (root/'PROJECT_STATE.md').read_text()
    for field, name in [('status', 'COLLABORATION_STATUS'), ('coordinator', 'COORDINATOR'),
                        ('worker', 'WORKER'), ('learning_register', 'SHARED_LEARNING_REGISTER'),
                        ('automatic_handoff', 'AUTOMATIC_HANDOFF'),
                        ('capability_status', 'CLAUDE_CAPABILITY_STATUS'),
                        ('cross_model_acceptance', 'CROSS_MODEL_ACCEPTANCE')]:
        require(c.get(field) == scalar(md, name), 'CAPABILITY_PROJECTION_DRIFT')
    require(scalar(md, 'COLLABORATION_RUNTIME_ENABLED') == str(c['runtime_enabled']).lower(),
            'RUNTIME_PROJECTION_DRIFT')
    if c['runtime_enabled']:
        evidence = c['activation_evidence']
        relative_path(evidence['path'])
        ep = root / evidence['path']
        require(ep.is_file() and not ep.is_symlink(), 'ACTIVATION_EVIDENCE_UNAVAILABLE')
        require(hashlib.sha256(ep.read_bytes()).hexdigest() == evidence['sha256'],
                'ACTIVATION_EVIDENCE_HASH')
    for name in ('CLAUDE.md', 'docs/DUAL_AI_COLLABORATION.md', 'docs/DUAL_AI_AUTOMATIC_HANDOFF.md'):
        require((root/name).is_file(), 'DESIGN_FILE_MISSING')
    print('DUAL_AI_CONTRACT_PASS scope=DECLARATIONS_ONLY runtime_verified=NOT_EVALUATED cross_model_verified=NOT_EVALUATED learning=NOT_PROVEN')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ContractError, ValueError, OSError) as e:
        print('DUAL_AI_CONTRACT_FAIL', str(e)); sys.exit(1)
