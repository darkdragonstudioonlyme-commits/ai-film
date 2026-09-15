# AI Film Server — Persistent Project Control Plane

A fresh chat must be able to resume correctly without the previous transcript.

## Cold start

1. `PROJECT_STATE.md`
2. `NEXT_WORK_ITEM.md`
3. `WORKFLOW_ROUTER.md`
4. `DOCUMENTATION_MAP.md`
5. `EXECUTION_LANES.md`
6. fresh selected lane `LANE_STATE.md`
7. `TEST_STRATEGY.md` for any test-bearing workflow
8. `SELF_LEARNING_SYSTEM.md` when work is stalled/repeated/wrong or yields reusable improvement
9. `KNOWLEDGE_LIFECYCLE.md` when policy/know-how/architecture ownership or pruning matters
10. relevant `PROJECT_MEMORY.md`
11. `GIT_WORKFLOW.md`, `WORKSPACE_WSL.md`, `SERVER_ENVIRONMENT.md` as applicable
12. task-specific approved contracts/source/evidence

Run governance checks before consequential routing in the prepared workspace.

## Routing shorthand

- `continue` → deterministic `WORKFLOW_ROUTER.md` decision; do not ask for known context.
- source change/finding fix → IMPLEMENT.
- exact candidate review → REVIEW.
- material documentation-policy change → DOC-DESIGN → DOC-REVIEW → DOC-AUDIT.
- repeated deadlock/inefficiency/wrong-result pattern → retrospective/self-learning route.

README is version-agnostic by design; mutable truth lives in its owning state/work-item artifacts.
