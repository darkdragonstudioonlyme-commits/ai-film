# New Chat Handoff — AI-FILM-SERVER

Use GitHub repository `darkdragonstudioonlyme-commits/ai-film` as the persistent project handoff.

## Minimal bootstrap — do this first

1. Read `PROJECT_STATE.md` completely.
2. Read `NEXT_WORK_ITEM.md` completely.
3. Read the active/relevant entries in `PROJECT_MEMORY.md`.
4. Verify the current remote `main` head.
5. Before making persistent changes, read `GIT_WORKFLOW.md` and follow its Documentation Sync Gate.
6. Read only the conditional/source/design artifacts referenced by current state.

Do **not** depend on the previous chat transcript.

## Expected state at checkpoint V13

```text
ACTIVE MODE: IMPLEMENTATION
PHASE: 00 — Host / WSL
WORK ITEM: IMPL-P00-001
CURRENT VERIFIED DELIVERY: 0.1.0.dev6 / PARTIAL_SOURCE_DROP_DEV6
TARGET GATE: CODE_REVIEW_PASS
AUTHOR COMPLETE: false
HOST_READY: NOT_EVALUATED
```

The exact current state in `PROJECT_STATE.md` overrides this summary if the project has advanced.

## Critical persistence prerequisite

At checkpoint V13 the exact dev6 source has **not yet been accepted as a byte-identical GitHub mirror**.

Do not reconstruct source from Markdown or conversation summaries and do not begin new implementation on an approximate copy.

Read `SOURCE_IMPORT_STATUS.md`. Implementation may resume only after repository state explicitly records:

```yaml
EXACT_DEV6_SOURCE_MIRRORED: true
SOURCE_IMPORT_VERIFIED: true
IMPLEMENTATION_MAY_RESUME: true
```

## Standing self-improving-memory rule

During any project work, automatically persist reusable learning:

- reusable discovery/optimization/tooling lesson/risk/test lesson → `PROJECT_MEMORY.md`;
- current state change → `PROJECT_STATE.md`;
- next action change → `NEXT_WORK_ITEM.md`;
- workflow/document-process improvement → `GIT_WORKFLOW.md` + `PROJECT_MEMORY.md`;
- milestone → new immutable checkpoint MD + JSON.

Do this **without waiting for the user to request documentation updates**.

A meaningful increment is not complete until the Documentation Sync Gate in `GIT_WORKFLOW.md` has been evaluated, applicable MD files updated, and persistent changes committed/pushed/verified.

## Operating constraints

Follow the one-active-mode state machine from the authoritative Blueprint. Do not mix implementation and review. Do not change reviewed contracts during implementation. Do not claim native validation from author tests. Do not use memory entries to bypass design/review gates.
