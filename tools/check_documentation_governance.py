#!/usr/bin/env python3
"""Portable documentation-governance invariants for the active DOCSYS release."""
from pathlib import Path
import re,subprocess,sys

ROOT=Path(__file__).resolve().parents[1]
errors=[]

def read(path:str)->str:
    p=ROOT/path
    if not p.is_file():
        errors.append(f"missing:{path}")
        return ""
    return p.read_text(encoding="utf-8")

state=read("PROJECT_STATE.md")
required_state_tokens=(
    "DOCUMENTATION_GOVERNANCE:","PROMOTION_STATE:","DESIGN_BRANCH:","REVIEW_BRANCH:","AUDIT_BRANCH:",
    "FINAL_REVIEW_ID:","FINAL_REVIEW_RECORD:","FINAL_AUDIT_ID:","FINAL_AUDIT_RECORD:",
    "PROMOTION_RULE:","SOURCE_VISIBILITY:","REMOTE_SOURCE_ADDRESSABILITY:","FULL_SOURCE_GIT_MIRROR:",
    "LEARNING_ACTIVATION:","LEARNED_BUT_NOT_ACTIVE_BACKLOG:","UNRESOLVED_INEFFECTIVE_LEARNING:",
    "PENDING_EFFECTIVENESS_MEASUREMENT:","OVERDUE_EFFECTIVENESS_MEASUREMENT:",
)
for token in required_state_tokens:
    if token not in state: errors.append(f"project-state-missing:{token}")

standing={name:read(name) for name in ("GIT_WORKFLOW.md","EXECUTION_LANES.md","WORKSPACE_WSL.md")}
for name,text in standing.items():
    for literal in ("lane/docs-v2-design","lane/docs-v2-review","lane/docs-v2-audit","/docs-v2-design","/docs-v2-review","/docs-v2-audit"):
        if literal in text: errors.append(f"stale-governance-identity:{name}:{literal}")

learning=read("SELF_LEARNING.md")
for token in ("LEARNING_STATE.json","ACTIVE_BUT_NOT_EFFECTIVE","LIFECYCLE_STATE_DRIFT","SEMANTIC_EVIDENCE_MISMATCH","Guarded automation","measurement_gate","Semantic effectiveness proof"):
    if token not in learning: errors.append(f"learning-governance-missing:{token}")

if not (ROOT/"learning/LEARNING_STATE.json").is_file(): errors.append("learning-state-register-missing")
if not (ROOT/"tools/check_learning_lifecycle.py").is_file(): errors.append("learning-lifecycle-checker-missing")

# Canonical TEST_REVIEW provenance must resolve its proposal/gap from the canonical tree.
for review_path in sorted((ROOT/"test-governance").glob("TEST_REVIEW-*.md")):
    text=review_path.read_text(encoding="utf-8")
    m=re.search(r"^TEST_CHANGE_ID:\s*(\S+)\s*$",text,re.M)
    if m and not (ROOT/"test-governance"/(m.group(1)+".md")).is_file():
        errors.append(f"test-review-orphan:{review_path.name}:{m.group(1)}")
    g=re.search(r"^TEST_GAP_ID:\s*(\S+)\s*$",text,re.M)
    if g and not (ROOT/"test-governance"/(g.group(1)+".md")).is_file():
        errors.append(f"test-review-gap-orphan:{review_path.name}:{g.group(1)}")

# Root package metadata is not implicit current project truth.
docmap=read("DOCUMENTATION_MAP.md")
if "pyproject.toml" not in docmap or "not current candidate/version/review authority" not in docmap.lower():
    errors.append("root-metadata-authority-not-explicit")

# The dedicated lifecycle checker is part of governance, not an optional informational tool.
if not errors:
    proc=subprocess.run([sys.executable,str(ROOT/"tools/check_learning_lifecycle.py")],cwd=ROOT,text=True,capture_output=True)
    if proc.returncode!=0:
        details=";".join(line.strip() for line in proc.stdout.splitlines() if line.strip())
        errors.append("learning-lifecycle:"+details)

if errors:
    for error in errors: print(f"FAIL {error}")
    raise SystemExit(1)
print("PASS documentation governance release-selection/promotion/learning-lifecycle/source-visibility/test-provenance invariants")
