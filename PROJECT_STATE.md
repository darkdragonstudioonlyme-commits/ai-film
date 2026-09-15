# AI-FILM-SERVER — CANONICAL PROJECT STATE V16

> Read this file first in every new chat. It contains current operational truth only. Reusable lessons live in `PROJECT_MEMORY.md`; exact next work lives in `NEXT_WORK_ITEM.md`.

## Fast resume snapshot

```yaml
PROJECT: AI-FILM-SERVER
STATE_VERSION: 16
REPOSITORY: darkdragonstudioonlyme-commits/ai-film
DEFAULT_BRANCH: main

CURRENT_MODE: IMPLEMENTATION
CURRENT_PHASE: "00 — Host / WSL"
CURRENT_TASK: IMPL-P00-001
TASK_STATUS: IN_PROGRESS
TARGET_GATE: CODE_REVIEW_PASS
PHASE_GATE: HOST_READY
MODE_TRANSITION: NONE

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
CODE_REVIEW: NOT_PERFORMED
HOST_READY: NOT_EVALUATED

DEV_WORKSPACE_READY: true
WSL_WORKSPACE_ROOT: /home/dragon/ai-film-dev
CANONICAL_REPO_CLONE: /home/dragon/ai-film-dev/repo
ACTIVE_SOURCE_DIR: /home/dragon/ai-film-dev/source-dev8
ACTIVE_SOURCE_LOCAL_GIT: c44c2f87084f8082ce29af5935c6b47d03f7b96c
ROLLBACK_SOURCE_DIR: /home/dragon/ai-film-dev/source-dev7
DEV_VENV: /home/dragon/ai-film-dev/.venv
DIRECT_WSL_GITHUB_PUSH_AUTH: NOT_CONFIGURED

OPEN_FINDINGS: []
OPEN_DESIGN_GAPS: []
OPEN_VALIDATION_FAILURES: []
OPEN_IMPLEMENTATION_ITEMS: "IMPL-REM-01…08 at full-item scope"
IMPLEMENTATION_BLOCKERS: "IMPL-BLOCK-01…03"

AUTO_DOCUMENTATION_SYNC: true
NO_SILENT_KNOWLEDGE: true
LIVING_MEMORY_FILE: PROJECT_MEMORY.md
WORKSPACE_DOC: WORKSPACE_WSL.md
NEXT_ACTION: "Prior pre-C3/checkpoint provenance selection + nested cross-stage E00 semantics."
```

**Do not transition to CODE_REVIEW.** Dev8 is verified author work, not an author-complete Phase00 candidate.

## Persistence model

- **GitHub** is canonical for project state, living memory, next work, workflow, delivery records and review history.
- **Google Drive raw artifacts** are the byte-exact packaged-delivery recovery anchors.
- **WSL local Git** is the authoring diff/rollback workspace; local commits are not remote approval.

The dev8 artifact was uploaded by file reference, downloaded again as raw bytes, and re-hashed. Size and SHA-256 matched exactly. A duplicate accidental Drive upload was deleted; `125T2wVf0CVkcmQND0PSmF3HHvXh8AgxD` is the canonical dev8 file ID.

## Dev8 lifecycle increment

Dev8 changed implementation behavior only; reviewed plan operations/contracts remain unchanged.

Implemented/hardened:

1. `ENABLE_PREREQUISITES` / `INSTALL_RUNTIME` cannot advance from process exit alone if Windows observations show pending reboot; the durable step waits at `AWAITING_REBOOT/20`.
2. Existing `3010 → AWAITING_REBOOT` is preserved.
3. Reconciliation from reboot wait requires a changed host boot witness and cleared pending-reboot indicators before the original step can commit.
4. C3 actions completed after reboot consume affected-resource owner postchecks before terminal commit.
5. Missing owner postcondition evidence may retain/relabel only an existing operator-wait fence as `AWAITING_OWNER_VERIFICATION/20`; mutation is not replayed.
6. OOBE owner verification remains distinct and does not invent reboot semantics.
7. The explicit final `AWAIT_OWNER_RESTART` remains in reviewed plans. Design V2/T00-05 requires an owner-planned host restart lifecycle; an earlier engine-required reboot is not silently treated as the same reviewed boundary.

Targeted dev8 lifecycle suite: **10 PASS**. Full workspace regression: **683 PASS**. Static checks: **92 PASS**.

These are synthetic/POSIX author results only. They do not establish Windows/WSL/LAB/SITE behavior, qualification, CODE_REVIEW_PASS or HOST_READY.

## WSL workspace

Active author workspace:

```text
/home/dragon/ai-film-dev/source-dev8
branch: dev8-baseline
commit: c44c2f87084f8082ce29af5935c6b47d03f7b96c
```

Rollback dev7 remains preserved at `/home/dragon/ai-film-dev/source-dev7` and was reset clean to its exact dev7 baseline.

Use:

```bash
source /home/dragon/ai-film-dev/env.sh
/home/dragon/ai-film-dev/test.sh
```

The helper stores actual run evidence outside the source tree and restores tracked generated evidence so verification-only runs keep source Git clean. Direct WSL `git push` is not authenticated; remote writes continue through the connected GitHub connector. Do not store PATs/tokens in plaintext.

## Open implementation scope

All full-item REM entries remain OPEN despite dev7/dev8 progress:

- `IMPL-REM-01`: remaining effective-profile/eligibility/native-factory route closure.
- `IMPL-REM-02`: remaining exhaustion/interrupted-reader/lifecycle journal procedures.
- `IMPL-REM-03`: remaining guest/bootstrap dependency trust, source epochs and prior pre-C3/checkpoint proof selection.
- `IMPL-REM-04`: remaining service/OOBE/restart/resume/factory combinations and actual native coverage.
- `IMPL-REM-05`: prolonged/multi-stage resume/later request/recovery-publication interactions.
- `IMPL-REM-06`: non-DIRECT transport + terminal/restore integration.
- `IMPL-REM-07`: nested cross-stage E00, prior pre-C3/checkpoint selection, temp/incomplete publication and remaining E17 integration.
- `IMPL-REM-08`: causal preparations/controllers/oracles for all normative 86 T/F/subcases + production-factory author integration.

## Exact next implementation order

Next coherent increment:

1. inspect E00 stage semantics, prior-evidence graph and pre-C3/checkpoint requirements;
2. implement exact prior pre-C3/checkpoint provenance selection without using envelope labels as proof;
3. close nested cross-stage E00 field/source selection that can be resolved without contract change;
4. add targeted positive/negative author tests for unrelated/tampered/ambiguous/stale prior evidence and stage applicability;
5. run full regression/static checks;
6. Documentation Sync Gate + exact artifact persistence + remote state verification.

Then proceed separately to temp/incomplete bundle/E17 recovery, reviewed non-DIRECT transport, full causal 86-case controller work, and production-factory author integration.

See `NEXT_WORK_ITEM.md` for executable detail.

## Current-mode prohibitions

- no FD/D00/public/reviewed-contract changes or acceptance lowering;
- no native Windows/WSL/LAB/SITE/guest/live-network provisioning/validation during authoring;
- no process exit, fixture flag, author test count or envelope label treated as native proof;
- no deletion of unresolved durable state as a recovery shortcut;
- no fake production backend;
- no self-approved code review, qualification or HOST_READY;
- no user host data requested as substitute for missing source work;
- no useful reusable discovery left only in chat.

## Exit condition

`IMPL-P00-001` exits IMPLEMENTATION only when the full source/harness/docs/test candidate is author-complete, all REM scope is actually closed or correctly managed, no hidden stub remains in reviewed scope, required author tests are clean, exact candidate is durably reviewable, and `CODE_REVIEW_HANDOFF_READY=true` is evidence-backed. Only then transition to `CODE_REVIEW / CODE-REVIEW-P00-001`.
