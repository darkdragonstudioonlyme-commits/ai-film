# LEARNING-DOC-STATE-MACHINE-001

```yaml
LEARNING_ID: LEARNING-DOC-STATE-MACHINE-001
CLASS: TOOLING
OBSERVATION: "V2 R6 checkers became invalid when project moved from WIP to reviewed-clean residual audit."
ROOT_CAUSE: "Verifier encoded one snapshot schema instead of lifecycle-neutral state invariants."
REUSABLE_RULE: "Machine reconciliation consumes a stable state-machine contract; transient state markers are data, not checker schema."
SCORE: 9
POLICY_OR_TOOL_PROMOTION: "DOCSYS-V2-R7 check_project_docs/check_runtime_state/audit + CHECKER_DRIFT recovery"
SUCCESS_METRIC: "Future WIP→handoff→reviewed-fail→reviewed-clean transitions pass reconciliation without checker code edits when runtime_reconciliation schema is unchanged."
REVIEW_STATUS: PENDING_R7_DOC_REVIEW
STATUS: ACTIVE
```
