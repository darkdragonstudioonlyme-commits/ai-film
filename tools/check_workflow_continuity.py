#!/usr/bin/env python3
from pathlib import Path
import argparse,json,re,subprocess,sys,os,hashlib
from check_state_contract import StateContractError, load_selected_state
ROOT=Path(__file__).resolve().parents[1]
WS=Path(os.environ.get('AIFILM_WORKSPACE_ROOT','/home/dragon/ai-film-dev'))
REPO=Path(os.environ.get('AIFILM_CONTROL_REPO',str(ROOT))); errors=[]
parser=argparse.ArgumentParser(description='Verify selected-state continuity with explicit evidence scope.')
scope=parser.add_mutually_exclusive_group()
scope.add_argument('--require-remote',action='store_true',help='Fail closed unless the active lane is freshly resolved.')
scope.add_argument('--schema-only',action='store_true',help='Only check portable state shape; never a handoff verdict.')
parser.add_argument('--require-local',action='store_true',help='Also require the bound local worktree head; implies remote verification.')
args=parser.parse_args()
if args.schema_only and args.require_local:
    parser.error('--schema-only cannot satisfy --require-local')

def field(text,name):
    m=re.search(r'(?m)^\s*'+re.escape(name)+r':\s*(.*?)\s*$',text)
    if not m: return None
    value=m.group(1).strip()
    if len(value)>=2 and value[0]==value[-1]=='"': value=value[1:-1]
    return value

try:
    v,_,state=load_selected_state(ROOT)
except StateContractError as exc:
    print('WORKFLOW_CONTINUITY_CHECK_FAIL',exc);raise SystemExit(1)
active=state.get('active_run')
if 'active_run' not in state or (active is not None and type(active) is not dict):
    print('WORKFLOW_CONTINUITY_CHECK_FAIL active-run-schema');raise SystemExit(1)
if active is None:
    print('WORKFLOW_CONTINUITY_CHECK_PASS scope=NO_ACTIVE_RUN state=V'+str(v)); raise SystemExit(0)
for k in ['run_id','workflow_id','owner_lane','run_record','status','current_step','canonical_base']:
    if not active.get(k): errors.append('active-run-field:'+k)
if 'local_worktree' not in active: errors.append('active-run-field:local_worktree')
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
local_rel=active.get('local_worktree')
worktree=None
if local_rel is not None:
    if not isinstance(local_rel,str) or not re.fullmatch(r'[A-Za-z0-9._-]+(?:/[A-Za-z0-9._-]+)*',local_rel) or '..' in Path(local_rel).parts:
        errors.append('active-run-worktree-schema')
    else:
        worktree=WS/local_rel
        try:
            if not worktree.resolve().is_relative_to(WS.resolve()): errors.append('active-run-worktree-scope')
        except OSError: errors.append('active-run-worktree-scope')
snap=active.get('canonical_snapshot')
if snap and not (ROOT/snap).is_file(): errors.append('active-run-snapshot-missing')
remote_checked=False
local_checked=False
lane_head=None
repo_available=False
if REPO.is_dir() and not args.schema_only:
    probe=subprocess.run(['git','-C',str(REPO),'rev-parse','--git-dir'],capture_output=True,text=True,timeout=10)
    repo_available=probe.returncode==0
if (args.require_remote or args.require_local) and not repo_available:
    errors.append('remote-reconciliation-unavailable')
if repo_available and ':' in record_locator and not errors:
    branch,path=record_locator.split(':',1)
    try:
        # Read one fresh immutable lane identity; never trust cached tracking refs or
        # a mutable FETCH_HEAD shared with another worktree.
        wanted='refs/heads/'+branch
        rows=subprocess.check_output(['git','-C',str(REPO),'ls-remote','--exit-code','origin',wanted],text=True,stderr=subprocess.DEVNULL,timeout=30).splitlines()
        if len(rows)!=1 or rows[0].split()[1]!=wanted or not re.fullmatch(r'[0-9a-f]{40}',rows[0].split()[0]):
            raise ValueError('ambiguous-lane-ref')
        lane_head=rows[0].split()[0]
        known=subprocess.run(['git','-C',str(REPO),'cat-file','-e',lane_head+'^{commit}'],capture_output=True,timeout=10)
        if known.returncode:
            subprocess.check_call(['git','-C',str(REPO),'fetch','--no-tags','--no-write-fetch-head','origin',lane_head],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=30)
        remote=lane_head
        remote_checked=True
    except (OSError,ValueError,IndexError,subprocess.SubprocessError) as exc:
        print('WORKFLOW_CONTINUITY_CHECK_FAIL remote-lane-fetch:'+type(exc).__name__);raise SystemExit(1)
    try: lane=subprocess.check_output(['git','-C',str(REPO),'show',remote+':LANE_STATE.md'],text=True)
    except subprocess.CalledProcessError: lane=''; errors.append('lane-state-missing')
    if lane:
        for token in [rid,path,active.get('current_step','')]:
            if token and token not in lane: errors.append('lane-active-run-token:'+str(token))
    try: record=subprocess.check_output(['git','-C',str(REPO),'show',remote+':'+path],text=True)
    except subprocess.CalledProcessError: record=''; errors.append('lane-run-record-missing')
    if record:
        required={'RUN_ID':rid,'WORKFLOW_ID':wid,'BASE_IDENTITY':base,'CURRENT_STEP':str(active.get('current_step','')),'STATUS':str(active.get('status',''))}
        for name,value in required.items():
            if field(record,name)!=value: errors.append('lane-run-field:'+name)
        expected_worktree=local_rel if local_rel is not None else 'NONE'
        if field(record,'WORKTREE_REL')!=expected_worktree: errors.append('lane-run-field:WORKTREE_REL')
        local_head=active.get('observed_local_head')
        if local_rel is not None:
            if not re.fullmatch(r'[0-9a-f]{40}',str(local_head or '')): errors.append('active-run-local-head-schema')
            elif str(local_head) not in record: errors.append('lane-run-output-head')
        elif local_head is not None:
            errors.append('remote-only-run-has-local-head')
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
        if step_state=='COMPLETE' and (not isinstance(output_obj,dict) or not output_obj): errors.append('current-step-complete-output-missing')
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
    if worktree is not None:
        if not worktree.is_dir():
            if args.require_local: errors.append('active-run-worktree-missing:'+str(worktree))
        else:
            head=subprocess.check_output(['git','-C',str(worktree),'rev-parse','HEAD'],text=True,timeout=10).strip()
            local_checked=True
            if head!=active.get('observed_local_head'): errors.append('active-run-local-head:'+head+'!='+str(active.get('observed_local_head')))
if args.require_local and worktree is None:
    errors.append('local-worktree-not-bound')
if errors:
    print('WORKFLOW_CONTINUITY_CHECK_FAIL');print('\n'.join(errors));raise SystemExit(1)
if not remote_checked:
    print('WORKFLOW_CONTINUITY_SCHEMA_ONLY','state=V'+str(v),'remote=NOT_EVALUATED','local=NOT_EVALUATED','NOT_HANDOFF_EVIDENCE')
else:
    print('WORKFLOW_CONTINUITY_CHECK_PASS','scope=REMOTE_LEDGER','state=V'+str(v),'run='+rid,'workflow='+wid,'step='+str(active.get('current_step')),'lane_head='+str(lane_head),'local='+('HEAD_IDENTITY_VERIFIED' if local_checked else ('NOT_APPLICABLE_REMOTE_ONLY' if local_rel is None else 'NOT_EVALUATED')),'native=NOT_EVALUATED')
