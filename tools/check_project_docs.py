#!/usr/bin/env python3
from pathlib import Path
import re, sys
ROOT=Path(__file__).resolve().parents[1]
required=['README.md','PROJECT_STATE.md','NEXT_WORK_ITEM.md','PROJECT_ROADMAP.md',
          'WORKFLOW_ROUTER.md','EXECUTION_LANES.md','DOCUMENTATION_MAP.md',
          'PROJECT_MEMORY.md','GIT_WORKFLOW.md','WORKSPACE_WSL.md','CHAT_HANDOFF.md']
errors=[]
for name in required:
    if not (ROOT/name).is_file(): errors.append(f'missing:{name}')
text={name:(ROOT/name).read_text(encoding='utf-8') for name in required if (ROOT/name).is_file()}
checks=[
 ('state-mode', 'CURRENT_MODE: IMPLEMENTATION', text.get('PROJECT_STATE.md','')),
 ('next-mode', 'MODE: IMPLEMENTATION', text.get('NEXT_WORK_ITEM.md','')),
 ('state-wip', 'WIP_NOT_DURABLE_NOT_REVIEWABLE', text.get('PROJECT_STATE.md','')),
 ('next-router', 'WORKFLOW_ROUTER', text.get('NEXT_WORK_ITEM.md','')),
 ('router-continue', '“Continue” algorithm', text.get('WORKFLOW_ROUTER.md','')),
 ('lanes-doc-review', 'DOC-DESIGN / DOC-REVIEW', text.get('EXECUTION_LANES.md','')),
 ('map-sync', 'Documentation Sync Gate', text.get('DOCUMENTATION_MAP.md','')),
 ('memory-promotion', 'promotion', text.get('PROJECT_MEMORY.md','').lower()),
 ('git-fetch', 'fetch origin main', text.get('GIT_WORKFLOW.md','')),
]
for key,needle,body in checks:
    if needle not in body: errors.append(f'invariant:{key}')
# README and handoff must not pin mutable delivery versions.
for name in ('README.md','CHAT_HANDOFF.md'):
    if re.search(r'0\.1\.0\.dev\d+', text.get(name,'')): errors.append(f'version-drift-risk:{name}')
if errors:
    print('\n'.join(errors));sys.exit(1)
print('DOCS_CHECK_PASS', len(required), 'core files')
