# AI-FILM-SERVER — CANONICAL PROJECT STATE V17

> Read this file first in every new chat. Current operational truth only. Reusable lessons live in `PROJECT_MEMORY.md`; exact next work lives in `NEXT_WORK_ITEM.md`.

## Fast resume snapshot

```yaml
PROJECT: AI-FILM-SERVER
STATE_VERSION: 17
REPOSITORY: darkdragonstudioonlyme-commits/ai-film
DEFAULT_BRANCH: main

CURRENT_MODE: IMPLEMENTATION
CURRENT_PHASE: "00 — Host / WSL"
CURRENT_TASK: IMPL-P00-001
TASK_STATUS: IN_PROGRESS
TARGET_GATE: CODE_REVIEW_PASS
PHASE_GATE: HOST_READY
MODE_TRANSITION: "EARLY CODE_REVIEW COMPLETED FAIL; returned to IMPLEMENTATION"

REQUIREMENTS_BASELINE: "AI VIDEO SERVER — SINGLE CHAT WORKFLOW BLUEPRINT V2"
REVIEWED_DESIGN: "Phase00 exact Design V2 — REVIEW-P00-002 PASS"
FROZEN_DECISIONS: "FD-01…FD-08 unchanged"
APPROVED_PHASE00_DESIGN: "D00-01…D00-14 exact V2"
APPROVED_CONTRACT_SET_DIGEST: f259656c48ed24c15bd48da2bb040950ed94d8edcf1473cf6456b96578c933ee

CURRENT_VERIFIED_DELIVERY: "0.1.0.dev8 / PARTIAL_SOURCE_DROP_DEV8"
AUTHOR_COMPLETE: false
CODE_REVIEW_HANDOFF_READY: false

DEV8_PACKAGE: IMPL-P00-001_IMPLEMENTATION_PACKAGE_V8.zip
DEV8_SIZE_BYTES: 1091121
DEV8_SHA256: d4e6b67eebd40fbc173f85205792499021cf6eea9b82309e54c2a76a9a9e3cb5
DEV8_DRIVE_FILE_ID: 125T2wVf0CVkcmQND0PSmF3HHvXh8AgxD
RAW_REDOWNLOAD_SHA_VERIFIED: true
SOURCE_DIFF_SHA256: c9c519dc4bb0cc99135ffdd6884f31a573bbd191f9141ac9ad2484a4b030560e

WORKSPACE_AUTHOR_TESTS: "683 PASS / 0 failure / 0 error / 0 skip"
STATIC_AUTHOR_CHECKS: "92 PASS / 0 failed"
SOURCE_CONTENT_DIGEST: e793fc78d622c987343d1b5e5d3909cb4c19d7b0bcbafbc32909f137a1894c08
TEST_CONTENT_DIGEST: f91b422b6ce4ffeee9fc516bff0dc00c8e4a6216ae98e94b977ac2ef00949021
NATIVE_WINDOWS_WSL: NOT_RUN
LAB: NOT_RUN
SITE: NOT_RUN
QUALIFICATION_ISSUED: false
HOST_READY: NOT_EVALUATED

LAST_CODE_REVIEW:
  WORK_ITEM: CODE-REVIEW-P00-001
  TARGET: dev8
  KIND: EARLY_OWNER_REQUESTED_REVIEW
  VERDICT: FAIL
  CODE_REVIEW_PASS: false
  FORMAL_GATE_TRANSITION: NOT_ACTIVATED
  SOURCE_MODIFIED_DURING_REVIEW: false
  REVIEW_RECORD: reviews/CODE-REVIEW-P00-001_DEV8.md

OPEN_CODE_REVIEW_FINDINGS:
  - CR-P00-001 BLOCKER — formal review handoff premature / full scope incomplete
  - CR-P00-002 HIGH — owner-wait durable relabel lacks renewed authority check
  - CR-P00-003 HIGH — pending-reboot actual observation discarded at wait persistence boundary
  - CR-P00-004 MEDIUM — unbounded/untyped wait_observation persistence API

DEV_WORKSPACE_READY: true
WSL_WORKSPACE_ROOT: /home/dragon/ai-film-dev
CANONICAL_REPO_CLONE: /home/dragon/ai-film-dev/repo
ACTIVE_SOURCE_DIR: /home/dragon/ai-film-dev/source-dev8
ACTIVE_SOURCE_LOCAL_GIT: c44c2f87084f8082ce29af5935c6b47d03f7b96c
ROLLBACK_SOURCE_DIR: /home/dragon/ai-film-dev/source-dev7
DEV_VENV: /home/dragon/ai-film-dev/.venv
DIRECT_WSL_GITHUB_PUSH_AUTH: NOT_CONFIGURED

OPEN_DESIGN_GAPS: []
OPEN_VALIDATION_FAILURES: []
OPEN_IMPLEMENTATION_ITEMS: "IMPL-REM-01…08 at full-item scope"
IMPLEMENTATION_BLOCKERS: "IMPL-BLOCK-01…03"

AUTO_DOCUMENTATION_SYNC: true
NO_SILENT_KNOWLEDGE: true
LIVING_MEMORY_FILE: PROJECT_MEMORY.md
WORKSPACE_DOC: WORKSPACE_WSL.md
NEXT_ACTION: "Fix CR-P00-002/003/004 first; then continue prior pre-C3/checkpoint + nested E00 and remaining implementation scope. Re-enter formal CODE_REVIEW only after author-complete handoff."
```

## Code review result

The owner explicitly requested CODE_REVIEW against dev8 before the implementation handoff gate was ready. The review was performed under Blueprint review discipline and made no source changes.

Independent review rerun reproduced the exact dev8 author baseline: **683 PASS**, **92 static PASS**, source/test digests unchanged, source Git clean.

Verdict: **FAIL**.

The full report is `reviews/CODE-REVIEW-P00-001_DEV8.md`; the machine-readable verdict is `reviews/CODE-REVIEW-P00-001_DEV8.json`.

The formal `CODE_REVIEW_PASS` gate was not activated because dev8 remains explicitly partial. This does not erase the findings: `CR-P00-002…004` are concrete implementation defects/robustness gaps and must be fixed before the next formal review.

## Review findings requiring implementation

### CR-P00-001 — BLOCKER — incomplete handoff

Dev8 declares `AUTHOR_COMPLETE=false`, `CODE_REVIEW_HANDOFF_READY=false`, and all full-item `IMPL-REM-01…08` remain open. The package still records unfinished cross-stage evidence, publication recovery, non-DIRECT transport, dependency provenance, full 86-case causal harness and production-factory integration work.

This finding closes only when the full implementation exit condition is actually satisfied.

### CR-P00-002 — HIGH — reauthorization gap

In the owner-verification relabel branch of `RecoveryRunner`, the durable fence can be changed to `AWAITING_OWNER_VERIFICATION` after observation without the renewed `_reauthorize(...)` check used by successful reconciliation and pause/cancel branches.

A review-only executable scenario advanced synthetic authority beyond approval expiry during `d.reconcile`; dev8 still accepted and persisted the owner-wait relabel. Fix requires renewed authority/fence/request checks immediately before the durable transition and negative tests for expiry/generation/actor/request drift.

### CR-P00-003 — HIGH — reboot wait evidence loss

`native.lifecycle.classify_c3_process_result` produces actual `wait_reason` and normalized `pending_reboot`, but `SessionRunner` persists only the wait state. A review scenario confirmed the resulting fence had `AWAITING_REBOOT` with no `wait_observation`/pending-reboot facts.

Persist a bounded typed wait observation/digest at the durable wait boundary.

### CR-P00-004 — MEDIUM — wait context is unbounded

`Coordinator.awaiting` accepts any non-empty dictionary and deep-copies it into the durable fence. Define per-kind schemas/allowed keys and a serialized-size/privacy boundary; prefer digests/references over raw data.

## Non-finding retained from dev8 review

The explicit final `AWAIT_OWNER_RESTART` was not treated as a duplicate restart defect. Exact Design V2/T00-05 requires an owner-planned host restart lifecycle distinct from an engine-required reboot.

## Current implementation order

1. Fix `CR-P00-002`, `CR-P00-003`, `CR-P00-004` with targeted negative/positive author tests.
2. Full workspace regression/static checks and exact package persistence.
3. Continue prior pre-C3/checkpoint provenance selection + nested cross-stage E00 semantics.
4. Complete temp/incomplete publication + E17 recovery integration.
5. Complete reviewed non-DIRECT transport.
6. Complete causal 86-case controller/oracles and production-factory author integration.
7. Close `IMPL-REM-01…08`, produce author-complete candidate and set `CODE_REVIEW_HANDOFF_READY=true` only when justified.
8. Run `CODE-REVIEW-P00-001` again on the exact final candidate.

## Current-mode prohibitions

- no FD/D00/public/reviewed-contract changes or acceptance lowering;
- no native Windows/WSL/LAB/SITE/guest/live-network provisioning/validation during authoring;
- no process exit, fixture flag, author test count or envelope label treated as native proof;
- no deletion of unresolved durable state as a recovery shortcut;
- no fake production backend;
- no self-approved code review, qualification or HOST_READY;
- no useful reusable discovery left only in chat.

## Implementation exit condition

`IMPL-P00-001` exits IMPLEMENTATION only when the full source/harness/docs/test candidate is author-complete, all REM scope is actually closed or correctly managed, no hidden stub remains in reviewed scope, required author tests are clean, exact candidate is durably reviewable, and `CODE_REVIEW_HANDOFF_READY=true` is evidence-backed. Only then activate the formal `CODE_REVIEW_PASS` gate.
