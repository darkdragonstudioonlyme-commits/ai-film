# AI-FILM-SERVER — CANONICAL PROJECT STATE V18

> Read first in every new chat. Global truth only. Lane protocol: `EXECUTION_LANES.md`.

## Fast resume snapshot

```yaml
PROJECT: AI-FILM-SERVER
STATE_VERSION: 18
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
  STATUS: ACTIVE
  SOURCE_WRITABLE: true
REVIEW_LANE:
  REMOTE_BRANCH: lane/review-p00
  WSL_WORKTREE: /home/dragon/ai-film-dev/review
  SOURCE_MODE: DETACHED_EXACT_CANDIDATE
  STATUS: WAITING_FOR_NEXT_CANDIDATE
  SOURCE_WRITABLE: false

REVIEWED_DESIGN: "Phase00 exact Design V2 — REVIEW-P00-002 PASS"
FROZEN_DECISIONS: "FD-01…FD-08 unchanged"
APPROVED_PHASE00_DESIGN: "D00-01…D00-14 exact V2"
APPROVED_CONTRACT_SET_DIGEST: f259656c48ed24c15bd48da2bb040950ed94d8edcf1473cf6456b96578c933ee

CURRENT_VERIFIED_DELIVERY: "0.1.0.dev8 / PARTIAL_SOURCE_DROP_DEV8"
DEV8_SOURCE_COMMIT: c44c2f87084f8082ce29af5935c6b47d03f7b96c
DEV8_PACKAGE_SHA256: d4e6b67eebd40fbc173f85205792499021cf6eea9b82309e54c2a76a9a9e3cb5
DEV8_DRIVE_FILE_ID: 125T2wVf0CVkcmQND0PSmF3HHvXh8AgxD
AUTHOR_COMPLETE: false
CODE_REVIEW_HANDOFF_READY: false

WORKSPACE_AUTHOR_TESTS: "683 PASS / 0 failure / 0 error / 0 skip"
STATIC_AUTHOR_CHECKS: "92 PASS / 0 failed"
NATIVE_WINDOWS_WSL: NOT_RUN
LAB: NOT_RUN
SITE: NOT_RUN
QUALIFICATION_ISSUED: false
HOST_READY: NOT_EVALUATED

LAST_CODE_REVIEW:
  WORK_ITEM: CODE-REVIEW-P00-001
  TARGET: dev8
  VERDICT: FAIL
  REVIEW_RECORD: reviews/CODE-REVIEW-P00-001_DEV8.md

OPEN_CODE_REVIEW_FINDINGS:
  - CR-P00-001 BLOCKER — full implementation handoff incomplete
  - CR-P00-002 HIGH — owner-wait durable relabel lacks renewed authority check
  - CR-P00-003 HIGH — actual pending-reboot cause discarded at persistence boundary
  - CR-P00-004 MEDIUM — wait_observation API untyped/unbounded

OPEN_IMPLEMENTATION_ITEMS: "IMPL-REM-01…08"
IMPLEMENTATION_BLOCKERS: "IMPL-BLOCK-01…03"
OPEN_DESIGN_GAPS: []
OPEN_VALIDATION_FAILURES: []

NEXT_ACTION: "IMPLEMENT lane fixes CR-P00-002/003/004, persists a new exact candidate, then continues remaining source scope. REVIEW lane stays frozen on dev8 until immutable handoff."
```

## Dual-lane operating model

`main` remains the only canonical project mode/gate ledger. Lane branches/worktrees isolate responsibilities but cannot independently promote gates.

### IMPLEMENT

- remote state branch: `lane/implement-p00`;
- writable WSL source: `/home/dragon/ai-film-dev/implement`;
- local source branch: `impl/p00`;
- starts from exact dev8 commit `c44c2f87...`;
- may change source/tests/docs and create candidates;
- may not issue review verdicts or CODE_REVIEW_PASS.

### REVIEW

- remote state branch: `lane/review-p00`;
- WSL worktree: `/home/dragon/ai-film-dev/review`;
- detached exact candidate source;
- current frozen candidate: dev8 / `c44c2f87...`;
- last verdict: FAIL;
- may write findings/verdicts only; must not patch source;
- status: waiting for next immutable candidate.

Full permissions/handoff protocol: `EXECUTION_LANES.md`.

## Immutable candidate rule

A formal implementation→review handoff binds exact source commit, package name/size/SHA-256/artifact ID, source/test digests, author-test/static results, contract digest, changed scope, known findings and handoff readiness flags.

REVIEW never follows IMPLEMENT head automatically. A new candidate requires an explicit handoff and REVIEW worktree reset/recreation at the exact candidate commit.

Formal `CODE_REVIEW_PASS` remains impossible while `AUTHOR_COMPLETE=false` or `CODE_REVIEW_HANDOFF_READY=false`.

## Current IMPLEMENT queue

1. Fix `CR-P00-002` with renewed authority immediately before persistent relabel and negative drift/expiry tests.
2. Fix `CR-P00-003` by persisting safe typed wait-cause identity.
3. Fix `CR-P00-004` with exact schemas + canonical size/privacy limits.
4. Run targeted/full author tests in IMPLEMENT lane.
5. Commit/persist exact next candidate.
6. Continue prior pre-C3/checkpoint + nested E00, publication/E17 recovery, non-DIRECT transport, full causal 86-case controller and production-factory integration work.
7. `CR-P00-001` closes only when full author-complete scope exists.

## Current REVIEW disposition

Exact dev8 review is complete and frozen for audit. Review lane waits for the next candidate. It does not inspect mutable IMPLEMENT changes as formal input.

## WSL commands

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

Both lanes independently reproduced the dev8 baseline: 683 tests PASS and 92 static checks PASS. This remains author/review workspace evidence only.

## Prohibitions

- no cross-lane permission mixing in one increment;
- REVIEW does not patch source;
- IMPLEMENT does not self-review/approve;
- no formal review of uncommitted IMPLEMENT work;
- no FD/D00/public-contract change in IMPLEMENT;
- no native Windows/WSL/LAB/SITE proof inferred from author/review tests;
- no deletion of unresolved durable state;
- no plaintext credentials;
- no useful reusable knowledge left only in chat.

## Exit condition

IMPLEMENT must produce a full author-complete exact candidate with `CODE_REVIEW_HANDOFF_READY=true`. REVIEW then independently reviews that exact identity. Only REVIEW PASS on that immutable candidate can satisfy `CODE_REVIEW_PASS`.
