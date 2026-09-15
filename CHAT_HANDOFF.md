# New Chat Handoff — AI-FILM-SERVER

Use GitHub repository `darkdragonstudioonlyme-commits/ai-film` as the persistent project handoff.

## Minimal bootstrap

1. Read `PROJECT_STATE.md` completely.
2. Read `NEXT_WORK_ITEM.md` completely.
3. Read `EXECUTION_LANES.md`.
4. Choose exactly one lane from the user's requested task:
   - source changes / finding fixes / implementation → `IMPLEMENT`;
   - candidate review / verdict → `REVIEW`.
5. Read that branch's `LANE_STATE.md` (`lane/implement-p00` or `lane/review-p00`).
6. Scan relevant `PROJECT_MEMORY.md` entries.
7. Verify current remote `main` head.
8. Read `GIT_WORKFLOW.md` before persistent changes.
9. If using WSL/Desktop Commander, read `WORKSPACE_WSL.md` and verify the selected worktree Git status.
10. Read only the exact contracts/source/evidence required by the selected lane/work item.

Do **not** rely on the previous chat transcript and do not use an old checkpoint summary as current state.

## Lane discipline

### IMPLEMENT

Use `/home/dragon/ai-film-dev/implement` / branch `impl/p00`. This lane may modify source/tests/docs, run author tests, create commits/packages and fix review findings. It may not issue CODE_REVIEW verdicts.

### REVIEW

Use `/home/dragon/ai-film-dev/review`, detached at the exact handed-off candidate. This lane may inspect/retest/write findings and verdicts. It must not patch candidate source.

Candidate exchange is by exact source commit + package/artifact identity. REVIEW never auto-follows IMPLEMENT head.

## Global mode rule

`PROJECT_STATE.md` on `main` remains the only canonical mode/gate authority. The existence of two lanes does not allow two independent gate transitions.

Do not:

- mix IMPLEMENT and REVIEW permissions inside one work increment;
- change reviewed contracts inside IMPLEMENTATION;
- infer native/LAB/SITE validation from author/review tests;
- review uncommitted IMPLEMENT changes as a formal candidate;
- patch source in REVIEW;
- use memory entries to bypass design/review gates.

## Standing self-improving-memory rule

Persist reusable learning automatically:

```text
global state/gate change         → PROJECT_STATE.md
next executable work             → NEXT_WORK_ITEM.md
lane status/candidate            → selected lane LANE_STATE.md
reusable discovery/optimization  → PROJECT_MEMORY.md
workspace/environment change     → WORKSPACE_WSL.md + memory
lane/workflow improvement        → EXECUTION_LANES.md / GIT_WORKFLOW.md + memory
review finding/verdict           → reviews/* + state
milestone                        → new checkpoint MD + JSON
```

A meaningful increment is not complete until Documentation Sync Gate and remote identity verification are complete.
