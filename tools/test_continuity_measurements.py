#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re,shutil,subprocess,sys,tempfile
from check_state_contract import load_selected_state

ROOT=Path(__file__).resolve().parents[1]

def latest_state_path(root):
    return load_selected_state(root)[1]

def event_hash(obj):
    payload={k:v for k,v in obj.items() if k not in {'event_identity_sha256','event_id'}}
    raw=json.dumps(payload,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()

def make_event(n=1, *, identity_changed=False, repeated=0, duplicate_runs=0,
               same_run=True, result='PASS', eligible=True):
    obj={
      'schema_version':1,
      'event_id':f'CONTINUITY-EVENT-TEST-{n:03d}',
      'event_kind':'INTERRUPTED_RESUME',
      'run_id':'RUN-P00-VALIDATION-001',
      'workflow_id':'WF-P00-VALIDATION-ENTRY',
      'owner_lane':'VALIDATION',
      'base_identity':'934659f535d81d9a4a07389531acc2b9c304fa6d',
      'interrupted_step':'V02_LAB_EXECUTION_AUTHORITY',
      'resumed_step':f'V02_LAB_EXECUTION_AUTHORITY_{n:03d}',
      'same_run_id':same_run,
      'identity_changed':identity_changed,
      'duplicate_logical_runs':duplicate_runs,
      'repeated_completed_expensive_steps':repeated,
      'resume_disposition':'SAFE_REEXECUTE_AFFECTED_STEP' if identity_changed else 'RECONCILE_AND_CONTINUE',
      'interruption_evidence':['a'*39+str(n%10),'workflow-runs/snapshots/example.md'],
      'resume_evidence':['b'*39+str(n%10),'workflow-runs/snapshots/example.md'],
      'event_identity_sha256':'',
      'result':result,
      'measurement_eligible':eligible,
    }
    obj['event_identity_sha256']=event_hash(obj)
    return obj

def set_measurement(root,count,status):
    p=latest_state_path(root)
    state=json.loads(p.read_text(encoding='utf-8'))
    m=state['learning_activation']['continuity_measurement']
    m['qualifying_event_count']=count
    m['status']=status
    p.write_text(json.dumps(state,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    md=root/'PROJECT_STATE.md'
    text=md.read_text(encoding='utf-8')
    text=re.sub(r'(?m)^(\s*CONTINUITY_QUALIFYING_EVENT_COUNT:)\s*\d+\s*$',rf'\1 {count}',text)
    text=re.sub(r'(?m)^(\s*CONTINUITY_MEASUREMENT_STATUS:)\s*\S+\s*$',rf'\1 {status}',text)
    md.write_text(text,encoding='utf-8')

def write_event(root,obj,name=None):
    d=root/'workflow-runs'/'continuity-events'
    d.mkdir(parents=True,exist_ok=True)
    path=d/(name or (obj['event_id']+'.json'))
    path.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n',encoding='utf-8')

def run_case(mutator=None):
    with tempfile.TemporaryDirectory(prefix='aifilm-continuity-measure-') as td:
        dst=Path(td)/'repo'
        shutil.copytree(ROOT,dst,ignore=shutil.ignore_patterns('.git','__pycache__'))
        if mutator: mutator(dst)
        return subprocess.run([sys.executable,str(dst/'tools/check_continuity_measurements.py')],
                              cwd=dst,text=True,capture_output=True)

def require(name,proc,should_pass,needle=None):
    out=(proc.stdout or '')+(proc.stderr or '')
    ok=proc.returncode==0
    if ok!=should_pass or (needle and needle not in out):
        print('FAIL',name); print(out); raise SystemExit(1)
    print('PASS',name)

require('baseline_zero_events',run_case(),True,'qualifying=0')

def one_event_no_aggregate(dst):
    write_event(dst,make_event(1))
require('count_drift',run_case(one_event_no_aggregate),False,'continuity-event-count-drift:1!=0')

def one_event_reconciled(dst):
    write_event(dst,make_event(1)); set_measurement(dst,1,'PENDING_MEASUREMENT')
require('one_event_reconciled',run_case(one_event_reconciled),True,'qualifying=1')

def semantic_duplicate(dst):
    a=make_event(1); b=dict(a); b['event_id']='CONTINUITY-EVENT-TEST-DUP'; b['event_identity_sha256']=event_hash(b)
    write_event(dst,a); write_event(dst,b); set_measurement(dst,2,'PENDING_MEASUREMENT')
require('semantic_duplicate',run_case(semantic_duplicate),False,'continuity-event-identity-duplicate')

def duplicate_run(dst):
    e=make_event(1,duplicate_runs=1); write_event(dst,e); set_measurement(dst,1,'PENDING_MEASUREMENT')
require('duplicate_logical_run',run_case(duplicate_run),False,'continuity-event-duplicate-runs')

def repeated_without_change(dst):
    e=make_event(1,repeated=1); write_event(dst,e); set_measurement(dst,1,'PENDING_MEASUREMENT')
require('repeat_without_identity_change',run_case(repeated_without_change),False,'continuity-event-repeat-without-identity-change')

def repeated_with_change(dst):
    e=make_event(1,repeated=1,identity_changed=True); write_event(dst,e); set_measurement(dst,1,'PENDING_MEASUREMENT')
require('repeat_with_identity_change',run_case(repeated_with_change),True,'qualifying=1')

def different_run(dst):
    e=make_event(1,same_run=False); write_event(dst,e); set_measurement(dst,1,'PENDING_MEASUREMENT')
require('same_run_required',run_case(different_run),False,'continuity-event-same-run')

def tampered_hash(dst):
    e=make_event(1); e['resumed_step']='V02_TAMPERED'; write_event(dst,e); set_measurement(dst,1,'PENDING_MEASUREMENT')
require('tamper_hash',run_case(tampered_hash),False,'continuity-event-hash')

def three_events_wrong_status(dst):
    for i in range(1,4): write_event(dst,make_event(i))
    set_measurement(dst,3,'PENDING_MEASUREMENT')
require('three_events_require_ready_status',run_case(three_events_wrong_status),False,'READY_FOR_EFFECTIVENESS_REVIEW')

def three_events_ready(dst):
    for i in range(1,4): write_event(dst,make_event(i))
    set_measurement(dst,3,'READY_FOR_EFFECTIVENESS_REVIEW')
require('three_events_ready',run_case(three_events_ready),True,'qualifying=3')

def failed_event_preserved(dst):
    e=make_event(1,same_run=False,duplicate_runs=1,repeated=1,result='FAIL',eligible=False)
    write_event(dst,e); set_measurement(dst,0,'PENDING_MEASUREMENT')
require('failed_event_preserved_not_counted',run_case(failed_event_preserved),True,'qualifying=0')


def bool_counter(dst):
    e=make_event(1); e['duplicate_logical_runs']=False; e['event_identity_sha256']=event_hash(e)
    write_event(dst,e); set_measurement(dst,1,'PENDING_MEASUREMENT')
require('boolean_not_count',run_case(bool_counter),False,'continuity-event-duplicate-runs-schema')

def bool_declared(dst):
    set_measurement(dst,0,'PENDING_MEASUREMENT')
    p=latest_state_path(dst); data=json.loads(p.read_text());data['learning_activation']['continuity_measurement']['qualifying_event_count']=False;p.write_text(json.dumps(data))
require('boolean_not_declared_count',run_case(bool_declared),False,'continuity-declared-count-schema')

def invalid_gate(dst):
    p=dst/'learning/LEARNING_STATE.json';data=json.loads(p.read_text());data['records']['LEARNING-WORKFLOW-CONTINUITY-001']['measurement_gate']['value']=0;p.write_text(json.dumps(data))
require('nonpositive_sample_requirement',run_case(invalid_gate),False,'continuity-learning-gate-invalid')

def unearned_effective(dst):
    p=dst/'learning/LEARNING_STATE.json';data=json.loads(p.read_text());data['records']['LEARNING-WORKFLOW-CONTINUITY-001']['effectiveness_status']='EFFECTIVE';p.write_text(json.dumps(data));set_measurement(dst,0,'COMPLETE')
require('effective_requires_samples',run_case(unearned_effective),False,'continuity-effective-insufficient-events')

print('ADVERSARIAL_CONTINUITY_MEASUREMENT_TEST_PASS 16 cases')
