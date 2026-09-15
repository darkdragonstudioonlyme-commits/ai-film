# AI Film Server

Persistent project-state and cross-chat handoff repository for **AI-FILM-SERVER**.

## Fast start for a new chat

Read in this order:

1. `PROJECT_STATE.md` — canonical global mode/phase/baseline/gates/findings.
2. `NEXT_WORK_ITEM.md` — current implementation/review disposition.
3. `EXECUTION_LANES.md` — independent IMPLEMENT / REVIEW permissions and immutable handoff protocol.
4. Choose the lane required by the user's task and read that branch's `LANE_STATE.md`:
   - `lane/implement-p00`
   - `lane/review-p00`
5. `PROJECT_MEMORY.md` — reusable discoveries/optimizations/risks/tooling/test/security lessons.
6. Verify current GitHub `main` head.
7. `GIT_WORKFLOW.md` — persistence + Documentation Sync Gate.
8. `WORKSPACE_WSL.md` when using Desktop Commander/WSL.
9. Read only the contracts/source/evidence required by the selected work item/lane.

Do not depend on previous chat history. Historical checkpoints are immutable snapshots, not current state.

## Documentation model

```text
PROJECT_STATE.md     = global current truth/gates
NEXT_WORK_ITEM.md    = current queue + lane disposition
EXECUTION_LANES.md   = lane isolation and handoff rules
lane/*/LANE_STATE.md = lane-specific current state
PROJECT_MEMORY.md    = reusable learned knowledge
GIT_WORKFLOW.md      = persistence/documentation protocol
WORKSPACE_WSL.md     = local worktrees/helpers/baselines
reviews/*            = immutable review records
CHECKPOINT_Vn        = immutable milestone history
Drive delivery ZIPs  = byte-exact packaged recovery anchors
```

## Standing rule: no silent knowledge

If work discovers a reusable optimization, constraint, failure pattern, tooling behavior, risk, test/security lesson or clarification, persist it automatically. If global state, lane state, next work, workspace or workflow changes, update its canonical file before the increment is durable.

## Lane rule

- source changes/finding fixes → **IMPLEMENT** lane;
- candidate review/verdict → **REVIEW** lane;
- never mix lane permissions inside one work increment;
- candidate exchange is by exact commit/package identity, never by following a mutable worktree.

The current delivery/version is intentionally not duplicated here. Always read `PROJECT_STATE.md`.
