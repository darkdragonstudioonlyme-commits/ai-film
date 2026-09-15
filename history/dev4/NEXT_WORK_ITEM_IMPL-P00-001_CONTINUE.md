# NEXT_WORK_ITEM — continue IMPL-P00-001 from dev4

```yaml
WORK_ITEM_ID: IMPL-P00-001
MODE: IMPLEMENTATION
PHASE: "00 — Host / WSL"
STATUS: IN_PROGRESS
CURRENT_DELIVERY: PARTIAL_SOURCE_DROP_DEV4
ENTRY_GATE: DESIGN_REVIEW_PASS
ENTRY_GATE_STATUS: SATISFIED_EXACT_V2
TARGET_GATE: CODE_REVIEW_PASS
MODE_TRANSITION_NOW: NONE
INPUTS:
  - AI_FILM_PROJECT_STATE_V9.json
  - Exact_approved_V2_contracts
  - IMPL-P00-001_IMPLEMENTATION_PACKAGE_V4
  - docs/REMAINING_IMPLEMENTATION.md
  - docs/NATIVE_INTEGRATION_BOUNDARY.md
  - evidence/WORKSPACE_TEST_REPORT.json
FIRST_INTEGRATION:
  - "Finish C0 observation-to-binding and original-request recovery for detached C0 reads before a mutation fence exists."
  - "Complete native service/OOBE/restart/resume/factory paths and journal capacity handling."
THEN:
  - "Close cross-stage E00/proof/failure/publication recovery and primary CLI."
  - "Write full supported-route/failure controller harness and factory integration tests."
FORBIDDEN:
  - "Change FD/D00/public contract or lower acceptance."
  - "Execute native Windows/WSL/LAB/SITE/guest/network during authoring."
  - "Register fixture/fake CLI backends or treat intent/process exit as proof."
  - "Delete unresolved journal state or self-approve review/qualification/HOST_READY."
DESIGN_GAP_RULE: "Record a genuine required behavior change; leave affected implementation before redesign."
EXIT_CONDITION: "Full author-complete source/harness/docs/test candidate; no hidden stubs."
NEXT_MODE_AFTER_EXIT: CODE_REVIEW
NEXT_REVIEW_WORK_ITEM: CODE-REVIEW-P00-001
```

REM-01…08 and BLOCK-01…03 remain full-scope OPEN, owned by this task. Original-fence recovery and live-NOOP components were authored in dev4; do not re-list them as wholly absent, or claim the full lifecycle is finished. No user-supplied host data or permission substitutes for remaining code. Native execution belongs to later gates.
