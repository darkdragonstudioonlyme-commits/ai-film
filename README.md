# AI Film Server — Persistent Project Control Plane

This repository is the cross-chat control plane for **AI-FILM-SERVER**. A fresh chat must be able to resume without the previous transcript.

## Cold-start order

1. `PROJECT_STATE.md` — current global truth, accepted candidate, WIP, review target/findings.
2. `NEXT_WORK_ITEM.md` — exact resumable task and success/block/failure routes.
3. `WORKFLOW_ROUTER.md` — how to interpret “continue”, blockers, findings and gate transitions.
4. `EXECUTION_LANES.md` — independent workflow trust boundaries and immutable handoffs.
5. `DOCUMENTATION_MAP.md` — source-of-truth map, update triggers and freshness rules.
6. Read the selected lane's remote `LANE_STATE.md` after a fresh fetch.
7. Scan relevant `PROJECT_MEMORY.md` entries.
8. `GIT_WORKFLOW.md` before any persistent change.
9. `WORKSPACE_WSL.md` when using WSL/Desktop Commander.
10. Read only task-specific contracts/source/evidence referenced by state/next-work.

Never use an old checkpoint, cached remote-tracking ref, directory name or conversation summary as current truth.

## One-line routing

- “continue / tiếp tục” → follow `WORKFLOW_ROUTER.md`; do not ask what to do if state is sufficient.
- source/finding fix → IMPLEMENT workflow.
- immutable candidate review → REVIEW workflow.
- documentation architecture change → DOC-DESIGN → DOC-REVIEW.
- genuine reviewed-behavior conflict → DESIGN_GAP route; do not redesign in IMPLEMENTATION.

## No-silent-knowledge rule

Reusable discoveries must be persisted before an increment is durable. Current state, next work, roadmap, workflow policy, workspace facts and reusable memory have different owners; see `DOCUMENTATION_MAP.md`.
