#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
errors=[]
strategy=(ROOT/'TEST_STRATEGY.md').read_text(encoding='utf-8')
nextwork=(ROOT/'NEXT_WORK_ITEM.md').read_text(encoding='utf-8')
required_strategy=['Test-basis precedence','Source code is the subject under test','Required test viewpoints','TEST_CONTRACT:','Changing tests when business changes','Test-script architecture','Model-evaluation testing']
for item in required_strategy:
    if item not in strategy: errors.append('test-strategy:'+item)
for item in ['TEST_CONTRACT:','BUSINESS_GOAL:','TEST_BASIS:','ORACLE_SOURCE:','VIEWPOINTS:','PASS_MEANS:','PASS_DOES_NOT_MEAN:']:
    if item not in nextwork: errors.append('next-work-test-contract:'+item)
if 'current code behavior' in nextwork.lower(): errors.append('code-derived-oracle')
if errors:
    print('\n'.join(errors));sys.exit(1)
print('TEST_STRATEGY_CHECK_PASS')
