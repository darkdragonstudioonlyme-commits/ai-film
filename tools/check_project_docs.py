#!/usr/bin/python3
from pathlib import Path
import re,sys
ROOT=Path(__file__).resolve().parents[1]
required=['README.md','PROJECT_STATE.md','NEXT_WORK_ITEM.md','PROJECT_ROADMAP.md','WORKFLOW_ROUTER.md','EXECUTION_LANES.md','DOCUMENTATION_MAP.md','PROJECT_MEMORY.md','GIT_WORKFLOW.md','WORKSPACE_WSL.md','CHAT_HANDOFF.md','TEST_STRATEGY.md','SELF_LEARNING_SYSTEM.md','KNOWLEDGE_LIFECYCLE.md','SERVER_ENVIRONMENT.md']
errors=[]
for name in required:
    if not (ROOT/name).is_file(): errors.append('missing:'+name)
text={name:(ROOT/name).read_text(encoding='utf-8') for name in required if (ROOT/name).is_file()}
checks=[('state-mode','CURRENT_MODE: IMPLEMENTATION',text.get('PROJECT_STATE.md','')),('state-wip','WIP_NOT_DURABLE_NOT_REVIEWABLE',text.get('PROJECT_STATE.md','')),('next-test','TEST_CONTRACT:',text.get('NEXT_WORK_ITEM.md','')),('router-retro','Retrospective/deadlock route',text.get('WORKFLOW_ROUTER.md','')),('lanes-audit','DOC-AUDIT',text.get('EXECUTION_LANES.md','')),('map-test','TEST_STRATEGY.md',text.get('DOCUMENTATION_MAP.md','')),('map-learning','SELF_LEARNING_SYSTEM.md',text.get('DOCUMENTATION_MAP.md','')),('test-business','Source code is the subject under test',text.get('TEST_STRATEGY.md','')),('learning-trigger','Mandatory meta-review triggers',text.get('SELF_LEARNING_SYSTEM.md','')),('knowledge-pruning','Promotion and pruning',text.get('KNOWLEDGE_LIFECYCLE.md','')),('server-readiness','MODEL_EVALUATION_READY:',text.get('SERVER_ENVIRONMENT.md','')),('git-test-policy','Test semantic changes',text.get('GIT_WORKFLOW.md',''))]
for key,needle,body in checks:
    if needle not in body: errors.append('invariant:'+key)
for name in ('README.md','CHAT_HANDOFF.md'):
    if re.search(r'\b(?:0\.1\.0\.)?dev\d+\b',text.get(name,''),re.I): errors.append('version-drift-risk:'+name)
for path in ['docs/DOCUMENTATION_SYSTEM_V2_DESIGN.md','docs/DOCUMENTATION_REVIEW_CRITERIA_V2.md','docs/DOCUMENTATION_AUDIT_CRITERIA_V2.md','retrospectives/RETROSPECTIVE_TEMPLATE.md','tools/sync_workspace_helpers.py']:
    if not (ROOT/path).is_file(): errors.append('missing:'+path)
allowed_root=set(required);checkpoint=re.compile(r'^AI_FILM_STATE_CHECKPOINT_V\d+\.md$')
for path in ROOT.glob('*.md'):
    if path.name not in allowed_root and not checkpoint.match(path.name): errors.append('unowned-root-md:'+path.name)
if errors: print('\n'.join(errors));sys.exit(1)
print('DOCS_CHECK_PASS',len(required),'core files')
