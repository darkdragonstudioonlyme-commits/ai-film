# New Chat Handoff — AI-FILM-SERVER

Use GitHub repository `darkdragonstudioonlyme-commits/ai-film` as the persistent project source of truth.

## Minimal bootstrap

Read these files before doing project work:

1. `PROJECT_STATE.md`
2. `NEXT_WORK_ITEM.md`
3. `GIT_WORKFLOW.md`
4. `contracts/AI_VIDEO_SERVER_SINGLE_CHAT_WORKFLOW_BLUEPRINT_V2.md`
5. all Phase 00 V2 contracts referenced by `PROJECT_STATE.md`
6. `docs/IMPLEMENTATION_STATUS.md`
7. `docs/REMAINING_IMPLEMENTATION.md`
8. `docs/NATIVE_INTEGRATION_BOUNDARY.md`

Do not rely on the previous chat transcript. The repository state is intentionally detailed enough to resume without it.

## Expected current mode at repository initialization

```text
IMPLEMENTATION
Phase 00 — Host / WSL
IMPL-P00-001
Current verified implementation delivery: dev6 (partial)
Target gate: CODE_REVIEW_PASS
```

If repository state has advanced, follow the newer state instead.

## Operating constraints

Follow the one-active-mode state machine from the Blueprint. Do not mix implementation and review. Do not change reviewed contracts during implementation. Do not claim native validation from author tests. Persist every coherent tested increment to Git before starting the next one.
