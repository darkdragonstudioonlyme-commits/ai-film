# AI Film Server

Persistent project-state and cross-chat handoff repository for **AI-FILM-SERVER**.

## Fast start for a new chat

Read in this order:

1. `PROJECT_STATE.md` — current truth: mode, phase, reviewed baseline, current delivery, gates, blockers and evidence status.
2. `NEXT_WORK_ITEM.md` — exact next executable increment, order, inputs and forbidden actions.
3. `PROJECT_MEMORY.md` — reusable discoveries/optimizations/risks/tooling/test/security lessons.
4. Verify current GitHub `main` head.
5. `GIT_WORKFLOW.md` — mandatory persistence + Documentation Sync Gate.
6. `WORKSPACE_WSL.md` when using Desktop Commander/WSL.
7. Read only the conditional contracts/source/evidence referenced by the current state/task.

Do not depend on previous chat history. `CHAT_HANDOFF.md` is a compact bootstrap prompt, not a second state database. Historical `AI_FILM_STATE_CHECKPOINT_Vn.md` files are immutable snapshots.

## Documentation model

```text
PROJECT_STATE.md     = where the project is now
NEXT_WORK_ITEM.md    = what to do next
PROJECT_MEMORY.md    = what the project has learned
GIT_WORKFLOW.md      = how state/source/evidence/memory must be persisted
WORKSPACE_WSL.md     = prepared local development environment
CHECKPOINT_Vn        = immutable milestone history
Git commits/diffs    = exact text/change ledger
Drive delivery ZIPs  = byte-exact packaged recovery anchors
```

## Standing rule: no silent knowledge

If work discovers a reusable optimization, constraint, failure pattern, tooling behavior, risk, test/security lesson or clarification, update `PROJECT_MEMORY.md` automatically. If current state, next work, workspace or workflow changes, update its canonical file before the increment is considered durable.

The current delivery/version is intentionally **not duplicated in this README**. Always read `PROJECT_STATE.md`; it overrides historical summaries and prevents README drift.
