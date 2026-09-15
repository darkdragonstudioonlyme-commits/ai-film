# New Chat Handoff — AI-FILM-SERVER

Use `darkdragonstudioonlyme-commits/ai-film` as the persistent project control plane. Do not rely on previous chat history.

## Cold start

1. Fresh-fetch `main` and relevant lane refs.
2. Read `PROJECT_STATE.md`.
3. Read `NEXT_WORK_ITEM.md`.
4. Read `WORKFLOW_ROUTER.md`.
5. Read `EXECUTION_LANES.md` and select exactly one workflow/lane.
6. Read `DOCUMENTATION_MAP.md` and the selected lane's freshly fetched `LANE_STATE.md`.
7. Scan relevant `PROJECT_MEMORY.md`; use `SELF_LEARNING.md` for new reusable learning.
8. Read `GIT_WORKFLOW.md` + `POLICY_REGISTRY.md`; read `TEST_STRATEGY.md` before changing test behavior.
9. Read `WORKSPACE_WSL.md`; for model/benchmark work verify `SERVER_ENVIRONMENT.md` / `MODEL_EVALUATION.md`.
10. If degraded/recovering read `WORKFLOW_HEALTH.md` / `RECOVERY_PLAYBOOK.md`.
11. Read only task-specific contracts/source/evidence.

## If user says only “continue”

Do not ask them to repeat project context. Apply the routing algorithm in `WORKFLOW_ROUTER.md`. Current state may include uncommitted WIP; preserve/resume it when state says so.

## Trust boundary

Do not trust another workflow's PASS label. Verify immutable input identities and rerun the checks required by the consuming workflow. IMPLEMENT cannot review itself; REVIEW cannot patch source. Documentation governance V2 uses DOC-DESIGN → DOC-REVIEW → DOC-AUDIT.

## Self-learning

Persist reusable learning automatically. Candidate-specific defects become findings; reusable lessons become memory; recurring/safety-critical lessons are promoted into standing policy. A chat should leave the project easier to resume than it found it.
