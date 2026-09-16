#!/usr/bin/env python3
"""Fail-closed reconciliation of immutable learning evidence and current lifecycle state."""
from pathlib import Path
import json,re,sys

ROOT=Path(__file__).resolve().parents[1]
errors=[]

def err(msg): errors.append(msg)

def read(path):
    p=ROOT/path
    if not p.is_file(): err(f"missing:{path}"); return ""
    return p.read_text(encoding="utf-8")

state_text=read("PROJECT_STATE.md")
state_match=re.search(r"^STATE_VERSION: (\d+)$",state_text,re.M)
docsys_match=re.search(r"^DOCUMENTATION_SYSTEM: (\S+)$",state_text,re.M)
if not state_match: err("project-state-version-missing")
if not docsys_match: err("project-documentation-system-missing")
current_docsys=docsys_match.group(1) if docsys_match else ""

reg_path=ROOT/"learning/LEARNING_STATE.json"
try:
    register=json.loads(reg_path.read_text(encoding="utf-8"))
except Exception as exc:
    print("LEARNING_LIFECYCLE_CHECK_FAIL")
    print(f"register-invalid:{type(exc).__name__}")
    raise SystemExit(1)

if register.get("schema_version")!=1: err("register-schema-version")
records=register.get("records")
if not isinstance(records,dict) or not records: err("register-records-empty"); records={}

# Every durable active learning record is represented exactly once.
md_records={p.stem:p for p in (ROOT/"learning").glob("LEARNING-*.md")}
for learning_id,p in sorted(md_records.items()):
    if learning_id not in records: err(f"learning-unregistered:{learning_id}")
for learning_id,row in sorted(records.items()):
    if not isinstance(row,dict): err(f"learning-row-not-object:{learning_id}"); continue
    path=row.get("record")
    if not isinstance(path,str) or not (ROOT/path).is_file():
        err(f"learning-record-missing:{learning_id}"); continue
    text=(ROOT/path).read_text(encoding="utf-8")
    if f"LEARNING_ID: {learning_id}" not in text: err(f"learning-id-mismatch:{learning_id}")
    if row.get("score") not in range(0,11): err(f"learning-score:{learning_id}")
    for key in ("activation_target","review_status","activation_status","effectiveness_status","success_metric","measurement_trigger"):
        if not row.get(key): err(f"learning-field-missing:{learning_id}:{key}")

valid_review={"PASS","PASS_ON_FINAL_REVIEW","PENDING_REVIEW","BLOCKED"}
valid_activation={"PENDING_ACTIVATION","BLOCKED","ACTIVE","ACTIVE_ON_PROMOTION","SUPERSEDED","RETIRED"}
valid_effectiveness={"PENDING_MEASUREMENT","EFFECTIVE","INEFFECTIVE","SUPERSEDED","RETIRED"}

for learning_id,row in sorted(records.items()):
    if not isinstance(row,dict): continue
    rv=row.get("review_status"); av=row.get("activation_status"); ev=row.get("effectiveness_status")
    if rv not in valid_review: err(f"learning-review-status:{learning_id}:{rv}")
    if av not in valid_activation: err(f"learning-activation-status:{learning_id}:{av}")
    if ev not in valid_effectiveness: err(f"learning-effectiveness-status:{learning_id}:{ev}")
    target=row.get("activation_target")
    blocker=row.get("activation_blocker")
    activated=row.get("activated_in")
    if av=="ACTIVE":
        if rv!="PASS": err(f"active-without-pass:{learning_id}")
        if activated!=target: err(f"active-release-mismatch:{learning_id}")
        if blocker not in (None,""): err(f"active-has-blocker:{learning_id}")
    if av=="ACTIVE_ON_PROMOTION":
        if rv!="PASS_ON_FINAL_REVIEW": err(f"promotion-active-without-final-review-contract:{learning_id}")
        if target!=current_docsys: err(f"promotion-target-not-current-tree:{learning_id}")
        review_record=row.get("review_record")
        if not review_record or review_record not in state_text: err(f"promotion-review-not-predeclared:{learning_id}")
    if av in {"PENDING_ACTIVATION","BLOCKED"} and target==current_docsys:
        err(f"stale-current-release-activation:{learning_id}")
    if av=="BLOCKED" and not blocker: err(f"blocked-without-blocker:{learning_id}")
    evidence=row.get("effectiveness_evidence")
    if not isinstance(evidence,list): err(f"effectiveness-evidence-schema:{learning_id}")
    if ev=="EFFECTIVE" and not evidence: err(f"effective-without-evidence:{learning_id}")
    if ev=="INEFFECTIVE":
        successor=row.get("successor")
        if not successor or successor not in records: err(f"ineffective-without-successor:{learning_id}")

# Derive aggregate process debt.
pending_activation=sum(1 for r in records.values() if r.get("activation_status") in {"PENDING_ACTIVATION","BLOCKED"})
unresolved_ineffective=0
for r in records.values():
    if r.get("effectiveness_status")!="INEFFECTIVE": continue
    successor=records.get(r.get("successor"),{})
    if successor.get("activation_status") not in {"ACTIVE","ACTIVE_ON_PROMOTION"}:
        unresolved_ineffective+=1
pending_measurement=sum(1 for r in records.values() if r.get("effectiveness_status")=="PENDING_MEASUREMENT")

def state_int(name):
    m=re.search(rf"^\s*{re.escape(name)}:\s*(\d+)\s*$",state_text,re.M)
    if not m: err(f"project-learning-aggregate-missing:{name}"); return None
    return int(m.group(1))

# Promotion-ready tree owns intended post-promotion aggregates.
expected_pending=state_int("LEARNED_BUT_NOT_ACTIVE_BACKLOG")
expected_ineffective=state_int("UNRESOLVED_INEFFECTIVE_LEARNING")
expected_measure=state_int("PENDING_EFFECTIVENESS_MEASUREMENT")
if expected_pending is not None and expected_pending!=pending_activation:
    err(f"learning-backlog-drift:{expected_pending}!={pending_activation}")
if expected_ineffective is not None and expected_ineffective!=unresolved_ineffective:
    err(f"learning-ineffective-drift:{expected_ineffective}!={unresolved_ineffective}")
if expected_measure is not None and expected_measure!=pending_measurement:
    err(f"learning-measurement-drift:{expected_measure}!={pending_measurement}")

if errors:
    print("LEARNING_LIFECYCLE_CHECK_FAIL")
    for e in errors: print(e)
    raise SystemExit(1)
print("LEARNING_LIFECYCLE_CHECK_PASS",len(records),"records",
      f"pending_activation={pending_activation}",
      f"unresolved_ineffective={unresolved_ineffective}",
      f"pending_measurement={pending_measurement}")
