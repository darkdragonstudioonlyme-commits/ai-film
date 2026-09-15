#!/usr/bin/env python3
from pathlib import Path
import subprocess,sys,re
ROOT=Path(__file__).resolve().parents[1]
mode=sys.argv[1] if len(sys.argv)>1 else None
if mode not in ('implement','review','docs'):
    print('usage: run_test_workflow.py implement|review|docs');raise SystemExit(10)
nextwork=(ROOT/'NEXT_WORK_ITEM.md').read_text(encoding='utf-8')
server=(ROOT/'SERVER_ENVIRONMENT.md').read_text(encoding='utf-8')
def field(text,name):
    m=re.search(r'^\s*'+re.escape(name)+r':\s*(.+?)\s*$',text,re.M)
    return m.group(1).strip().strip('"\'') if m else None
lane=field(nextwork,'LANE') or ''
expected='docs' if lane.startswith('DOC-') else ('implement' if 'IMPLEMENT' in lane else ('review' if 'REVIEW' in lane else None))
if expected!=mode:
    print(f'TEST_WORKFLOW_LANE_MISMATCH active={lane} requested={mode} expected={expected}');raise SystemExit(12)
contract_env=field(nextwork,'ENVIRONMENT_CLASS')
observed_env=field(server,'ENVIRONMENT_CLASS')
if contract_env!=observed_env:
    print(f'TEST_ENVIRONMENT_MISMATCH contract={contract_env} observed={observed_env}');raise SystemExit(11)
native=(field(nextwork,'NATIVE_EXECUTION_ALLOWED') or '').lower()
if native!='false':
    print('AUTHOR_TEST_WRAPPER_NATIVE_FORBIDDEN');raise SystemExit(12)
subprocess.check_call([sys.executable,str(ROOT/'tools/check_test_strategy.py')])
subprocess.check_call([sys.executable,str(ROOT/'tools/check_knowledge_hygiene.py')])
subprocess.check_call([sys.executable,str(ROOT/'tools/check_runtime_state.py')])
if mode=='docs':
    subprocess.check_call([sys.executable,str(ROOT/'tools/check_project_docs.py')])
else:
    helper=Path('/home/dragon/ai-film-dev/lane-test.sh')
    if not helper.is_file():
        print('lane-test helper unavailable');raise SystemExit(18)
    subprocess.check_call([str(helper),mode])
