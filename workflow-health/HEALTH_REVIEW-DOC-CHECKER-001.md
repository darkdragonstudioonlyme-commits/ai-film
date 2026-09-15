# HEALTH_REVIEW-DOC-CHECKER-001

```yaml
HEALTH_REVIEW_ID: HEALTH_REVIEW-DOC-CHECKER-001
TRIGGER: "Canonical V26 entered reviewed-clean residual-audit state; V2 R6 checkers falsely required V22 WIP/promotion markers"
WORKFLOW: WF-P00-IMPL-CR001-RESIDUAL-AUDIT
HEALTH_STATE: DEGRADED
ROOT_CAUSE_CLASS: TOOL_AND_STATE_SCHEMA
SYSTEMIC_CHANGE: DOCSYS-V2-R7 lifecycle-aware reconciliation
RETURN_TO: WF-P00-IMPL-CR001-RESIDUAL-AUDIT
RESULT: CORRECTION_PENDING_REVIEW
```

## Evidence

`check_project_docs.py` required `WIP_NOT_DURABLE_NOT_REVIEWABLE`, V2 promotion review IDs from R6, and V22 snapshot files. `check_runtime_state.py` required `BASE_COMMIT`, `TARGET_COMMIT`, `PLANNED_VERSION`, and `PACKAGE_PATH` Markdown fields. V26 legitimately represented a reviewed-clean residual audit state and therefore produced false failures.

## Root cause

The checkers were authored against one transient V22 state shape instead of the project state machine. The verifier became stale even though source/lane identities were valid.

## Correction

R7 introduces a stable machine-readable `runtime_reconciliation` object in the version-matched JSON state snapshot, dynamic current snapshot selection, allowed lifecycle state kinds, and explicit `CHECKER_DRIFT` recovery. Checkers are forbidden from pinning one delivery/checkpoint/review ID/WIP marker.
