#!/usr/bin/env python3
from pathlib import Path
import json,re,subprocess,sys,os,hashlib
ROOT=Path(__file__).resolve().parents[1]
WS=Path(os.environ.get('AIFILM_WORKSPACE_ROOT','/home/dragon/ai-film-dev'))
REPO=WS/'repo'; errors=[]

def latest_state():
    rows=[]
    for p in ROOT.glob('AI_FILM_PROJECT_STATE_V*.json'):
        m=re.fullmatch(r'AI_FILM_PROJECT_STATE_V(\d+)\.json',p.name)
        if m: rows.append((int(m.group(1)),p))
    if not rows: raise ValueError('STATE_JSON_MISSING')
    v,p=max(rows); return v,json.loads(p.read_text())

def field(text,name):
    m=re.search(r'(?m)^\s*'+re.escape(name)+r':\s*(.*?)\s*$',text)
    if not m: return None
    value=m.group(1).strip()
    if len(value)>=2 and value[0]==value[-1]=='"': value=value[1:-1]
    return value

v,state=latest_state(); active=state.get('active_run')
if type(active) is not dict:
    print('WORKFLOW_CONTINUITY_CHECK_PASS no-active-run state=V'+str(v)); raise SystemExit(0)
for k in ['run_id','workflow_id','owner_lane','run_record','status','current_step','canonical_base','observed_local_head']:
    if not active.get(k): errors.append('active-run-field:'+k)
rid=str(active.get('run_id','')); wid=str(active.get('workflow_id','')); base=str(active.get('canonical_base',''))
if not re.fullmatch(r'RUN-[A-Z0-9][A-Z0-9._-]{2,79}',rid): errors.append('active-run-id-schema')
if not re.fullmatch(r'WF-[A-Z0-9][A-Z0-9._-]{2,99}',wid): errors.append('active-workflow-id-schema')
if not re.fullmatch(r'[0-9a-f]{40}',base): errors.append('active-run-base-schema')
record_locator=str(active.get('run_record',''))
if ':' not in record_locator: errors.append('active-run-record-locator')
else:
    branch,path=record_locator.split(':',1)
    if not branch.startswith('lane/') or not re.fullmatch(r'workflow-runs/[A-Z0-9._-]+\.md',path):
        errors.append('active-run-record-locator')
snap=active.get('canonical_snapshot')
if snap and not (ROOT/snap).is_file(): errors.append('active-run-snapshot-missing')
if REPO.is_dir() and (WS/'implement').is_dir() and ':' in record_locator:
    branch,path=record_locator.split(':',1); remote='origin/'+branch
    subprocess.check_call(['git','-C',str(REPO),'fetch','origin',branch],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    try: lane=subprocess.check_output(['git','-C',str(REPO),'show',remote+':LANE_STATE.md'],text=True)
    except subprocess.CalledProcessError: lane=''; errors.append('lane-state-missing')
    if lane:
        for token in [rid,path,active.get('current_step','')]:
            if token and token not in lane: errors.append('lane-active-run-token:'+str(token))
    try: record=subprocess.check_output(['git','-C',str(REPO),'show',remote+':'+path],text=True)
    except subprocess.CalledProcessError: record=''; errors.append('lane-run-record-missing')
    if record:
        required={'RUN_ID':rid,'WORKFLOW_ID':wid,'BASE_IDENTITY':base,'CURRENT_STEP':str(active.get('current_step',''))}
        for name,value in required.items():
            if field(record,name)!=value: errors.append('lane-run-field:'+name)
        if str(active.get('observed_local_head','')) not in record: errors.append('lane-run-output-head')
        # The currently executable duplicate-prone step must be machine-addressable.
        step_id=field(record,'STEP_ID'); step_state=field(record,'STATE')
        input_raw=field(record,'INPUT_IDENTITY'); idem=field(record,'IDEMPOTENCY_KEY')
        done_raw=field(record,'DONE_WHEN'); output_raw=field(record,'OUTPUT_IDENTITY'); replay=field(record,'REPLAY_POLICY')
        if step_id!=str(active.get('current_step','')): errors.append('current-step-id-drift')
        if step_state not in {'PENDING','INTENT','COMPLETE','RECONCILE_REQUIRED','BLOCKED','SKIPPED'}: errors.append('current-step-state')
        if replay not in {'VERIFY_AND_REUSE','SAFE_REEXECUTE','NEVER_REEXECUTE'}: errors.append('current-step-replay-policy')
        if not re.fullmatch(r'[0-9a-f]{64}',str(idem or '')): errors.append('current-step-idempotency-schema')
        input_obj=done_obj=output_obj=None
        try:
            input_obj=json.loads(input_raw) if input_raw is not None else None
            done_obj=json.loads(done_raw) if done_raw is not None else None
            output_obj=json.loads(output_raw) if output_raw is not None else None
        except (ValueError,TypeError): errors.append('current-step-json')
        if not isinstance(input_obj,dict) or not input_obj: errors.append('current-step-input-identity')
        if not isinstance(done_obj,dict) or not done_obj: errors.append('current-step-done-when')
        if isinstance(input_obj,dict) and step_id:
            key=hashlib.sha256(json.dumps({'step_id':step_id,'input_identity':input_obj},sort_keys=True,separators=(',',':')).encode()).hexdigest()
            if idem!=key: errors.append('current-step-idempotency-mismatch')
        if step_state=='COMPLETE' and not isinstance(output_obj,dict): errors.append('current-step-complete-output-missing')
        if step_state!='COMPLETE' and output_obj is not None and not isinstance(output_obj,dict): errors.append('current-step-output-schema')
        # One live run for one workflow/base on this lane. Historical COMPLETE records do not conflict.
        paths=subprocess.check_output(['git','-C',str(REPO),'ls-tree','-r','--name-only',remote,'workflow-runs'],text=True).splitlines()
        active_matches=[]
        for rp in paths:
            if not re.fullmatch(r'workflow-runs/[A-Z0-9._-]+\.md',rp): continue
            body=subprocess.check_output(['git','-C',str(REPO),'show',remote+':'+rp],text=True)
            if field(body,'WORKFLOW_ID')==wid and field(body,'BASE_IDENTITY')==base and field(body,'STATUS')!='COMPLETE':
                active_matches.append(rp)
        if active_matches!=[path]: errors.append('duplicate-or-mismatched-active-run:'+','.join(active_matches))
    head=subprocess.check_output(['git','-C',str(WS/'implement'),'rev-parse','HEAD'],text=True).strip()
    if head!=active.get('observed_local_head'): errors.append('active-run-local-head:'+head+'!='+str(active.get('observed_local_head')))
if errors:
    print('WORKFLOW_CONTINUITY_CHECK_FAIL');print('\n'.join(errors));raise SystemExit(1)
print('WORKFLOW_CONTINUITY_CHECK_PASS','state=V'+str(v),'run='+rid,'workflow='+wid,'step='+str(active.get('current_step')))
