# NEXT_WORK_ITEM — continue IMPL-P00-001 from dev3

```yaml
WORK_ITEM_ID: IMPL-P00-001
MODE: IMPLEMENTATION
PHASE: "00 — Host / WSL"
STATUS: IN_PROGRESS
CURRENT_DELIVERY: PARTIAL_SOURCE_DROP_DEV3
ENTRY_GATE: DESIGN_REVIEW_PASS
ENTRY_GATE_STATUS: SATISFIED_EXACT_V2
TARGET_GATE: CODE_REVIEW_PASS
MODE_TRANSITION_NOW: NONE
GOAL: "Finish remaining source/integration/harness; do not reinterpret missing code as missing native evidence."
FIRST_INTEGRATION:
  - "Complete original-fence safe diagnostics/cancellation/pause/reconciliation."
  - "Complete committed-run live NOOP verification and C0 observation-to-binding."
THEN:
  - "Close cross-stage proof/E00 semantics, failure/publication recovery and primary CLI wiring."
  - "Write full supported-route/failure controller harness and production-driver integration tests."
INPUTS:
  - AI_FILM_PROJECT_STATE_V8
  - Exact_approved_V2_contracts
  - IMPL-P00-001_IMPLEMENTATION_PACKAGE_V3
  - docs/REMAINING_IMPLEMENTATION.md
  - docs/NATIVE_INTEGRATION_BOUNDARY.md
  - evidence/WORKSPACE_TEST_REPORT.json
FORBIDDEN:
  - "Change FD/D00/public contract or lower acceptance."
  - "Execute native Windows/WSL/LAB/SITE in authoring."
  - "Use fixture flags, process exit, inventory or test count as actual proof."
  - "Register fake ports as the active CLI backend."
  - "Self-approve code review, qualification or HOST_READY."
DESIGN_GAP_RULE: "Record a genuine required behavior change and leave affected implementation before redesign."
EXIT_CONDITION: "Full author-complete code/harness/docs/test candidate, no hidden stubs."
NEXT_MODE_AFTER_EXIT: CODE_REVIEW
NEXT_REVIEW_WORK_ITEM: CODE-REVIEW-P00-001
```

IMPL-BLOCK-01…03 are source blockers owned by this task. No user-supplied host information or permission is requested as a substitute for writing the remaining code. Native execution belongs only to later authorized gates.
