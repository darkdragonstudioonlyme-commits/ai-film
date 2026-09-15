# New Chat Handoff — AI-FILM-SERVER

Use GitHub repository `darkdragonstudioonlyme-commits/ai-film` as the persistent project handoff.

## Minimal bootstrap

1. Read `PROJECT_STATE.md` completely.
2. Read `NEXT_WORK_ITEM.md` completely.
3. Scan active/relevant entries in `PROJECT_MEMORY.md`.
4. Verify the current remote `main` head.
5. Read `GIT_WORKFLOW.md` before persistent changes.
6. If using WSL/Desktop Commander, read `WORKSPACE_WSL.md` and verify the prepared local source Git status.
7. Read only the exact reviewed contracts/source/evidence required by the current work item.

Do **not** rely on the previous chat transcript and do not use an old checkpoint summary as current state.

## Mode rule

Follow the one-active-mode state machine from the authoritative Blueprint. The exact current mode/phase/work item must come from `PROJECT_STATE.md` and `NEXT_WORK_ITEM.md`.

Do not:

- mix IMPLEMENTATION with CODE_REVIEW/VALIDATION responsibilities;
- change reviewed contracts inside IMPLEMENTATION;
- infer native/LAB/SITE validation from author tests;
- use memory entries to bypass design/review gates;
- reconstruct a delivery from prose when an exact recovery artifact/worktree exists.

## Standing self-improving-memory rule

Persist reusable learning automatically:

```text
state/gate/evidence change      → PROJECT_STATE.md
next executable work change     → NEXT_WORK_ITEM.md
reusable discovery/optimization → PROJECT_MEMORY.md
workspace/environment change    → WORKSPACE_WSL.md + PROJECT_MEMORY.md
workflow improvement            → GIT_WORKFLOW.md + PROJECT_MEMORY.md
milestone                        → new checkpoint MD + JSON
```

A meaningful increment is not complete until the Documentation Sync Gate is evaluated, exact delivery/state persistence is verified, and the next chat can identify the active baseline without conversation history.
