# AI Film Server

Persistent project-state and cross-chat handoff repository for **AI-FILM-SERVER**.

## Fast start for a new chat

Read in this order:

1. `PROJECT_STATE.md` — **current truth**: mode, phase, baseline, blockers, gates and current status.
2. `NEXT_WORK_ITEM.md` — **exact next executable work** and forbidden actions.
3. `PROJECT_MEMORY.md` — **reusable discoveries, optimizations, risks and lessons** accumulated across chats.
4. Verify the current `main` remote head.
5. `GIT_WORKFLOW.md` — mandatory Git + automatic documentation-sync protocol before making persistent changes.
6. Read conditional artifacts referenced by state, e.g. `SOURCE_IMPORT_STATUS.md` while the exact dev6 persistence blocker is open.
7. Read authoritative design/contracts required by the current task.

`CHAT_HANDOFF.md` is a compact bootstrap prompt/template. Historical `AI_FILM_STATE_CHECKPOINT_Vn.md` files are immutable snapshots, not the current state database.

## Documentation model

```text
PROJECT_STATE.md     = where the project is now
NEXT_WORK_ITEM.md    = what to do next
PROJECT_MEMORY.md    = what the project has learned
GIT_WORKFLOW.md      = how work/state/memory must be persisted
CHECKPOINT_Vn        = immutable milestone history
Git commits/diffs    = exact change history
```

### Standing rule: no silent knowledge

When work discovers a reusable optimization, constraint, failure pattern, tooling behavior, risk, test lesson or clarification, the assistant must update `PROJECT_MEMORY.md` automatically. If that discovery changes status, next action or workflow, the corresponding canonical MD must also be updated before the increment is considered durable.

See the **Documentation Sync Gate** in `GIT_WORKFLOW.md`.

## Current checkpoint

Current project work remains:

```text
MODE: IMPLEMENTATION
PHASE: 00 — Host / WSL
WORK ITEM: IMPL-P00-001
VERIFIED DELIVERY: 0.1.0.dev6 / partial
TARGET GATE: CODE_REVIEW_PASS
```

The exact dev6 source tree is still **not accepted as a byte-identical GitHub mirror**. New implementation remains paused until the persistence prerequisite in `SOURCE_IMPORT_STATUS.md` is resolved and recorded in `PROJECT_STATE.md`.

Do not infer that missing Git source means missing implementation; dev6 is the verified author delivery outside Git. Do not reconstruct source from prose.
