# NEXT_WORK_ITEM — continue the same implementation task

```yaml
WORK_ITEM_ID: IMPL-P00-001
MODE: IMPLEMENTATION
PHASE: "00 — Host / WSL"
STATUS: IN_PROGRESS
CURRENT_DELIVERY: PARTIAL_SOURCE_DROP_DEV2
TARGET_GATE: CODE_REVIEW_PASS
ENTRY_GATE: DESIGN_REVIEW_PASS
ENTRY_GATE_STATUS: SATISFIED_EXACT_V2
GOAL: "Finish REM-01…08, connecting concrete native components into full reviewed behavior."
INPUTS:
  - AI_FILM_PROJECT_STATE_V7
  - Exact_approved_V2_contracts
  - IMPL-P00-001_IMPLEMENTATION_PACKAGE_V2
  - docs/REMAINING_IMPLEMENTATION.md
  - docs/NATIVE_INTEGRATION_BOUNDARY.md
  - evidence/WORKSPACE_TEST_REPORT.json
FIRST_INTEGRATION:
  - "Native session driver: observed context/proofs → one admission/fence → refresh per step"
  - "Actuation → actual route/service postcondition → terminal/safe pause/resume"
THEN:
  - "Full E00 field/stage collectors, snapshot source, bundle/E17 and CLI registration"
  - "Complete executable route/failure harness and author integration regression"
FORBIDDEN:
  - "Change FD/D00/public contracts or lower acceptance"
  - "Run native Windows/WSL on host/LAB during authoring"
  - "Use fixture flags or process exit as actual proof/qualification"
  - "Enable active CLI by substituting MemoryGuard/fake observations"
  - "Self-approve CODE_REVIEW_PASS or HOST_READY"
DESIGN_GAP_RULE: "Record evidence and exit affected implementation scope before changing approved behavior."
EXIT_CONDITION: "Full author-complete candidate; all REM closures or properly managed blockers, no hidden stubs."
NEXT_MODE_AFTER_EXIT: CODE_REVIEW
NEXT_REVIEW_WORK_ITEM: CODE-REVIEW-P00-001
MODE_TRANSITION_NOW: NONE
```

The remaining work is code integration, not a request for the user to supply missing data or a claim that Windows tests alone would complete the source. Native execution belongs to later authorized gates.
