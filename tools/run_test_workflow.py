#!/usr/bin/env python3
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
mode=sys.argv[1] if len(sys.argv)>1 else None
if mode not in ('implement','review','docs'):
    print('usage: run_test_workflow.py implement|review|docs');raise SystemExit(10)
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
