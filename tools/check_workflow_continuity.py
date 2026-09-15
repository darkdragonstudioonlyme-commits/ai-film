#!/usr/bin/env python3
from pathlib import Path
import json,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
WS=Path('/home/dragon/ai-film-dev'); REPO=WS/'repo'; errors=[]

def latest_state():
    rows=[]
    for p in ROOT.glob('AI_FILM_PROJECT_STATE_V*.json'):
        m=re.fullmatch(r'AI_FILM_PROJECT_STATE_V(\d+)\.json',p.name)
        if m: rows.append((int(m.group(1)),p))
    v,p=max(rows); return v,json.loads(p.read_text())

v,state=latest_state(); active=state.get('active_run')
if type(active) is not dict:
    print('WORKFLOW_CONTINUITY_CHECK_PASS no-active-run state=V'+str(v)); raise SystemExit(0)
for k in ['run_id','owner_lane','run_record','status','current_step','canonical_base','observed_local_head']:
    if not active.get(k): errors.append('active-run-field:'+k)
if active.get('run_id')!='RUN-P00-CR001-001' and state.get('runtime_reconciliation',{}).get('state_kind')=='IN_FLIGHT_AHEAD_OF_CANONICAL':
    errors.append('active-run-id-unbound')
# Canonical snapshot must exist. Live lane record is verified when prepared workspace exists.
snap=active.get('canonical_snapshot')
if snap and not (ROOT/snap).is_file(): errors.append('active-run-snapshot-missing')
if REPO.is_dir() and (WS/'implement').is_dir():
    subprocess.check_call(['git','-C',str(REPO),'fetch','origin','lane/implement-p00'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    lane=subprocess.check_output(['git','-C',str(REPO),'show','origin/lane/implement-p00:LANE_STATE.md'],text=True)
    rid=active.get('run_id','')
    if rid not in lane: errors.append('lane-active-run-pointer-missing')
    try:
        record=subprocess.check_output(['git','-C',str(REPO),'show',f'origin/lane/implement-p00:workflow-runs/{rid}.md'],text=True)
    except subprocess.CalledProcessError:
        record=''; errors.append('lane-run-record-missing')
    if record:
        for token in [rid,active.get('current_step',''),active.get('observed_local_head','')]:
            if token and token not in record: errors.append('lane-run-record-token:'+token)
    head=subprocess.check_output(['git','-C',str(WS/'implement'),'rev-parse','HEAD'],text=True).strip()
    if head!=active.get('observed_local_head'): errors.append('active-run-local-head:'+head+'!='+str(active.get('observed_local_head')))
if errors:
    print('WORKFLOW_CONTINUITY_CHECK_FAIL'); print('\n'.join(errors)); raise SystemExit(1)
print('WORKFLOW_CONTINUITY_CHECK_PASS','state=V'+str(v),'run='+active['run_id'],'step='+active['current_step'])
