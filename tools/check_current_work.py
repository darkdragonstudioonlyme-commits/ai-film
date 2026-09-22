#!/usr/bin/env python3
"""Bound current-work projections and audit scope; not product/native validation."""
from __future__ import annotations
import json
from pathlib import Path
import re
import sys
from check_state_contract import load_selected_state, StateContractError

ACTIVE = {'READY', 'RUNNING', 'WIP', 'REVIEWING', 'HANDED_OFF'}
STATES = ACTIVE | {'BLOCKED', 'WAITING_INPUT', 'FAILED', 'COMPLETE'}
HEX40 = re.compile(r'[0-9a-f]{40}')


def scalar(text: str, name: str) -> str | None:
    values = re.findall(r'^' + re.escape(name) + r':[ \t]*(.*)$', text, re.M)
    if len(values) != 1:
        return None
    return values[0].strip().strip('"')


def check_projection(state: dict, md: str, nxt: str) -> list[str]:
    errors = []
    work = state.get('current_work')
    if not isinstance(work, dict):
        return ['current-work-missing']
    required = ('work_item', 'mode', 'status', 'parent_run_id', 'baseline_source_commit')
    if any(not isinstance(work.get(k), str) or not work[k] for k in required):
        return ['current-work-schema']
    for field, mdname, nwname in (('work_item', 'CURRENT_TASK', 'WORK_ITEM'),
                                 ('mode', 'CURRENT_MODE', 'MODE'),
                                 ('status', 'CURRENT_WORK_STATUS', 'STATUS')):
        if not (work[field] == scalar(md, mdname) == scalar(nxt, nwname)):
            errors.append('current-work-parity:' + field)
    if state.get('current_task', work['work_item']) != work['work_item']:
        errors.append('current-task-machine-parity')
    if work['mode'] != state.get('current_mode'):
        errors.append('current-mode-machine-parity')
    if work['status'] not in STATES:
        errors.append('current-work-status')
    parent = state.get('active_run', {})
    if not (work['parent_run_id'] == parent.get('run_id') == scalar(nxt, 'RUN_ID')):
        errors.append('current-work-parent')
    candidate = state.get('accepted_code_candidate', {})
    if work['baseline_source_commit'] != candidate.get('source_commit'):
        errors.append('current-work-baseline')
    if state.get('readiness_scope') != 'ACCEPTED_CODE_CANDIDATE' or scalar(md, 'READINESS_SCOPE') != 'ACCEPTED_CODE_CANDIDATE':
        errors.append('readiness-scope')
    for key in ('author_complete', 'code_review_handoff_ready', 'code_review_pass'):
        if type(work.get(key)) is not bool:
            errors.append('current-work-readiness-type:' + key)
        elif work[key]:
            if not HEX40.fullmatch(str(work.get('candidate_source_commit', ''))):
                errors.append('current-work-readiness-without-candidate:' + key)
            evidence = work.get('readiness_evidence', {})
            if not isinstance(evidence, dict) or not evidence.get(key):
                errors.append('current-work-readiness-without-evidence:' + key)
    # These are legacy duplicate current-work holders, not arbitrary backlog records.
    prior = [state.get('test_design', {}), state.get('validation', {}).get('binding_producer_implementation_target', {})]
    for item in prior:
        if not isinstance(item, dict):
            continue
        name = item.get('work_item', item.get('work_item_id'))
        if name and name != work['work_item'] and item.get('status') in ACTIVE:
            errors.append('superseded-work-still-actionable:' + name)
    return errors


def check_audit_scope(receipt: dict) -> list[str]:
    if not isinstance(receipt, dict):
        return ['audit-receipt-not-object']
    errors = []
    if type(receipt.get('schema_version')) is not int or receipt.get('schema_version') != 1 or receipt.get('population_kind') != 'EXACT_REPOSITORY_BOUNDARIES':
        errors.append('audit-receipt-schema')
    if receipt.get('session_denominator') is not None:
        errors.append('unmeasured-session-denominator')
    if receipt.get('improvement_status') != 'IMPROVEMENT_NOT_PROVEN':
        errors.append('unproven-global-improvement')
    for key in ('historical_semantic_review_complete', 'native_revalidated', 'historical_sessions_reconstructed'):
        if receipt.get(key) is not False:
            errors.append('audit-scope-overclaim:' + key)
    for key in ('main_commits_in_window', 'active_control_documents_read'):
        if type(receipt.get(key)) is not int or receipt[key] < 0:
            errors.append('audit-count-type:' + key)
    refs = receipt.get('input_refs')
    if not isinstance(refs, dict) or not refs or any(not HEX40.fullmatch(str(x)) for x in refs.values()):
        errors.append('audit-input-identity')
    return errors


def check_test_targets(root: Path) -> list[str]:
    """Support actual recorded field spellings; local targets must resolve exactly.

    Historic records without a target field are outside this structural predicate.
    This deliberately does not claim to authenticate prose or remote-only evidence.
    """
    errors = []
    aliases = {'change': ('TEST_CHANGE_ID', 'TARGET_TEST_CHANGE', 'TARGET_TEST_CHANGE_ID'),
               'gap': ('TEST_GAP_ID', 'TARGET_TEST_GAP', 'TARGET_TEST_GAP_ID')}
    for path in sorted((root / 'test-governance').glob('TEST_REVIEW-*.md')):
        text = path.read_text(encoding='utf-8')
        for kind, names in aliases.items():
            targets = [scalar(text, x) for x in names if re.search(r'^' + x + r':', text, re.M)]
            if not targets:
                continue
            if any(not x for x in targets) or len(set(targets)) != 1:
                errors.append('test-target-ambiguous:' + path.name)
                continue
            target = targets[0]
            prefix = 'TEST_CHANGE-' if kind == 'change' else 'TEST_GAP-'
            if not re.fullmatch(re.escape(prefix) + r'[A-Za-z0-9_-]+', target):
                errors.append('test-target-invalid:' + path.name)
            elif not (root / 'test-governance' / (target + '.md')).is_file():
                errors.append('test-target-unresolved:' + path.name + ':' + target)
    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    try:
        _, _, state = load_selected_state(root)
        errors = check_projection(state, (root/'PROJECT_STATE.md').read_text(), (root/'NEXT_WORK_ITEM.md').read_text())
        rel = state.get('current_work', {}).get('audit_receipt')
        if not isinstance(rel, str) or Path(rel).is_absolute() or '..' in Path(rel).parts:
            errors.append('audit-receipt-path')
        else:
            path = root / rel
            if path.is_symlink() or not path.is_file():
                errors.append('audit-receipt-unavailable')
            else:
                errors += check_audit_scope(json.loads(path.read_text()))
        errors += check_test_targets(root)
    except (StateContractError, OSError, ValueError, TypeError) as exc:
        errors = ['current-work-unreadable:' + type(exc).__name__]
    if errors:
        print('CURRENT_WORK_CHECK_FAIL\n' + '\n'.join(errors))
        return 1
    print('CURRENT_WORK_CHECK_PASS scope=ROUTING_PROJECTION_AND_AUDIT_DECLARATIONS native=NOT_EVALUATED effectiveness=NOT_PROVEN')
    return 0


if __name__ == '__main__':
    sys.exit(main())
