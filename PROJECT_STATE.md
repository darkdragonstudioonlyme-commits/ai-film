# AI-FILM-SERVER — CANONICAL PROJECT STATE V22-CANDIDATE

> Global current truth. Read with `NEXT_WORK_ITEM.md` and `WORKFLOW_ROUTER.md`; verify fresh lane/runtime state before routing.

```yaml
PROJECT: AI-FILM-SERVER
CURRENT_MODE: IMPLEMENTATION
CURRENT_PHASE: "00 — Host / WSL"
CURRENT_TASK: IMPL-P00-001
TARGET_GATE: CODE_REVIEW_PASS
PHASE_GATE: HOST_READY

DOCUMENTATION_GOVERNANCE:
  ACTIVE_SYSTEM: V1_REVIEWED
  CANDIDATE_SYSTEM: V2
  V2_STATUS: DESIGN_HANDOFF_PENDING_REVIEW_AND_FINAL_AUDIT
  REQUIRED_FLOW: DOC-DESIGN-V2 -> DOC-REVIEW-V2 -> DOC-AUDIT-V2
  RETURN_TO_AFTER_PASS: WF-P00-IMPL-DEV18

LAST_DURABLE_IMPLEMENT_CANDIDATE:
  VERSION: 0.1.0.dev17
  COMMIT: 64ea95bf10e05e856a009be9204983182f520b45
  PACKAGE: /home/dragon/ai-film-dev/artifacts/IMPL-P00-001_IMPLEMENTATION_PACKAGE_V17.zip
  PACKAGE_SHA256: 130f43c1b54ce00c19a894c61dfa0edfc4218a434ba4d1f060ef815cfaff951e
  AUTHOR_TESTS: "753 PASS"
  STATIC_CHECKS: "100 PASS"

IMPLEMENT_WIP:
  PLANNED_VERSION: 0.1.0.dev18
  STATUS: WIP_NOT_DURABLE_NOT_REVIEWABLE
  BASE_COMMIT: 64ea95bf10e05e856a009be9204983182f520b45
  WORKTREE: /home/dragon/ai-film-dev/implement
  DIRTY_FILES:
    - config/required-native-test-inventory.json
    - src/aifilm_p00/native/harness_cases.py
    - src/aifilm_p00/native/harness_controller.py
    - tests/test_dev15_harness.py
  LAST_AUTHOR_RUN: "756 PASS / 100 static PASS"
  PURPOSE: "remediate CR-P00-012/013 collector scope and stage-window continuity"

LAST_REVIEW:
  TARGET_VERSION: 0.1.0.dev17
  TARGET_COMMIT: 64ea95bf10e05e856a009be9204983182f520b45
  OVERALL_VERDICT: FAIL
  CLOSED_FINDINGS: [CR-P00-007, CR-P00-008, CR-P00-009, CR-P00-010, CR-P00-011]
  OPEN_FINDINGS: [CR-P00-001, CR-P00-012, CR-P00-013]

ENVIRONMENT:
  DOC: SERVER_ENVIRONMENT.md
  SNAPSHOT: evidence/SERVER_ENVIRONMENT_SNAPSHOT.json
  FINGERPRINT: fde8230f226af7bdd2492144131d3e6f54aa2ac139927ae2751e77553437e7f8
  MODEL_EVALUATION_READY: false

AUTHOR_COMPLETE: false
CODE_REVIEW_HANDOFF_READY: false
CODE_REVIEW_PASS: false
NATIVE_WINDOWS_WSL: NOT_RUN
LAB: NOT_RUN
SITE: NOT_RUN
HOST_READY: NOT_EVALUATED
```

## Current control-plane priority

Documentation System V2 must complete independent review and final holistic audit before source implementation resumes. Source WIP is preserved and must not be reset or formally reviewed while mutable.

## State invariants

- durable candidate, mutable WIP and review target are different identities;
- fresh remote lane state must reconcile with this file and prepared worktrees;
- policy docs do not override approved design contracts;
- author/review tests are not native validation;
- model-evaluation results require a qualified environment fingerprint.
