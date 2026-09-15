#!/usr/bin/env python3
from pathlib import Path
import re,sys,json
ROOT=Path(__file__).resolve().parents[1]
errors=[]
required=['KNOWLEDGE_LIFECYCLE.md','SELF_LEARNING_SYSTEM.md','SERVER_ENVIRONMENT.md','TEST_STRATEGY.md']
for name in required:
    if not (ROOT/name).is_file(): errors.append('missing:'+name)
mem=(ROOT/'PROJECT_MEMORY.md').read_text(encoding='utf-8')
lines=mem.splitlines()
entries=len(re.findall(r'\bMEM-\d{8}-\d{3}\b',mem))
if len(lines)>250: errors.append(f'memory-lines:{len(lines)}>250')
if entries>40: errors.append(f'memory-entry-refs:{entries}>40')
version_agnostic=['README.md','CHAT_HANDOFF.md','WORKFLOW_ROUTER.md','EXECUTION_LANES.md','DOCUMENTATION_MAP.md','GIT_WORKFLOW.md','PROJECT_ROADMAP.md','TEST_STRATEGY.md','SELF_LEARNING_SYSTEM.md','KNOWLEDGE_LIFECYCLE.md']
pat=re.compile(r'\b(?:0\.1\.0\.)?dev\d+\b',re.I)
for name in version_agnostic:
    text=(ROOT/name).read_text(encoding='utf-8')
    if pat.search(text): errors.append('mutable-version-in-policy:'+name)
server=(ROOT/'SERVER_ENVIRONMENT.md').read_text(encoding='utf-8')
for item in ['OBSERVED_AT:','MODEL_EVALUATION_READY:','GPU_STATUS:','Tool provenance rule','Environment freshness']:
    if item not in server: errors.append('server-env:'+item)
snap=json.loads((ROOT/'evidence/SERVER_ENVIRONMENT_SNAPSHOT.json').read_text(encoding='utf-8'))
fp=snap.get('environment_fingerprint_sha256')
if not fp or fp not in server: errors.append('server-fingerprint-mismatch')
state=(ROOT/'PROJECT_STATE.md').read_text(encoding='utf-8')
if fp and fp not in state: errors.append('state-environment-fingerprint-mismatch')
if not (ROOT/'memory/archive/PROJECT_MEMORY_V1_BEFORE_V2.md').is_file(): errors.append('memory-archive-missing')
if errors:
    print('\n'.join(errors));sys.exit(1)
print('KNOWLEDGE_HYGIENE_PASS', 'memory_lines='+str(len(lines)), 'memory_refs='+str(entries))
