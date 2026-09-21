#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re,sys
from check_state_contract import StateContractError, load_selected_state

ROOT=Path(__file__).resolve().parents[1]
EVENT_DIR=ROOT/'workflow-runs'/'continuity-events'
errors=[]

def canonical_event_hash(obj):
    payload={k:v for k,v in obj.items() if k not in {'event_id','event_identity_sha256'}}
    raw=json.dumps(payload,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()

def valid_evidence_list(value):
    if not isinstance(value,list) or not value:
        return False
    for item in value:
        if not isinstance(item,str) or not item or len(item)>240:
            return False
    return any(re.fullmatch(r'[0-9a-f]{40}',x) for x in value)

try:
    version,state_path,state=load_selected_state(ROOT)
except StateContractError as exc:
    print('CONTINUITY_MEASUREMENT_CHECK_FAIL',exc);raise SystemExit(1)
learning=json.loads((ROOT/'learning/LEARNING_STATE.json').read_text(encoding='utf-8'))
record=learning.get('records',{}).get('LEARNING-WORKFLOW-CONTINUITY-001')
if not isinstance(record,dict):
    errors.append('continuity-learning-record-missing')
    record={}
gate=record.get('measurement_gate') if isinstance(record.get('measurement_gate'),dict) else {}
if gate.get('kind')!='EVENT_COUNT_AT_LEAST' or gate.get('event_kind')!='INTERRUPTED_RESUME' or (type(gate.get('value')) is not int or gate.get('value',0)<=0):
    errors.append('continuity-learning-gate-invalid')
required=gate.get('value') if type(gate.get('value')) is int and gate['value']>0 else None

measurement=state.get('learning_activation',{}).get('continuity_measurement')
if not isinstance(measurement,dict):
    errors.append('continuity-measurement-state-missing')
    measurement={}

md_state=(ROOT/'PROJECT_STATE.md').read_text(encoding='utf-8')
def md_field(name):
    m=re.search(r'^\s*'+re.escape(name)+r':\s*(.*?)\s*$',md_state,re.M)
    if not m: return None
    value=m.group(1).strip()
    if len(value)>=2 and value[0]==value[-1]=='"': value=value[1:-1]
    return value

expected_domain='workflow-runs/continuity-events'
if measurement.get('event_domain')!=expected_domain:
    errors.append('continuity-event-domain-drift')
if measurement.get('event_kind')!='INTERRUPTED_RESUME':
    errors.append('continuity-event-kind-state-drift')
if required is not None and measurement.get('required_event_count')!=required:
    errors.append('continuity-required-count-drift')

md_parity={
    'CONTINUITY_EVENT_DOMAIN':measurement.get('event_domain'),
    'CONTINUITY_EVENT_KIND':measurement.get('event_kind'),
    'CONTINUITY_QUALIFYING_EVENT_COUNT':measurement.get('qualifying_event_count'),
    'CONTINUITY_REQUIRED_EVENT_COUNT':measurement.get('required_event_count'),
    'CONTINUITY_MEASUREMENT_STATUS':measurement.get('status'),
}
for name,value in md_parity.items():
    observed=md_field(name)
    if observed is None:
        errors.append('continuity-measurement-md-field-missing:'+name)
    elif str(value)!=observed:
        errors.append(f'continuity-measurement-md-parity:{name}:{value}!={observed}')

if not EVENT_DIR.is_dir() or not (EVENT_DIR/'README.md').is_file():
    errors.append('continuity-event-domain-missing')

required_keys={
    'schema_version','event_id','event_kind','run_id','workflow_id','owner_lane',
    'base_identity','interrupted_step','resumed_step','same_run_id','identity_changed',
    'duplicate_logical_runs','repeated_completed_expensive_steps','resume_disposition',
    'interruption_evidence','resume_evidence','event_identity_sha256','result',
    'measurement_eligible'
}
event_ids=set(); event_hashes=set(); qualifying=0
for path in sorted(EVENT_DIR.glob('*.json')) if EVENT_DIR.is_dir() else []:
    try:
        obj=json.loads(path.read_text(encoding='utf-8'))
    except (OSError,UnicodeError,json.JSONDecodeError):
        errors.append('continuity-event-json:'+path.name); continue
    if not isinstance(obj,dict) or set(obj)!=required_keys:
        errors.append('continuity-event-schema:'+path.name); continue
    eid=obj.get('event_id')
    if not isinstance(eid,str) or not re.fullmatch(r'CONTINUITY-EVENT-[A-Z0-9._-]{3,120}',eid):
        errors.append('continuity-event-id-schema:'+path.name)
    elif eid in event_ids:
        errors.append('continuity-event-id-duplicate:'+eid)
    else:
        event_ids.add(eid)
    if type(obj.get('schema_version')) is not int or obj.get('schema_version')!=1: errors.append('continuity-event-schema-version:'+path.name)
    if obj.get('event_kind')!='INTERRUPTED_RESUME': errors.append('continuity-event-kind:'+path.name)
    if not re.fullmatch(r'RUN-[A-Z0-9][A-Z0-9._-]{2,79}',str(obj.get('run_id',''))):
        errors.append('continuity-event-run-id:'+path.name)
    if not re.fullmatch(r'WF-[A-Z0-9][A-Z0-9._-]{2,99}',str(obj.get('workflow_id',''))):
        errors.append('continuity-event-workflow-id:'+path.name)
    if not re.fullmatch(r'[A-Z][A-Z0-9._-]{1,39}',str(obj.get('owner_lane',''))):
        errors.append('continuity-event-owner-lane:'+path.name)
    if not re.fullmatch(r'[0-9a-f]{40}',str(obj.get('base_identity',''))):
        errors.append('continuity-event-base:'+path.name)
    for key in ('interrupted_step','resumed_step'):
        if not isinstance(obj.get(key),str) or not re.fullmatch(r'[A-Z0-9][A-Z0-9._-]{1,99}',obj[key]):
            errors.append('continuity-event-step:'+path.name+':'+key)
    if type(obj.get('same_run_id')) is not bool:
        errors.append('continuity-event-same-run-schema:'+path.name)
    if type(obj.get('identity_changed')) is not bool:
        errors.append('continuity-event-identity-changed:'+path.name)
    duplicate_runs=obj.get('duplicate_logical_runs')
    if type(duplicate_runs) is not int or duplicate_runs<0:
        errors.append('continuity-event-duplicate-runs-schema:'+path.name)
    repeated=obj.get('repeated_completed_expensive_steps')
    if type(repeated) is not int or repeated<0:
        errors.append('continuity-event-repeat-schema:'+path.name)
    if obj.get('resume_disposition') not in {'REUSE_VERIFIED_OUTPUT','RECONCILE_AND_CONTINUE','SAFE_REEXECUTE_AFFECTED_STEP'}:
        errors.append('continuity-event-resume-disposition:'+path.name)
    if not valid_evidence_list(obj.get('interruption_evidence')):
        errors.append('continuity-event-interruption-evidence:'+path.name)
    if not valid_evidence_list(obj.get('resume_evidence')):
        errors.append('continuity-event-resume-evidence:'+path.name)
    calc=canonical_event_hash(obj)
    claimed=obj.get('event_identity_sha256')
    if claimed!=calc:
        errors.append('continuity-event-hash:'+path.name)
    elif calc in event_hashes:
        errors.append('continuity-event-identity-duplicate:'+path.name)
    else:
        event_hashes.add(calc)
    if obj.get('result') not in {'PASS','FAIL'}:
        errors.append('continuity-event-result:'+path.name)
    if type(obj.get('measurement_eligible')) is not bool:
        errors.append('continuity-event-eligible-schema:'+path.name)
    if obj.get('measurement_eligible') is True:
        if obj.get('result')!='PASS':
            errors.append('continuity-event-eligible-not-pass:'+path.name)
        else:
            if obj.get('same_run_id') is not True:
                errors.append('continuity-event-same-run:'+path.name)
            if duplicate_runs!=0:
                errors.append('continuity-event-duplicate-runs:'+path.name)
            if type(repeated) is int and repeated>0 and obj.get('identity_changed') is not True:
                errors.append('continuity-event-repeat-without-identity-change:'+path.name)
            if obj.get('same_run_id') is True and duplicate_runs==0 and (type(repeated) is not int or repeated==0 or obj.get('identity_changed') is True):
                qualifying+=1

declared=measurement.get('qualifying_event_count')
if type(declared) is not int or declared<0:
    errors.append('continuity-declared-count-schema')
if declared!=qualifying:
    errors.append(f'continuity-event-count-drift:{qualifying}!={declared}')
if required is not None:
    expected_status='READY_FOR_EFFECTIVENESS_REVIEW' if qualifying>=required else 'PENDING_MEASUREMENT'
    if record.get('effectiveness_status')=='EFFECTIVE':
        if qualifying<required:
            errors.append('continuity-effective-insufficient-events')
        expected_status='COMPLETE'
    if measurement.get('status')!=expected_status:
        errors.append(f'continuity-measurement-status:{measurement.get("status")}!={expected_status}')

if errors:
    print('CONTINUITY_MEASUREMENT_CHECK_FAIL')
    print('\n'.join(errors))
    raise SystemExit(1)
print('CONTINUITY_MEASUREMENT_CHECK_PASS',
      'state=V'+str(version),
      'qualifying='+str(qualifying),
      'required='+str(required),
      'status='+str(measurement.get('status')),
      'scope=STRUCTURAL_EVENT_COUNT','event_semantics=REVIEW_REQUIRED')
