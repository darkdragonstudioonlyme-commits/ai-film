# AI-FILM-SERVER — CANONICAL PROJECT STATE V19

> Read first in every new chat. Global truth only. Lane protocol: `EXECUTION_LANES.md`.

## Fast resume snapshot

```yaml
PROJECT: AI-FILM-SERVER
STATE_VERSION: 19
REPOSITORY: darkdragonstudioonlyme-commits/ai-film
DEFAULT_BRANCH: main

CURRENT_MODE: IMPLEMENTATION
CURRENT_PHASE: "00 — Host / WSL"
CURRENT_TASK: IMPL-P00-001
TASK_STATUS: IN_PROGRESS
TARGET_GATE: CODE_REVIEW_PASS
PHASE_GATE: HOST_READY
EXECUTION_MODEL: DUAL_LANE

IMPLEMENT_LANE:
  REMOTE_BRANCH: lane/implement-p00
  WSL_WORKTREE: /home/dragon/ai-film-dev/implement
  LOCAL_SOURCE_BRANCH: impl/p00
  STATUS: ACTIVE_NEXT_INCREMENT
  SOURCE_WRITABLE: true
  CURRENT_SOURCE_COMMIT: 3da3ddc771c15d175a2c5045c86a7c1ff9987dbd
REVIEW_LANE:
  REMOTE_BRANCH: lane/review-p00
  WSL_WORKTREE: /home/dragon/ai-film-dev/review
  SOURCE_MODE: DETACHED_EXACT_CANDIDATE
  STATUS: REVIEW_COMPLETE_WAITING_FOR_NEXT_CANDIDATE
  SOURCE_WRITABLE: false
  LAST_REVIEWED_COMMIT: 3da3ddc771c15d175a2c5045c86a7c1ff9987dbd

REVIEWED_DESIGN: "Phase00 exact Design V2 — REVIEW-P00-002 PASS"
APPROVED_CONTRACT_SET_DIGEST: f259656c48ed24c15bd48da2bb040950ed94d8edcf1473cf6456b96578c933ee
FROZEN_DECISIONS: "FD-01…FD-08 unchanged"
APPROVED_PHASE00_DESIGN: "D00-01…D00-14 exact V2"

CURRENT_VERIFIED_DELIVERY: "0.1.0.dev9 / PARTIAL_SOURCE_DROP_DEV9"
DEV9_SOURCE_COMMIT: 3da3ddc771c15d175a2c5045c86a7c1ff9987dbd
DEV9_PACKAGE: IMPL-P00-001_IMPLEMENTATION_PACKAGE_V9.zip
DEV9_PACKAGE_LOCATION: /home/dragon/ai-film-dev/artifacts/IMPL-P00-001_IMPLEMENTATION_PACKAGE_V9.zip
DEV9_PACKAGE_SIZE_BYTES: 1114609
DEV9_PACKAGE_SHA256: d6f83dc3ff60f73acd54750f58db34d817c7bb492c83088693f7c47c65d510cb
DEV9_MANIFEST_SHA256: c151189747e56da6b334afaa4c9fd81a9843e2fb8a356834d4c88f542608254d
SOURCE_CONTENT_DIGEST: 09104ef51e06d9d3be984271c1f2eaf3b7d7a2fa3c1f5435cab6d20e45248b93
TEST_CONTENT_DIGEST: 59e56a692018fce4d5514d0083d861423d1e2b6fa131d3a7756804afe1b7f697
AUTHOR_TESTS: "692 PASS / 0 failure / 0 error / 0 skip"
STATIC_CHECKS: "93 PASS / 0 failed"
NATIVE_WINDOWS_WSL: NOT_RUN
LAB: NOT_RUN
SITE: NOT_RUN
QUALIFICATION_ISSUED: false
HOST_READY: NOT_EVALUATED
AUTHOR_COMPLETE: false
CODE_REVIEW_HANDOFF_READY: false

LAST_REVIEW:
  TARGET: dev9
  KIND: DELTA_REVIEW_CR_P00_002_003_004
  DELTA_VERDICT: PASS
  OVERALL_CODE_REVIEW_VERDICT: FAIL
  SOURCE_MODIFIED_DURING_REVIEW: false
  RECORD: reviews/CODE-REVIEW-P00-001_DEV9_DELTA.md

FINDING_STATUS:
  CR-P00-001: OPEN_BLOCKER
  CR-P00-002: CLOSED_BY_DEV9_REVIEW
  CR-P00-003: CLOSED_BY_DEV9_REVIEW
  CR-P00-004: CLOSED_BY_DEV9_REVIEW

OPEN_IMPLEMENTATION_ITEMS: "IMPL-REM-01…08"
IMPLEMENTATION_BLOCKERS: "IMPL-BLOCK-01…03"
OPEN_DESIGN_GAPS: []
OPEN_VALIDATION_FAILURES: []

NEXT_ACTION: "IMPLEMENT lane: prior pre-C3/checkpoint provenance selection + nested cross-stage E00 semantics; REVIEW lane waits for the next immutable candidate."
```

## Dev9 dual-lane cycle result

IMPLEMENT produced exact dev9 candidate commit `3da3ddc...` to remediate CR-P00-002/003/004. REVIEW detached at that exact commit, independently reran 692 workspace tests and 93 static checks, reproduced the former failure scenarios, and independently verified the local V9 package SHA/manifest.

Review dispositions:

- CR-P00-002 — CLOSED: durable owner-verification relabel now renews authority after observation and immediately before persistence; expiry/generation/actor/request drift block the write.
- CR-P00-003 — CLOSED: actual pending-reboot cause is persisted as typed safe wait metadata instead of only a derived state.
- CR-P00-004 — CLOSED: durable wait metadata has an exact schema, previous-state binding, fixed normalized reboot keys, digest checks and a canonical 1024-byte cap; raw/unknown/oversized shapes are rejected.

No approved contract changed. Source was not modified in REVIEW lane.

## Why the full gate still fails

CR-P00-001 remains an umbrella blocker. Dev9 is still a partial implementation and `AUTHOR_COMPLETE=false`. Prior pre-C3/checkpoint/nested E00 semantics, remaining publication/E17 recovery, non-DIRECT transport, complete causal 86-case controller/oracles, and production-factory author integration remain open.

Therefore `CODE_REVIEW_PASS=false` remains correct even though the dev9 remediation delta passed review.

## Exact next implementation order

1. Prior pre-C3/checkpoint provenance selection.
2. Nested cross-stage E00 field/source semantics.
3. Focused positive/negative author tests for unrelated/tampered/ambiguous/stale/wrong-host/wrong-plan provenance.
4. Full IMPLEMENT regression/static checks and immutable candidate handoff.
5. REVIEW lane independently reviews that exact candidate.
6. Then remaining publication/E17, non-DIRECT transport, causal 86-case harness and production-factory integration increments.

## Lane commands

IMPLEMENT:

```bash
source /home/dragon/ai-film-dev/implement-env.sh
/home/dragon/ai-film-dev/lane-test.sh implement
```

REVIEW:

```bash
source /home/dragon/ai-film-dev/review-env.sh
/home/dragon/ai-film-dev/lane-test.sh review
```

## Prohibitions

- REVIEW never patches candidate source.
- IMPLEMENT never self-approves CODE_REVIEW.
- No formal review of uncommitted IMPLEMENT state.
- No FD/D00/public-contract changes in IMPLEMENT.
- No native Windows/WSL/LAB/SITE proof inferred from author/review tests.
- No deletion of unresolved durable state or raw sensitive wait payload persistence.
- No useful reusable knowledge left only in chat.

## Exit condition

Only a full author-complete immutable candidate with `CODE_REVIEW_HANDOFF_READY=true`, followed by independent REVIEW PASS on that exact identity, can satisfy `CODE_REVIEW_PASS`.
