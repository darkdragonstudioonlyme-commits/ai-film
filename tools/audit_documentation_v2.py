#!/usr/bin/env python3
from pathlib import Path
import re,sys,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
active=['README.md','PROJECT_STATE.md','NEXT_WORK_ITEM.md','PROJECT_ROADMAP.md','WORKFLOW_ROUTER.md','EXECUTION_LANES.md',
'DOCUMENTATION_MAP.md','PROJECT_MEMORY.md','SELF_LEARNING.md','TEST_STRATEGY.md','WORKFLOW_HEALTH.md','POLICY_REGISTRY.md',
'SERVER_ENVIRONMENT.md','MODEL_EVALUATION.md','RECOVERY_PLAYBOOK.md','OPERATING_ARCHITECTURE.md','GIT_WORKFLOW.md','WORKSPACE_WSL.md','CHAT_HANDOFF.md','WORKFLOW_CONTINUITY.md']
errors=[]; texts={p:(ROOT/p).read_text(encoding='utf-8') for p in active if (ROOT/p).is_file()}
# No mutable delivery versions in standing policy/bootstrap docs.
allow_version={'PROJECT_STATE.md','NEXT_WORK_ITEM.md','SERVER_ENVIRONMENT.md','PROJECT_ROADMAP.md','PROJECT_MEMORY.md'}
for p,t in texts.items():
    if p not in allow_version and re.search(r'0\.1\.0\.dev\d+',t): errors.append('stale-version-risk:'+p)
workspace=texts.get('WORKSPACE_WSL.md','')
if re.search(r'0\.1\.0\.dev\d+',workspace): errors.append('workspace-mutable-version')
if re.search(r'\b[0-9a-f]{40}\b',workspace): errors.append('workspace-source-commit-pin')
if re.search(r'\b\d+ PASS\b',workspace): errors.append('workspace-test-count-pin')
# Checkers must not pin one project lifecycle snapshot/version/review ID/package version.
for p in ['tools/check_project_docs.py','tools/check_runtime_state.py','tools/check_workflow_continuity.py','tools/audit_documentation_v2.py']:
    t=(ROOT/p).read_text(encoding='utf-8')
    if re.search(r'IMPLEMENTATION_PACKAGE_V\d+',t): errors.append('checker-hardcoded-package:'+p)
    if re.search(r'AI_FILM_(?:PROJECT_STATE|STATE_CHECKPOINT)_V(?:2[0-9]|[3-9][0-9])',t): errors.append('checker-hardcoded-state-version:'+p)
    if re.search(r'DOC-V2-(?:REVIEW|AUDIT)-\d{3}',t): errors.append('checker-hardcoded-review-id:'+p)
    run_literal='RUN-'+'P00-'
    step_literal='S'+'0'
    if re.search(re.escape(run_literal)+r'[A-Z0-9._-]+',t): errors.append('checker-hardcoded-run-id:'+p)
    if re.search(re.escape(step_literal)+r'[0-9]_[A-Z0-9_]+',t): errors.append('checker-hardcoded-current-step:'+p)
    forbidden_wip='WIP_'+'NOT_DURABLE_'+'NOT_REVIEWABLE'
    if forbidden_wip in t: errors.append('checker-hardcoded-wip-state:'+p)
continuity_tool=(ROOT/'tools/check_workflow_continuity.py').read_text(encoding='utf-8')
if "WS/'implement'" in continuity_tool or 'WS/"implement"' in continuity_tool:
    errors.append('continuity-checker-hardcoded-implement-worktree')

# Core V2 semantics.
if 'code is the subject under test' not in texts.get('TEST_STRATEGY.md',''): errors.append('test-code-authority-risk')
if 'SUPERSEDED' not in texts.get('POLICY_REGISTRY.md','') or 'RETIRED' not in texts.get('POLICY_REGISTRY.md',''): errors.append('policy-lifecycle-incomplete')
if 'SUCCESS_METRIC' not in texts.get('SELF_LEARNING.md',''): errors.append('learning-no-measurement')
if 'CHECKER_DRIFT' not in texts.get('RECOVERY_PLAYBOOK.md',''): errors.append('checker-drift-route-missing')
for path in ['environments/README.md','model-evaluations/README.md','learning/README.md','test-governance/README.md','workflow-health/README.md','workflow-runs/README.md']:
    if not (ROOT/path).is_file(): errors.append('missing-record-domain:'+path)
# Continuity architecture must prevent duplicate runs after interruption.
cont=texts.get('WORKFLOW_CONTINUITY.md','')
for token in ['one active `RUN_ID`','INTENT','COMPLETE','IDEMPOTENCY_KEY','IN_FLIGHT_AHEAD_OF_CANONICAL','There is no TTL-based abandonment']:
    if token not in cont: errors.append('continuity-missing:'+token)
nw=(ROOT/'NEXT_WORK_ITEM.md').read_text(encoding='utf-8')
for field in ['RUN_ID:','WORKFLOW_ID:','INPUT_IDENTITY:','STEPS:','CURRENT_STEP:','ON_BLOCK:','EXIT_CONDITION:']:
    if field not in nw: errors.append('next-work-resume-contract:'+field[:-1])

# Environment digest is actually reproducible.
env_record=ROOT/'environments/ENV-DEV-WSL-20260915.md'
if env_record.is_file():
    et=env_record.read_text(encoding='utf-8'); mp=re.search(r'```json\n(.+?)\n```',et,re.S); md=re.search(r'SNAPSHOT_DIGEST: ([0-9a-f]{64})',et)
    if not mp or not md: errors.append('environment-digest-record-missing')
    else:
        try:
            obj=json.loads(mp.group(1)); b=json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
            if hashlib.sha256(b).hexdigest()!=md.group(1): errors.append('environment-digest-mismatch')
        except Exception: errors.append('environment-canonical-json-invalid')
# Current state/snapshot dynamically match.
state=texts.get('PROJECT_STATE.md',''); mv=re.search(r'^STATE_VERSION: (\d+)$',state,re.M)
if not mv: errors.append('state-version-missing')
else:
    v=int(mv.group(1)); jp=ROOT/f'AI_FILM_PROJECT_STATE_V{v}.json'; cp=ROOT/f'AI_FILM_STATE_CHECKPOINT_V{v}.md'
    if not jp.is_file() or not cp.is_file(): errors.append('current-snapshot-missing')
    else:
        current=json.loads(jp.read_text())
        if current.get('state_version')!=v: errors.append('current-state-version-mismatch')
        active=current.get('active_run')
        if isinstance(active,dict):
            if str(active.get('run_id','')) not in nw: errors.append('current-run-id-drift')
            if str(active.get('current_step','')) not in nw: errors.append('current-run-step-drift')
if errors:
    print('DOC_AUDIT_FAIL');print('\n'.join(errors));sys.exit(1)
print('DOC_AUDIT_PASS',len(texts),'active docs','lifecycle-aware-checkers')
