# AI Film Server

Persistent project-state and Git handoff repository for **AI-FILM-SERVER**.

## Read first in a new chat

1. `PROJECT_STATE.md` — canonical detailed state.
2. `NEXT_WORK_ITEM.md` — exact next action and mode lock.
3. `GIT_WORKFLOW.md` — mandatory commit/push discipline.
4. `CHAT_HANDOFF.md` — compact new-chat bootstrap prompt.
5. `SOURCE_IMPORT_STATUS.md` — exact status of the dev6 source mirror.

## Current status

The repository has been initialized for work item `IMPL-P00-001`, Phase 00 — Host / WSL. The latest verified implementation delivery outside Git is `0.1.0.dev6` with 666 workspace tests PASS and 88 static checks PASS.

**Important:** the exact dev6 source tree is **not yet considered mirrored into GitHub**. Two attempted connector-based source/snapshot mirrors failed byte-identity checks and were removed from `main`. Do not infer that missing Git source means missing implementation; read `PROJECT_STATE.md` and `SOURCE_IMPORT_STATUS.md`.

No implementation work should resume until the exact dev6 source has been seeded through a Git-capable/file-preserving path and verified against the recorded package/content hashes.
