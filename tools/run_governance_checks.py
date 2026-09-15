#!/usr/bin/env python3
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
checks=['check_project_docs.py','check_test_strategy.py','check_knowledge_hygiene.py','check_runtime_state.py']
for name in checks:
    subprocess.check_call([sys.executable,str(ROOT/'tools'/name)])
print('GOVERNANCE_CHECKS_PASS',len(checks))
