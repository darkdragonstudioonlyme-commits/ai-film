#!/usr/bin/env python3
from pathlib import Path
import subprocess,sys,re,json
ROOT=Path(__file__).resolve().parents[1]
# First run all deterministic guardrails.
subprocess.check_call([sys.executable,str(ROOT/'tools/run_governance_checks.py')])
errors=[]
active=['README.md','CHAT_HANDOFF.md','PROJECT_STATE.md','NEXT_WORK_ITEM.md','PROJECT_ROADMAP.md',
        'WORKFLOW_ROUTER.md','EXECUTION_LANES.md','DOCUMENTATION_MAP.md','PROJECT_MEMORY.md',
        'GIT_WORKFLOW.md','WORKSPACE_WSL.md','TEST_STRATEGY.md','SELF_LEARNING_SYSTEM.md',
        'KNOWLEDGE_LIFECYCLE.md','SERVER_ENVIRONMENT.md']
texts={n:(ROOT/n).read_text(encoding='utf-8') for n in active}
# Version-agnostic operating policies cannot pin a mutable delivery.
agnostic=set(active)-{'PROJECT_STATE.md','NEXT_WORK_ITEM.md','PROJECT_MEMORY.md','WORKSPACE_WSL.md','SERVER_ENVIRONMENT.md'}
for n in agnostic:
    if re.search(r'\b(?:0\.1\.0\.)?dev\d+\b',texts[n],re.I): errors.append('stale-version-risk:'+n)
# All key policy owners must be discoverable from knowledge map/index.
for n in ['TEST_STRATEGY.md','SELF_LEARNING_SYSTEM.md','KNOWLEDGE_LIFECYCLE.md','SERVER_ENVIRONMENT.md']:
    if n not in texts['DOCUMENTATION_MAP.md']: errors.append('map-missing:'+n)
    if n not in texts['README.md'] and n not in texts['KNOWLEDGE_LIFECYCLE.md']: errors.append('discoverability:'+n)
# Self-learning must not authorize contract override.
if 'never overrides frozen/reviewed behavior' not in texts['SELF_LEARNING_SYSTEM.md'].lower(): errors.append('learning-contract-boundary')
# Test policy must make source the subject, not oracle.
if 'source code is the subject under test' not in texts['TEST_STRATEGY.md'].lower(): errors.append('test-source-boundary')
# Environment evidence must match snapshot and remain fail-closed today.
snap=json.loads((ROOT/'evidence/SERVER_ENVIRONMENT_SNAPSHOT.json').read_text())
fp=snap['environment_fingerprint_sha256']
if fp not in texts['SERVER_ENVIRONMENT.md'] or fp not in texts['PROJECT_STATE.md']: errors.append('environment-fingerprint-drift')
if snap.get('model_evaluation_ready') is not False: errors.append('model-readiness-not-fail-closed')
# Active memory stays compact; archive exists.
if len(texts['PROJECT_MEMORY.md'].splitlines())>250: errors.append('memory-bloat')
if not (ROOT/'memory/archive/PROJECT_MEMORY_V1_BEFORE_V2.md').is_file(): errors.append('memory-history-missing')
# Retrospective route and final audit must be visible.
if 'WORKFLOW_RETROSPECTIVE' not in texts['SELF_LEARNING_SYSTEM.md'] and 'Retrospective contract' not in texts['SELF_LEARNING_SYSTEM.md']: errors.append('retro-contract-missing')
if 'DOC-AUDIT' not in texts['EXECUTION_LANES.md']: errors.append('third-lane-missing')
if errors:
    print('\n'.join(errors));raise SystemExit(1)
print('CONTROL_PLANE_AUDIT_STATIC_PASS',len(active),'active docs')
