# AI Film Server — Persistent Project Control Plane

This repository is the cross-chat control plane for **AI-FILM-SERVER**. A fresh chat must be able to resume without the previous transcript.

## Cold-start order

1. `PROJECT_STATE.md` — current global truth, accepted candidate, WIP, review target/findings.
2. `NEXT_WORK_ITEM.md` — exact resumable task and success/block/failure routes.
3. `WORKFLOW_ROUTER.md` — how to interpret “continue”, blockers, findings and gate transitions.
4. `WORKFLOW_CONTINUITY.md` — active RUN_ID, step cursor, interruption/idempotent resume rules.
5. `EXECUTION_LANES.md` — independent workflow trust boundaries and immutable handoffs.
6. `DOCUMENTATION_MAP.md` — source-of-truth map, update triggers and freshness rules.
7. Read the selected lane's remote `LANE_STATE.md` after a fresh fetch.
8. Scan relevant `PROJECT_MEMORY.md` entries and `SELF_LEARNING.md` when work produced reusable lessons.
9. `GIT_WORKFLOW.md` + `POLICY_REGISTRY.md` before persistent/policy changes.
10. `TEST_STRATEGY.md` before changing test expectations or harness semantics.
11. `WORKSPACE_WSL.md`; use `SERVER_ENVIRONMENT.md` / `MODEL_EVALUATION.md` for benchmark/model work.
12. Use `WORKFLOW_HEALTH.md` / `RECOVERY_PLAYBOOK.md` when degraded, blocked or recovering.
13. Read only task-specific contracts/source/evidence referenced by state/next-work.

Never use an old checkpoint, cached remote-tracking ref, directory name, conversation summary, or root `pyproject.toml` package metadata as current project/candidate truth unless `PROJECT_STATE.md` explicitly delegates that authority.

## One-line routing

- “continue / tiếp tục” → follow `WORKFLOW_ROUTER.md` + active `WORKFLOW_CONTINUITY.md` run; do not ask what to do if state is sufficient.
- source/finding fix → IMPLEMENT workflow.
- immutable candidate review → REVIEW workflow.
- documentation architecture change → DOC-DESIGN → DOC-REVIEW → DOC-AUDIT.
- genuine reviewed-behavior conflict → DESIGN_GAP route; do not redesign in IMPLEMENTATION.

## No-silent-knowledge rule

Reusable discoveries must be persisted before an increment is durable. Current state, next work, roadmap, workflow policy, workspace facts and reusable memory have different owners; see `DOCUMENTATION_MAP.md`.
