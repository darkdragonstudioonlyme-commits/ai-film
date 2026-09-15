# AI-FILM-SERVER — CANONICAL PROJECT STATE V21

> Read first in every new chat. This is current global truth. Routing: `WORKFLOW_ROUTER.md`. Documentation ownership: `DOCUMENTATION_MAP.md`.

## Fast resume snapshot

```yaml
PROJECT: AI-FILM-SERVER
STATE_VERSION: 21
CURRENT_MODE: IMPLEMENTATION
CURRENT_PHASE: "00 — Host / WSL"
CURRENT_TASK: IMPL-P00-001
TARGET_GATE: CODE_REVIEW_PASS
PHASE_GATE: HOST_READY
EXECUTION_MODEL: INDEPENDENT_LANES_WITH_IMMUTABLE_HANDOFFS

REVIEWED_DESIGN: "Phase00 exact Design V2 — REVIEW-P00-002 PASS"
APPROVED_CONTRACT_SET_DIGEST: f259656c48ed24c15bd48da2bb040950ed94d8edcf1473cf6456b96578c933ee
FROZEN_DECISIONS: "FD-01…FD-08 unchanged"
APPROVED_PHASE00_DESIGN: "D00-01…D00-14 exact V2"

LAST_DURABLE_IMPLEMENT_CANDIDATE:
  VERSION: 0.1.0.dev17
  SOURCE_COMMIT: 64ea95bf10e05e856a009be9204983182f520b45
  PACKAGE_SHA256: 130f43c1b54ce00c19a894c61dfa0edfc4218a434ba4d1f060ef815cfaff951e
  AUTHOR_TESTS: "753 PASS / 0 failure / 0 error / 0 skip"
  STATIC_CHECKS: "100 PASS / 0 failed"

IMPLEMENT_WIP:
  STATUS: WIP_NOT_DURABLE_NOT_REVIEWABLE
  WORKTREE: /home/dragon/ai-film-dev/implement
  BRANCH: impl/p00
  BASE_COMMIT: 64ea95bf10e05e856a009be9204983182f520b45
  PLANNED_VERSION: 0.1.0.dev18
  DIRTY_FILES:
    - config/required-native-test-inventory.json
    - src/aifilm_p00/native/harness_cases.py
    - src/aifilm_p00/native/harness_controller.py
    - tests/test_dev15_harness.py
  LATEST_AUTHOR_TESTS: "756 PASS / 0 failure / 0 error / 0 skip"
  LATEST_STATIC_CHECKS: "100 PASS / 0 failed"
  LATEST_SOURCE_DIGEST: 44633115f00e1611a4851ece8cef5f27b455f0031f1b26970c9486bf8940cbb1
  LATEST_TEST_DIGEST: 8f65ebed7ccc5eee4a91e4df9f8c0c851a79f8719e230e75b98f104bd61ea5f7
  NOTE: "CR-P00-012/013 implementation fixes authored; must be finalized/committed/packaged before REVIEW."

LAST_REVIEW:
  TARGET_VERSION: 0.1.0.dev17
  TARGET_COMMIT: 64ea95bf10e05e856a009be9204983182f520b45
  DELTA_VERDICT: FAIL
  INDEPENDENT_TESTS: "753 PASS"
  INDEPENDENT_STATIC: "100 PASS"
  CLOSED_FINDINGS: [CR-P00-002, CR-P00-003, CR-P00-004, CR-P00-005, CR-P00-007, CR-P00-008, CR-P00-009, CR-P00-010, CR-P00-011]
  OPEN_FINDINGS: [CR-P00-001, CR-P00-012, CR-P00-013]

AUTHOR_COMPLETE: false
CODE_REVIEW_HANDOFF_READY: false
CODE_REVIEW_PASS: false
NATIVE_WINDOWS_WSL: NOT_RUN
LAB: NOT_RUN
SITE: NOT_RUN
HOST_READY: NOT_EVALUATED

ACTIVE_WORKFLOW:
  WORKFLOW_ID: WF-P00-IMPL-DEV18
  LANE: IMPLEMENT
  STATUS: WIP
  ON_SUCCESS: WF-P00-REVIEW-DEV18
  ON_FAIL: WF-P00-IMPL-DEV18
  ON_BLOCK: WORKFLOW_ROUTER_BLOCK_PROTOCOL

NEXT_ACTION: "Resume existing dev18 WIP; finalize version/docs/evidence, full regression, secret/diff audit, commit/package immutable candidate, then hand exact candidate to REVIEW."
```

## Important distinction

`dev17` is the last durable committed/reviewed candidate. `dev18` is real implementation progress but remains **uncommitted WIP**; a fresh chat must resume it, not discard it and not formally review it yet.

## Global blockers

- `CR-P00-001 OPEN_BLOCKER` — full Phase00 author completeness not yet established.
- `CR-P00-012/013` are open review findings on dev17; dev18 WIP contains intended fixes pending immutable handoff/review.

## State verification rule

Before work, fetch remote `main` and relevant lane refs. If local worktree state conflicts with this file, stop and classify whether the difference is a documented WIP, a newer durable handoff, or state drift. Never silently overwrite WIP.
