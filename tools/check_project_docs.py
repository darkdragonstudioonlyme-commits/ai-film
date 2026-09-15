#!/usr/bin/env python3
from pathlib import Path
import re,sys,json
ROOT=Path(__file__).resolve().parents[1]
required=[
 'README.md','PROJECT_STATE.md','NEXT_WORK_ITEM.md','PROJECT_ROADMAP.md','WORKFLOW_ROUTER.md',
 'EXECUTION_LANES.md','DOCUMENTATION_MAP.md','PROJECT_MEMORY.md','SELF_LEARNING.md',
 'TEST_STRATEGY.md','WORKFLOW_HEALTH.md','POLICY_REGISTRY.md','SERVER_ENVIRONMENT.md',
 'MODEL_EVALUATION.md','RECOVERY_PLAYBOOK.md','OPERATING_ARCHITECTURE.md',
 'GIT_WORKFLOW.md','WORKSPACE_WSL.md','CHAT_HANDOFF.md','WORKFLOW_CONTINUITY.md']
errors=[]
for name in required:
    if not (ROOT/name).is_file(): errors.append('missing:'+name)
for path in ['test-governance/README.md','workflow-health/README.md','environments/README.md',
             'model-evaluations/README.md','learning/README.md','workflow-runs/README.md']:
    if not (ROOT/path).is_file(): errors.append('missing:'+path)
text={n:(ROOT/n).read_text(encoding='utf-8') for n in required if (ROOT/n).is_file()}
state=text.get('PROJECT_STATE.md','')
mv=re.search(r'^STATE_VERSION: (\d+)$',state,re.M)
if not mv: errors.append('state-version-missing'); state_version=None
else: state_version=int(mv.group(1))
state_json=None
if state_version is not None:
    jp=ROOT/f'AI_FILM_PROJECT_STATE_V{state_version}.json'; mp=ROOT/f'AI_FILM_STATE_CHECKPOINT_V{state_version}.md'
    if not jp.is_file(): errors.append('state-json-missing:'+jp.name)
    if not mp.is_file(): errors.append('checkpoint-missing:'+mp.name)
    if jp.is_file():
        try: state_json=json.loads(jp.read_text(encoding='utf-8'))
        except (ValueError,TypeError): errors.append('state-json-invalid')
if state_json:
    if state_json.get('state_version')!=state_version: errors.append('state-version-mismatch')
    mode=re.search(r'^CURRENT_MODE: ([A-Z_]+)$',state,re.M)
    if not mode or state_json.get('current_mode')!=mode.group(1): errors.append('state-mode-mismatch')
    if state_json.get('documentation_system','').startswith('DOCSYS-V2-') is False: errors.append('documentation-system-not-v2')
    ar=state_json.get('active_run')
    if ar is not None and (type(ar) is not dict or not ar.get('run_id') or not ar.get('workflow_id') or not ar.get('run_record') or not ar.get('current_step')):
        errors.append('active-run-schema')
    rr=state_json.get('runtime_reconciliation')
    if type(rr) is not dict or rr.get('schema_version')!=1: errors.append('runtime-reconciliation-schema')
    else:
        allowed={'WIP','HANDED_OFF','REVIEWED_FAIL','REVIEWED_CLEAN_RESIDUAL_AUDIT','FINAL_AUTHOR_CANDIDATE','FORMAL_CODE_REVIEW','VALIDATION','IN_FLIGHT_AHEAD_OF_CANONICAL'}
        if rr.get('state_kind') not in allowed: errors.append('runtime-state-kind')
        if not re.fullmatch(r'[0-9a-f]{40}',str(rr.get('implement_head',''))): errors.append('runtime-implement-head')
        if not re.fullmatch(r'[0-9a-f]{40}',str(rr.get('review_head',''))): errors.append('runtime-review-head')
        if type(rr.get('implement_dirty_files')) is not list: errors.append('runtime-dirty-files')
checks=[
 ('router-continue','“Continue” algorithm','WORKFLOW_ROUTER.md'),('router-health','WORKFLOW_REVIEW','WORKFLOW_ROUTER.md'),
 ('test-authority','implementation code last','TEST_STRATEGY.md'),('test-change','TEST_CHANGE','TEST_STRATEGY.md'),
 ('health-meta','META_REVIEW_REQUIRED','WORKFLOW_HEALTH.md'),('policy-retire','RETIRED','POLICY_REGISTRY.md'),
 ('learning-retire','SUPERSEDED|RETIRED','SELF_LEARNING.md'),('env-notvisible','NOT_VISIBLE','SERVER_ENVIRONMENT.md'),
 ('model-env','EVAL_ENV_ID','MODEL_EVALUATION.md'),('recovery-drift','STATE_DRIFT','RECOVERY_PLAYBOOK.md'),
 ('recovery-checker','CHECKER_DRIFT','RECOVERY_PLAYBOOK.md'),('docs-audit','DOC-AUDIT','EXECUTION_LANES.md'),
 ('git-fetch','fetch origin main','GIT_WORKFLOW.md'),('test-records','test-governance/','TEST_STRATEGY.md'),
 ('health-records','workflow-health/','WORKFLOW_HEALTH.md'),('env-records','environments/','SERVER_ENVIRONMENT.md'),
 ('model-records','model-evaluations/','MODEL_EVALUATION.md'),('learning-records','learning/','SELF_LEARNING.md'),('continuity-run','RUN_ID','WORKFLOW_CONTINUITY.md'),('continuity-intent','INTENT','WORKFLOW_CONTINUITY.md'),('continuity-idempotency','IDEMPOTENCY_KEY','WORKFLOW_CONTINUITY.md'),('continuity-domain','workflow-runs/','DOCUMENTATION_MAP.md')]
for key,needle,name in checks:
    if needle not in text.get(name,''): errors.append('invariant:'+key)
version_agnostic=['README.md','CHAT_HANDOFF.md','WORKFLOW_ROUTER.md','EXECUTION_LANES.md','DOCUMENTATION_MAP.md',
 'TEST_STRATEGY.md','WORKFLOW_HEALTH.md','POLICY_REGISTRY.md','MODEL_EVALUATION.md','SELF_LEARNING.md',
 'RECOVERY_PLAYBOOK.md','OPERATING_ARCHITECTURE.md','GIT_WORKFLOW.md','WORKSPACE_WSL.md','WORKFLOW_CONTINUITY.md']
for name in version_agnostic:
    if re.search(r'0\.1\.0\.dev\d+',text.get(name,'')): errors.append('version-pin:'+name)

# NEXT_WORK_ITEM must satisfy the router's machine-resumable workflow contract.
nw=(ROOT/'NEXT_WORK_ITEM.md').read_text(encoding='utf-8')
for field in ['RUN_ID:','WORKFLOW_ID:','LANE:','STATUS:','INPUT_IDENTITY:','GOAL:','STEPS:','CURRENT_STEP:','SUCCESS_OUTPUT:','ON_SUCCESS:','ON_FAIL:','ON_BLOCK:','EXIT_CONDITION:']:
    if field not in nw: errors.append('next-work-contract:'+field[:-1])
# Bootstrap numbered lists must be contiguous.
for name,heading in [('README.md','## Cold-start order'),('CHAT_HANDOFF.md','## Cold start'),('WORKFLOW_ROUTER.md','## 3. “Continue” algorithm')]:
    body=(ROOT/name).read_text(encoding='utf-8'); section=body.split(heading,1)[1].split('\n## ',1)[0]
    nums=[int(x) for x in re.findall(r'(?m)^(\d+)\. ',section)]
    if nums!=list(range(1,len(nums)+1)): errors.append('bootstrap-numbering:'+name)
if errors:
    print('DOCS_CHECK_FAIL');print('\n'.join(errors));sys.exit(1)
print('DOCS_CHECK_PASS',len(required),'active files','state_version='+str(state_version),'state_kind='+state_json['runtime_reconciliation']['state_kind'])
