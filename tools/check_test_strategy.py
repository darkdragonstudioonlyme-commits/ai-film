#!/usr/bin/env python3
from pathlib import Path
import sys,re
ROOT=Path(__file__).resolve().parents[1]
errors=[]
strategy=(ROOT/'TEST_STRATEGY.md').read_text(encoding='utf-8')
nextwork=(ROOT/'NEXT_WORK_ITEM.md').read_text(encoding='utf-8')
required_strategy=['Test-basis precedence','Source code is the subject under test','Required test viewpoints','TEST_CONTRACT:','Changing tests when business changes','Test-script architecture','Model-evaluation testing','ORACLE_AUTHORITY_CLASS:']
for item in required_strategy:
    if item not in strategy: errors.append('test-strategy:'+item)
required_fields=['BUSINESS_GOAL','TEST_BASIS','ORACLE_AUTHORITY_CLASS','ORACLE_SOURCE','TEST_CHANGE_CLASS','TEST_CHANGE_AUTHORITY','VIEWPOINTS','ENVIRONMENT_CLASS','NATIVE_EXECUTION_ALLOWED','PASS_MEANS','PASS_DOES_NOT_MEAN']
for item in required_fields:
    if not re.search(r'^\s*'+re.escape(item)+r':',nextwork,re.M): errors.append('next-work-test-contract:'+item)
def field(name):
    m=re.search(r'^\s*'+re.escape(name)+r':\s*(.+?)\s*$',nextwork,re.M)
    return m.group(1).strip().strip('"\'') if m else None
allowed={'OWNER_REQUIREMENTS','REVIEWED_CONTRACTS','ACCEPTANCE_MATRIX','REVIEW_FINDINGS','VALIDATION_SPEC','COMPOSITE_APPROVED_AUTHORITIES'}
auth=field('ORACLE_AUTHORITY_CLASS')
if auth not in allowed: errors.append('oracle-authority-class:'+str(auth))
change=field('TEST_CHANGE_CLASS')
allowed_change={'NONE','APPROVED_BEHAVIOR_CHANGE','TEST_DEFECT','HARNESS_DEFECT','ENVIRONMENT_DEFECT','IMPLEMENTATION_DEFECT','DESIGN_GAP'}
if change not in allowed_change: errors.append('test-change-class:'+str(change))
source=(field('ORACLE_SOURCE') or '').lower()
forbidden=['current code','code behavior','implementation output','source implementation','implementation behavior','whatever the code']
if any(x in source for x in forbidden): errors.append('code-derived-oracle-source')
if errors:
    print('\n'.join(errors));sys.exit(1)
print('TEST_STRATEGY_CHECK_PASS', 'oracle_class='+str(auth), 'change_class='+str(change))
