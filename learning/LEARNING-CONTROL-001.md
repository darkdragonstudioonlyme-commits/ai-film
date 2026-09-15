# LEARNING-CONTROL-001 — Checker schema overfitting

```yaml
LEARNING_ID: LEARNING-CONTROL-001
DISCOVERED_IN: WF-P00-IMPL-CR001-RESIDUAL-AUDIT bootstrap
CLASS: TOOLING
OBSERVATION: "Documentation/runtime checkers failed after canonical state evolved from V22 to V26 even though V26 state, lane heads, reviewed candidate and workflow were mutually consistent."
ROOT_CAUSE: "Checkers encoded V22 Markdown field names/promotion markers as permanent invariants instead of validating semantic roles from the latest machine-readable state."
EVIDENCE: "check_project_docs.py required WIP/promotion fields; check_runtime_state.py required BASE_COMMIT/TARGET_COMMIT/PLANNED_VERSION/PACKAGE_PATH; audit checker required V22 promotion markers."
REUSABLE_RULE: "Control-plane checkers validate semantic invariants and latest state identity; checkpoint-specific field names are compatibility inputs, not permanent policy."
SCORE: 8
CURRENT_ACTION: "Use latest AI_FILM_PROJECT_STATE_Vn.json as primary runtime state, optional Markdown enrichment for WIP/package details, and semantic DOCSYS-V2 activation checks."
POLICY_OR_TOOL_PROMOTION: "tools/check_project_docs.py, tools/check_runtime_state.py, tools/audit_documentation_v2.py"
SUCCESS_METRIC: "Future state schema evolution does not require checker edits unless a semantic invariant changes; true lane/worktree/artifact drift still fails closed."
REVIEW_STATUS: PENDING_DOC_REVIEW_AUDIT
STATUS: ACTIVE
```
