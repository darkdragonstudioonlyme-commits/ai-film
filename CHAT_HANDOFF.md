# New Chat Handoff — AI-FILM-SERVER

Use GitHub repository `darkdragonstudioonlyme-commits/ai-film` as the persistent project handoff.

## Read before doing anything

1. `PROJECT_STATE.md` — canonical detailed state.
2. `NEXT_WORK_ITEM.md` — exact next action.
3. `GIT_WORKFLOW.md` — mandatory commit/push discipline.
4. `SOURCE_IMPORT_STATUS.md` — whether exact dev6 source is safe to use.
5. `AI_FILM_STATE_CHECKPOINT_V12.md` and `AI_FILM_PROJECT_STATE_V12.json` — checkpoint views.

Do **not** rely on the previous chat transcript.

## Expected state at this checkpoint

```text
ACTIVE MODE: IMPLEMENTATION
PHASE: 00 — Host / WSL
WORK ITEM: IMPL-P00-001
CURRENT VERIFIED DELIVERY: 0.1.0.dev6 / PARTIAL_SOURCE_DROP_DEV6
TARGET GATE: CODE_REVIEW_PASS
AUTHOR COMPLETE: false
HOST_READY: NOT_EVALUATED
```

## Critical persistence prerequisite

At checkpoint V12 the exact dev6 source has **not yet been accepted as a byte-identical GitHub mirror**. Do not reconstruct it from prose and do not start new implementation on an approximate copy.

Read `SOURCE_IMPORT_STATUS.md`. Only after the repository records both:

```yaml
EXACT_DEV6_SOURCE_MIRRORED: true
IMPLEMENTATION_MAY_RESUME: true
```

may the chat continue the implementation sequence from `NEXT_WORK_ITEM.md`.

## Operating constraints

Follow the one-active-mode state machine from the authoritative Blueprint. Do not mix implementation and review. Do not change reviewed contracts during implementation. Do not claim native validation from author tests.

After exact source persistence is established, every coherent implementation increment must be tested, documented, committed, pushed and remote-SHA-verified before starting the next increment.
