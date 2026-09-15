#!/usr/bin/python3
from pathlib import Path
import subprocess,sys,re,json,tempfile
ROOT=Path(__file__).resolve().parents[1]
subprocess.check_call([sys.executable,str(ROOT/'tools/run_governance_checks.py')])
errors=[]
active=['README.md','CHAT_HANDOFF.md','PROJECT_STATE.md','NEXT_WORK_ITEM.md','PROJECT_ROADMAP.md','WORKFLOW_ROUTER.md','EXECUTION_LANES.md','DOCUMENTATION_MAP.md','PROJECT_MEMORY.md','GIT_WORKFLOW.md','WORKSPACE_WSL.md','TEST_STRATEGY.md','SELF_LEARNING_SYSTEM.md','KNOWLEDGE_LIFECYCLE.md','SERVER_ENVIRONMENT.md']
texts={n:(ROOT/n).read_text(encoding='utf-8') for n in active}
agnostic=set(active)-{'PROJECT_STATE.md','NEXT_WORK_ITEM.md','PROJECT_MEMORY.md','WORKSPACE_WSL.md','SERVER_ENVIRONMENT.md'}
for n in agnostic:
    if re.search(r'\b(?:0\.1\.0\.)?dev\d+\b',texts[n],re.I): errors.append('stale-version-risk:'+n)
for n in ['TEST_STRATEGY.md','SELF_LEARNING_SYSTEM.md','KNOWLEDGE_LIFECYCLE.md','SERVER_ENVIRONMENT.md']:
    if n not in texts['DOCUMENTATION_MAP.md']: errors.append('map-missing:'+n)
    if n not in texts['README.md'] and n not in texts['KNOWLEDGE_LIFECYCLE.md']: errors.append('discoverability:'+n)
if 'never overrides frozen/reviewed behavior' not in texts['SELF_LEARNING_SYSTEM.md'].lower(): errors.append('learning-contract-boundary')
if 'source code is the subject under test' not in texts['TEST_STRATEGY.md'].lower(): errors.append('test-source-boundary')
snap=json.loads((ROOT/'evidence/SERVER_ENVIRONMENT_SNAPSHOT.json').read_text())
fp=snap['environment_fingerprint_sha256']
if fp not in texts['SERVER_ENVIRONMENT.md'] or fp not in texts['PROJECT_STATE.md']: errors.append('environment-fingerprint-drift')
if snap.get('model_evaluation_ready') is not False: errors.append('model-readiness-not-fail-closed')
if len(texts['PROJECT_MEMORY.md'].splitlines())>250: errors.append('memory-bloat')
if not (ROOT/'memory/archive/PROJECT_MEMORY_V1_BEFORE_V2.md').is_file(): errors.append('memory-history-missing')
with tempfile.TemporaryDirectory() as tmp:
    t=Path(tmp); (t/'repo/tools').mkdir(parents=True)
    subprocess.check_call([sys.executable,str(ROOT/'tools/sync_workspace_helpers.py'),'--root',tmp],stdout=subprocess.DEVNULL)
    subprocess.check_call([sys.executable,str(ROOT/'tools/sync_workspace_helpers.py'),'--root',tmp,'--check'],stdout=subprocess.DEVNULL)
    helper=(t/'test.sh').read_text(encoding='utf-8')
    if '/usr/bin/python3' not in helper or 'run_test_workflow.py implement' not in helper or 'lane-test.sh implement' in helper: errors.append('workspace-helper-policy-bypass')
if 'WORKFLOW_RETROSPECTIVE' not in texts['SELF_LEARNING_SYSTEM.md'] and 'Retrospective contract' not in texts['SELF_LEARNING_SYSTEM.md']: errors.append('retro-contract-missing')
if 'DOC-AUDIT' not in texts['EXECUTION_LANES.md']: errors.append('third-lane-missing')
if errors:
    print('\n'.join(errors));raise SystemExit(1)
print('CONTROL_PLANE_AUDIT_STATIC_PASS',len(active),'active docs')
