#!/usr/bin/env python3
"""Fail-closed reconciliation of immutable learning evidence and current lifecycle state."""
from pathlib import Path
import hashlib,json,os,re,subprocess,sys

ROOT=Path(__file__).resolve().parents[1]
errors=[]

def err(msg): errors.append(msg)
def read(path):
    p=ROOT/path
    if not p.is_file(): err(f"missing:{path}"); return ""
    return p.read_text(encoding="utf-8")
def field(text,name):
    m=re.search(rf"^\s*{re.escape(name)}:\s*(.*?)\s*$",text,re.M)
    if not m: return None
    value=m.group(1).strip()
    if len(value)>=2 and value[0]==value[-1]=='"': value=value[1:-1]
    return value
def state_str(name):
    v=field(state_text,name)
    if v is None: err(f"project-state-field-missing:{name}")
    return v
def norm(text): return " ".join(str(text).split())
def immutable_metric(text):
    m=re.search(r'^SUCCESS_METRIC:\s*"(.*?)"\s*$',text,re.M)
    if m: return norm(m.group(1))
    m=re.search(r'^SUCCESS_METRIC:\s*(.+?)\s*$',text,re.M)
    if m: return norm(m.group(1).strip('"'))
    m=re.search(r'^## Success metric\s*\n\s*(.+?)(?=\n## |\Z)',text,re.M|re.S)
    if m: return norm(m.group(1))
    return None
def metric_hash(metric): return hashlib.sha256(metric.encode('utf-8')).hexdigest()
def current_branch():
    forced=os.environ.get('AIFILM_DOCSYS_ROLE')
    if forced: return None,forced.upper()
    branch=os.environ.get('GITHUB_REF_NAME')
    if not branch:
        try:
            branch=subprocess.check_output(['git','-C',str(ROOT),'branch','--show-current'],text=True,stderr=subprocess.DEVNULL).strip()
        except Exception:
            branch=''
    role='GENERIC'
    if branch and branch==design_branch: role='DESIGN'
    elif branch and branch==review_branch: role='REVIEW'
    elif branch and branch==audit_branch: role='AUDIT'
    elif branch in {'main','master'}: role='PROMOTED'
    return branch or None,role

def validate_review(path):
    if not path or not path.is_file(): err('final-review-missing'); return None
    text=path.read_text(encoding='utf-8')
    for token in (f"REVIEW_ID: {final_review_id}",f"TARGET_RELEASE: {current_docsys}","VERDICT: PASS"):
        if token not in text: err(f"final-review-invalid:{token}")
    m=re.search(r"^TARGET_DESIGN_COMMIT:\s*([0-9a-f]{40})$",text,re.M)
    if not m: err('final-review-target-missing'); return None
    return m.group(1)
def validate_audit(path):
    if not path or not path.is_file(): err('final-audit-missing'); return None
    text=path.read_text(encoding='utf-8')
    for token in (f"AUDIT_ID: {final_audit_id}",f"TARGET_RELEASE: {current_docsys}",f"REQUIRED_REVIEW_ID: {final_review_id}","VERDICT: PASS"):
        if token not in text: err(f"final-audit-invalid:{token}")
    m=re.search(r"^TARGET_DESIGN_COMMIT:\s*([0-9a-f]{40})$",text,re.M)
    if not m: err('final-audit-target-missing'); return None
    return m.group(1)

def receipt_fields(text):
    keys=['LEARNING_ID','METRIC_ID','METRIC_VERSION','SUCCESS_METRIC_SHA256','SCOPE','SAMPLE_REQUIREMENT','OBSERVATIONS','EXPECTED_PREDICATE','MEASUREMENT_COMMIT','RESULT','REVIEW_ID']
    return {k:field(text,k) for k in keys}

state_text=read("PROJECT_STATE.md")
state_match=re.search(r"^STATE_VERSION: (\d+)$",state_text,re.M)
docsys_match=re.search(r"^DOCUMENTATION_SYSTEM: (\S+)$",state_text,re.M)
if not state_match: err("project-state-version-missing")
if not docsys_match: err("project-documentation-system-missing")
state_version=int(state_match.group(1)) if state_match else -1
current_docsys=docsys_match.group(1) if docsys_match else ""
design_branch=state_str('DESIGN_BRANCH')
review_branch=state_str('REVIEW_BRANCH')
audit_branch=state_str('AUDIT_BRANCH')
final_review_id=state_str("FINAL_REVIEW_ID")
final_review_record=state_str("FINAL_REVIEW_RECORD")
final_audit_id=state_str("FINAL_AUDIT_ID")
final_audit_record=state_str("FINAL_AUDIT_RECORD")
branch,role=current_branch()
review_path=ROOT/final_review_record if final_review_record else None
audit_path=ROOT/final_audit_record if final_audit_record else None
review_exists=bool(review_path and review_path.is_file())
audit_exists=bool(audit_path and audit_path.is_file())
promotion_resolved=False
promotion_target=None

# Stage-aware verdict invariants. GENERIC retains strict promoted-tree semantics for copied/adversarial fixtures.
if role=='DESIGN':
    if review_exists or audit_exists: err('design-stage-has-verdict-artifact')
elif role=='REVIEW':
    if not review_exists: err('review-stage-review-missing')
    if audit_exists: err('review-stage-premature-audit')
    promotion_target=validate_review(review_path)
elif role in {'AUDIT','PROMOTED'}:
    if not review_exists or not audit_exists: err('promotion-verdict-set-incomplete')
    rm=validate_review(review_path); am=validate_audit(audit_path)
    if rm and am and rm!=am: err('promotion-target-design-mismatch')
    else: promotion_target=rm or am; promotion_resolved=bool(rm and am)
else:
    if review_exists != audit_exists:
        err('partial-promotion-verdict-set')
    elif review_exists and audit_exists:
        rm=validate_review(review_path); am=validate_audit(audit_path)
        if rm and am and rm!=am: err('promotion-target-design-mismatch')
        else: promotion_target=rm or am; promotion_resolved=bool(rm and am)

reg_path=ROOT/"learning/LEARNING_STATE.json"
try:
    register=json.loads(reg_path.read_text(encoding="utf-8"))
except Exception as exc:
    print("LEARNING_LIFECYCLE_CHECK_FAIL")
    print(f"register-invalid:{type(exc).__name__}")
    raise SystemExit(1)
if register.get("schema_version")!=1: err("register-schema-version")
if register.get("candidate_documentation_release")!=current_docsys: err("register-documentation-release-drift")
records=register.get("records")
if not isinstance(records,dict) or not records: err("register-records-empty"); records={}

md_records={p.stem:p for p in (ROOT/"learning").glob("LEARNING-*.md")}
for learning_id,p in sorted(md_records.items()):
    if learning_id not in records: err(f"learning-unregistered:{learning_id}")
for learning_id,row in sorted(records.items()):
    if not isinstance(row,dict): err(f"learning-row-not-object:{learning_id}"); continue
    path=row.get("record")
    if not isinstance(path,str) or not (ROOT/path).is_file(): err(f"learning-record-missing:{learning_id}"); continue
    text=(ROOT/path).read_text(encoding="utf-8")
    if f"LEARNING_ID: {learning_id}" not in text: err(f"learning-id-mismatch:{learning_id}")
    if row.get("score") not in range(0,11): err(f"learning-score:{learning_id}")
    metric=immutable_metric(text)
    if not metric: err(f"immutable-success-metric-missing:{learning_id}")
    elif norm(row.get('success_metric',''))!=metric: err(f"success-metric-drift:{learning_id}")
    for key in ("activation_target","review_status","activation_status","effectiveness_status","success_metric","measurement_trigger"):
        if not row.get(key): err(f"learning-field-missing:{learning_id}:{key}")
    if not isinstance(row.get("activation_evidence"),list): err(f"activation-evidence-schema:{learning_id}")
    if not isinstance(row.get("measurement_gate"),dict): err(f"measurement-gate-schema:{learning_id}")

valid_review={"PASS","PASS_ON_FINAL_REVIEW","PENDING_REVIEW","BLOCKED"}
valid_activation={"PENDING_ACTIVATION","BLOCKED","ACTIVE","ACTIVE_ON_PROMOTION","SUPERSEDED","RETIRED"}
valid_effectiveness={"PENDING_MEASUREMENT","EFFECTIVE","INEFFECTIVE","SUPERSEDED","RETIRED"}
for learning_id,row in sorted(records.items()):
    if not isinstance(row,dict): continue
    rv=row.get("review_status"); av=row.get("activation_status"); ev=row.get("effectiveness_status")
    if rv not in valid_review: err(f"learning-review-status:{learning_id}:{rv}")
    if av not in valid_activation: err(f"learning-activation-status:{learning_id}:{av}")
    if ev not in valid_effectiveness: err(f"learning-effectiveness-status:{learning_id}:{ev}")
    target=row.get("activation_target"); blocker=row.get("activation_blocker"); activated=row.get("activated_in")
    activation_evidence=row.get("activation_evidence") if isinstance(row.get("activation_evidence"),list) else []
    if av=="ACTIVE":
        if rv!="PASS": err(f"active-without-pass:{learning_id}")
        if activated!=target: err(f"active-release-mismatch:{learning_id}")
        if blocker not in (None,""): err(f"active-has-blocker:{learning_id}")
        if not activation_evidence: err(f"active-without-activation-evidence:{learning_id}")
        for evidence_path in activation_evidence:
            if not isinstance(evidence_path,str) or not (ROOT/evidence_path).is_file(): err(f"active-activation-evidence-missing:{learning_id}:{evidence_path}")
    if av=="ACTIVE_ON_PROMOTION":
        if rv!="PASS_ON_FINAL_REVIEW": err(f"promotion-active-without-final-review-contract:{learning_id}")
        if target!=current_docsys: err(f"promotion-target-not-current-tree:{learning_id}")
        rr=row.get("review_record")
        if not rr or rr!=final_review_record: err(f"promotion-review-record-mismatch:{learning_id}")
        if rr not in activation_evidence or final_audit_record not in activation_evidence: err(f"promotion-verdict-evidence-incomplete:{learning_id}")
        if promotion_resolved:
            if activated!=target: err(f"promotion-activated-release-mismatch:{learning_id}")
            if blocker not in (None,""): err(f"promotion-active-has-blocker:{learning_id}")
    if av in {"PENDING_ACTIVATION","BLOCKED"} and target==current_docsys: err(f"stale-current-release-activation:{learning_id}")
    if av=="BLOCKED" and not blocker: err(f"blocked-without-blocker:{learning_id}")

    evidence=row.get("effectiveness_evidence")
    if not isinstance(evidence,list): err(f"effectiveness-evidence-schema:{learning_id}"); evidence=[]
    if ev=="EFFECTIVE":
        if not evidence: err(f"effective-without-evidence:{learning_id}")
        receipt=row.get('effectiveness_receipt')
        if not isinstance(receipt,str) or not receipt: err(f"effective-without-receipt:{learning_id}")
        elif not (ROOT/receipt).is_file(): err(f"effectiveness-receipt-missing:{learning_id}:{receipt}")
        else:
            rt=(ROOT/receipt).read_text(encoding='utf-8'); rf=receipt_fields(rt)
            source_text=(ROOT/row['record']).read_text(encoding='utf-8'); metric=immutable_metric(source_text) or ''
            if rf['LEARNING_ID']!=learning_id: err(f"receipt-learning-id:{learning_id}")
            if rf['SUCCESS_METRIC_SHA256']!=metric_hash(metric): err(f"receipt-metric-hash:{learning_id}")
            if rf['RESULT']!='PASS': err(f"receipt-result:{learning_id}:{rf['RESULT']}")
            if any(not rf[k] for k in ('METRIC_ID','METRIC_VERSION','SCOPE','SAMPLE_REQUIREMENT','OBSERVATIONS','EXPECTED_PREDICATE','MEASUREMENT_COMMIT','REVIEW_ID')): err(f"receipt-semantic-fields:{learning_id}")
            if rf['MEASUREMENT_COMMIT'] and not re.fullmatch(r'[0-9a-f]{40}',rf['MEASUREMENT_COMMIT']): err(f"receipt-measurement-commit:{learning_id}")
            for evidence_path in evidence:
                if not isinstance(evidence_path,str) or not (ROOT/evidence_path).is_file(): err(f"effective-evidence-missing:{learning_id}:{evidence_path}")
                elif evidence_path not in rt: err(f"receipt-evidence-binding:{learning_id}:{evidence_path}")
    elif ev=="INEFFECTIVE":
        if not evidence: err(f"ineffective-without-evidence:{learning_id}")
        for evidence_path in evidence:
            if not isinstance(evidence_path,str) or not (ROOT/evidence_path).is_file(): err(f"ineffective-evidence-missing:{learning_id}:{evidence_path}")
        successor=row.get("successor")
        if not successor or successor not in records: err(f"ineffective-without-successor:{learning_id}")
    if ev=="PENDING_MEASUREMENT" and av not in {"ACTIVE","ACTIVE_ON_PROMOTION"}: err(f"pending-measurement-before-activation:{learning_id}")
    gate=row.get("measurement_gate")
    if isinstance(gate,dict):
        kind=gate.get("kind")
        if ev=="PENDING_MEASUREMENT":
            if kind=="STATE_VERSION_AT_LEAST" and not isinstance(gate.get("value"),int): err(f"pending-measurement-gate-invalid:{learning_id}")
            elif kind=="NEXT_QUALIFYING_EVENT" and not isinstance(gate.get('event_kind'),str): err(f"pending-measurement-gate-invalid:{learning_id}")
            elif kind=="EVENT_COUNT_AT_LEAST" and (not isinstance(gate.get('event_kind'),str) or not isinstance(gate.get('value'),int) or gate.get('value',0)<1): err(f"pending-measurement-gate-invalid:{learning_id}")
            elif kind not in {"STATE_VERSION_AT_LEAST","NEXT_QUALIFYING_EVENT","EVENT_COUNT_AT_LEAST"}: err(f"pending-measurement-gate-invalid:{learning_id}")
        elif kind not in {"COMPLETE","STATE_VERSION_AT_LEAST","NEXT_QUALIFYING_EVENT","EVENT_COUNT_AT_LEAST"}: err(f"measurement-gate-kind:{learning_id}:{kind}")

pending_activation=sum(1 for r in records.values() if r.get("activation_status") in {"PENDING_ACTIVATION","BLOCKED"})
unresolved_ineffective=0
for r in records.values():
    if r.get("effectiveness_status")!="INEFFECTIVE": continue
    successor=records.get(r.get("successor"),{})
    if successor.get("activation_status") not in {"ACTIVE","ACTIVE_ON_PROMOTION"}: unresolved_ineffective+=1
pending_measurement=sum(1 for r in records.values() if r.get("effectiveness_status")=="PENDING_MEASUREMENT")
overdue_measurement=0
for r in records.values():
    if r.get("effectiveness_status")!="PENDING_MEASUREMENT": continue
    gate=r.get("measurement_gate",{})
    if gate.get("kind")=="STATE_VERSION_AT_LEAST" and isinstance(gate.get("value"),int) and state_version>=gate["value"]: overdue_measurement+=1

def state_int(name):
    m=re.search(rf"^\s*{re.escape(name)}:\s*(\d+)\s*$",state_text,re.M)
    if not m: err(f"project-learning-aggregate-missing:{name}"); return None
    return int(m.group(1))
expected_pending=state_int("LEARNED_BUT_NOT_ACTIVE_BACKLOG")
expected_ineffective=state_int("UNRESOLVED_INEFFECTIVE_LEARNING")
expected_measure=state_int("PENDING_EFFECTIVENESS_MEASUREMENT")
expected_overdue=state_int("OVERDUE_EFFECTIVENESS_MEASUREMENT")
if expected_pending is not None and expected_pending!=pending_activation: err(f"learning-backlog-drift:{expected_pending}!={pending_activation}")
if expected_ineffective is not None and expected_ineffective!=unresolved_ineffective: err(f"learning-ineffective-drift:{expected_ineffective}!={unresolved_ineffective}")
if expected_measure is not None and expected_measure!=pending_measurement: err(f"learning-measurement-drift:{expected_measure}!={pending_measurement}")
if expected_overdue is not None and expected_overdue!=overdue_measurement: err(f"learning-overdue-measurement-drift:{expected_overdue}!={overdue_measurement}")
if errors:
    print("LEARNING_LIFECYCLE_CHECK_FAIL")
    for e in errors: print(e)
    raise SystemExit(1)
print("LEARNING_LIFECYCLE_CHECK_PASS",len(records),"records",
      f"role={role}",f"branch={branch or 'UNKNOWN'}",f"pending_activation={pending_activation}",
      f"unresolved_ineffective={unresolved_ineffective}",f"pending_measurement={pending_measurement}",
      f"overdue_measurement={overdue_measurement}",f"promotion_evidence={'resolved' if promotion_resolved else 'predeclared'}",
      f"promotion_target={promotion_target or 'PENDING'}")
