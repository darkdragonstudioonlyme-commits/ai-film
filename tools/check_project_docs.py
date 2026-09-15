#!/usr/bin/env python3
from pathlib import Path
import re,sys
ROOT=Path(__file__).resolve().parents[1]
required=[
 'README.md','PROJECT_STATE.md','NEXT_WORK_ITEM.md','PROJECT_ROADMAP.md','WORKFLOW_ROUTER.md',
 'EXECUTION_LANES.md','DOCUMENTATION_MAP.md','PROJECT_MEMORY.md','SELF_LEARNING.md',
 'TEST_STRATEGY.md','WORKFLOW_HEALTH.md','POLICY_REGISTRY.md','SERVER_ENVIRONMENT.md',
 'MODEL_EVALUATION.md','RECOVERY_PLAYBOOK.md','OPERATING_ARCHITECTURE.md',
 'GIT_WORKFLOW.md','WORKSPACE_WSL.md','CHAT_HANDOFF.md']
errors=[]
for name in required:
    if not (ROOT/name).is_file(): errors.append('missing:'+name)
for path in ['test-governance/README.md','workflow-health/README.md']:
    if not (ROOT/path).is_file(): errors.append('missing:'+path)
text={n:(ROOT/n).read_text(encoding='utf-8') for n in required if (ROOT/n).is_file()}
checks=[
 ('state-mode','CURRENT_MODE: IMPLEMENTATION','PROJECT_STATE.md'),
 ('state-wip','WIP_NOT_DURABLE_NOT_REVIEWABLE','PROJECT_STATE.md'),
 ('router-continue','“Continue” algorithm','WORKFLOW_ROUTER.md'),
 ('router-health','WORKFLOW_REVIEW','WORKFLOW_ROUTER.md'),
 ('test-authority','implementation code last','TEST_STRATEGY.md'),
 ('test-change','TEST_CHANGE','TEST_STRATEGY.md'),
 ('health-meta','META_REVIEW_REQUIRED','WORKFLOW_HEALTH.md'),
 ('policy-retire','RETIRED','POLICY_REGISTRY.md'),
 ('learning-retire','SUPERSEDED|RETIRED','SELF_LEARNING.md'),
 ('env-notvisible','NOT_VISIBLE','SERVER_ENVIRONMENT.md'),
 ('model-env','EVAL_ENV_ID','MODEL_EVALUATION.md'),
 ('recovery-drift','STATE_DRIFT','RECOVERY_PLAYBOOK.md'),
 ('docs-audit','DOC-AUDIT','EXECUTION_LANES.md'),
 ('git-fetch','fetch origin main','GIT_WORKFLOW.md'),
 ('test-records','test-governance/','TEST_STRATEGY.md'),
 ('health-records','workflow-health/','WORKFLOW_HEALTH.md'),
 ('env-provenance','Measurement provenance','SERVER_ENVIRONMENT.md'),
 ('policy-owner','Owner','POLICY_REGISTRY.md')]
for key,needle,name in checks:
    body=text.get(name,'')
    if needle not in body: errors.append('invariant:'+key)
# Mutable versions are forbidden in routing/policy/bootstrap docs.
version_agnostic=['README.md','CHAT_HANDOFF.md','WORKFLOW_ROUTER.md','EXECUTION_LANES.md',
 'DOCUMENTATION_MAP.md','TEST_STRATEGY.md','WORKFLOW_HEALTH.md','POLICY_REGISTRY.md',
 'MODEL_EVALUATION.md','SELF_LEARNING.md','RECOVERY_PLAYBOOK.md','OPERATING_ARCHITECTURE.md','GIT_WORKFLOW.md']
for name in version_agnostic:
    if re.search(r'0\.1\.0\.dev\d+',text.get(name,'')): errors.append('version-pin:'+name)
if errors:
    print('DOCS_CHECK_FAIL');print('\n'.join(errors));sys.exit(1)
print('DOCS_CHECK_PASS',len(required),'active files')
