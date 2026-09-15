#!/usr/bin/env python3
"""Portable R8 documentation-governance invariants.

This checker intentionally validates standing-policy shape, not one release's
commit SHA. Release-specific identities belong to PROJECT_STATE.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
errors = []


def read(path: str) -> str:
    p = ROOT / path
    if not p.is_file():
        errors.append(f"missing:{path}")
        return ""
    return p.read_text(encoding="utf-8")


state = read("PROJECT_STATE.md")
required_state_tokens = (
    "DOCUMENTATION_GOVERNANCE:",
    "DESIGN_BRANCH:",
    "REVIEW_BRANCH:",
    "AUDIT_BRANCH:",
    "FINAL_REVIEW_ID:",
    "FINAL_REVIEW_RECORD:",
    "FINAL_AUDIT_ID:",
    "FINAL_AUDIT_RECORD:",
    "PROMOTION_RULE:",
    "SOURCE_VISIBILITY:",
    "REMOTE_SOURCE_ADDRESSABILITY:",
    "FULL_SOURCE_GIT_MIRROR:",
)
for token in required_state_tokens:
    if token not in state:
        errors.append(f"project-state-missing:{token}")

standing = {
    name: read(name)
    for name in ("GIT_WORKFLOW.md", "EXECUTION_LANES.md", "WORKSPACE_WSL.md")
}
for name, text in standing.items():
    for literal in (
        "lane/docs-v2-design",
        "lane/docs-v2-review",
        "lane/docs-v2-audit",
        "/docs-v2-design",
        "/docs-v2-review",
        "/docs-v2-audit",
    ):
        if literal in text:
            errors.append(f"stale-governance-identity:{name}:{literal}")

learning = read("SELF_LEARNING.md")
for token in ("ACTIVATION_STATUS", "LEARNED_BUT_NOT_ACTIVE", "ACTIVE_BUT_NOT_EFFECTIVE"):
    if token not in learning:
        errors.append(f"learning-activation-missing:{token}")

if errors:
    for error in errors:
        print(f"FAIL {error}")
    raise SystemExit(1)

print("PASS documentation governance release-selection/promotion/activation invariants")
