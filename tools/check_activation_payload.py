#!/usr/bin/python3
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1];errors=[]
state=(ROOT/'activation/PROJECT_STATE_V22.md').read_text(encoding='utf-8');nextwork=(ROOT/'activation/NEXT_WORK_ITEM_WF_P00_IMPL_DEV18.md').read_text(encoding='utf-8');checkpoint=(ROOT/'activation/AI_FILM_STATE_CHECKPOINT_V22.md').read_text(encoding='utf-8');machine=json.loads((ROOT/'activation/AI_FILM_PROJECT_STATE_V22.json').read_text(encoding='utf-8'))
for token in ['ACTIVE_SYSTEM: V2_REVIEWED_AUDITED','NEXT_ACTION: WF-P00-IMPL-DEV18','OPEN_FINDINGS: [CR-P00-001, CR-P00-012, CR-P00-013]']:
    if token not in state: errors.append('activation-state:'+token)
for token in ['WORKFLOW_ID: WF-P00-IMPL-DEV18','LANE: IMPLEMENT','TEST_CONTRACT:','ORACLE_AUTHORITY_CLASS: COMPOSITE_APPROVED_AUTHORITIES','TEST_CHANGE_CLASS: IMPLEMENTATION_DEFECT','NATIVE_EXECUTION_ALLOWED: false','FULL_COMMAND: "/usr/bin/python3 /home/dragon/ai-film-dev/repo/tools/run_test_workflow.py implement"']:
    if token not in nextwork: errors.append('activation-next:'+token)
if 'DOCUMENTATION_SYSTEM: V2_REVIEWED_AUDITED' not in checkpoint: errors.append('activation-checkpoint')
if machine.get('documentation_system')!='V2_REVIEWED_AUDITED' or machine.get('next_workflow')!='WF-P00-IMPL-DEV18': errors.append('activation-json')
if machine.get('durable_source_commit')!='64ea95bf10e05e856a009be9204983182f520b45': errors.append('activation-source')
if len(machine.get('implement_wip_files',[]))!=4: errors.append('activation-wip-count')
if errors: print('\n'.join(errors));sys.exit(1)
print('ACTIVATION_PAYLOAD_CHECK_PASS')
