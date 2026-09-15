# AI-FILM-SERVER — CANONICAL PROJECT STATE V27

> Read first in every new chat. Human current truth. Machine reconciliation snapshot: `AI_FILM_PROJECT_STATE_V27.json`.

```yaml
PROJECT: AI-FILM-SERVER
STATE_VERSION: 27
CURRENT_MODE: IMPLEMENTATION
CURRENT_PHASE: "00 — Host / WSL"
CURRENT_TASK: IMPL-P00-001
TARGET_GATE: CODE_REVIEW_PASS
PHASE_GATE: HOST_READY
DOCUMENTATION_SYSTEM: DOCSYS-V2-R7

DOCUMENTATION_GOVERNANCE:
  ACTIVE_SYSTEM_VERSION: V2
  SYSTEM_RELEASE_ID: DOCSYS-V2-R7
  PREVIOUS_RELEASE: DOCSYS-V2-R6
  ACTIVATION_CONDITION: "Promote exact R7 tree only after DOC-V2-R7-REVIEW-001 PASS and DOC-V2-R7-AUDIT-001 PASS"
  DETAILED_REVIEW_ID: DOC-V2-R7-REVIEW-001
  DETAILED_REVIEW_RECORD: reviews/DOCUMENTATION_SYSTEM_V2_R7_REVIEW_001_PASS.md
  HOLISTIC_AUDIT_ID: DOC-V2-R7-AUDIT-001
  HOLISTIC_AUDIT_RECORD: reviews/DOCUMENTATION_SYSTEM_V2_R7_AUDIT_001_PASS.md

LAST_REVIEWED_CANDIDATE:
  VERSION: 0.1.0.dev19
  SOURCE_COMMIT: 2ac37acdd3f81d3b86d4ffb019689655110a80c2
  PACKAGE_PATH: /home/dragon/ai-film-dev/artifacts/IMPL-P00-001_IMPLEMENTATION_PACKAGE_V19.zip
  PACKAGE_SHA256: 564ad67c2ddc00f1f4ffbc891afa1aeb1c0c194b0d2fb6c30767f6ae381491e1
  DELTA_VERDICT: PASS
  OVERALL_CODE_REVIEW_VERDICT: FAIL_CR_P00_001_ONLY

FINDING_STATUS:
  CR-P00-001: OPEN_BLOCKER
  CR-P00-012: CLOSED_DEV19
  CR-P00-013: CLOSED_DEV18_REVERIFIED_DEV19
  CR-P00-014: CLOSED_DEV19

AUTHOR_BASE_FOR_RESIDUAL_AUDIT:
  VERSION: 0.1.0.dev19
  COMMIT: 2ac37acdd3f81d3b86d4ffb019689655110a80c2
  AUTHOR_TESTS: "759 PASS"
  STATIC_CHECKS: "100 PASS"

RUNTIME_RECONCILIATION:
  STATE_KIND: REVIEWED_CLEAN_RESIDUAL_AUDIT
  SNAPSHOT_JSON: AI_FILM_PROJECT_STATE_V27.json
  IMPLEMENT_HEAD: 2ac37acdd3f81d3b86d4ffb019689655110a80c2
  REVIEW_HEAD: 2ac37acdd3f81d3b86d4ffb019689655110a80c2
  IMPLEMENT_DIRTY_FILES: []
  PACKAGE_REQUIRED: true
  PACKAGE_PATH: /home/dragon/ai-film-dev/artifacts/IMPL-P00-001_IMPLEMENTATION_PACKAGE_V19.zip
  PACKAGE_SHA256: 564ad67c2ddc00f1f4ffbc891afa1aeb1c0c194b0d2fb6c30767f6ae381491e1

AUTHOR_COMPLETE: false
CODE_REVIEW_HANDOFF_READY: false
CODE_REVIEW_PASS: false
NATIVE_WINDOWS_WSL: NOT_RUN
LAB: NOT_RUN
SITE: NOT_RUN
HOST_READY: NOT_EVALUATED

ACTIVE_WORKFLOW:
  WORKFLOW_ID: WF-P00-IMPL-CR001-RESIDUAL-AUDIT
  LANE: IMPLEMENT
  STATUS: READY
  INPUT_COMMIT: 2ac37acdd3f81d3b86d4ffb019689655110a80c2
  ON_SUCCESS: WF-P00-FINAL-AUTHOR-CANDIDATE
  ON_FAIL: WF-P00-IMPL-RESIDUAL-FIX

NEXT_ACTION: "Resume residual CR-P00-001 author-completeness audit after R7 governance promotion; do not infer completeness from test count."
```

## Runtime reconciliation contract

`RUNTIME_RECONCILIATION` is a stable lifecycle-neutral mirror for humans. `tools/check_runtime_state.py` reads the structured `runtime_reconciliation` object from the version-matched JSON snapshot, not transient prose fields such as WIP or review candidate names.

Allowed state kinds include `WIP`, `HANDED_OFF`, `REVIEWED_FAIL`, `REVIEWED_CLEAN_RESIDUAL_AUDIT`, `FINAL_AUTHOR_CANDIDATE`, and later reviewed lifecycle states. A state kind may have an empty dirty set. Checker success never implies code/native gate PASS.

## Checker failure classification

- actual canonical/lane/worktree/artifact mismatch → `STATE_DRIFT`;
- missing/unsupported snapshot schema or checker assumption that no longer models a valid lifecycle state → `CHECKER_DRIFT` and Documentation System review.

Do not repair `CHECKER_DRIFT` by mutating valid source state to satisfy an obsolete checker.
