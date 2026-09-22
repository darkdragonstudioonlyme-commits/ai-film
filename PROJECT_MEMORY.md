# AI-FILM — Shared operational knowledge index

Current learning lifecycle: `learning/LEARNING_STATE.json`. Policy authority:
`POLICY_REGISTRY.md`. Both ChatGPT and Claude use the same owners and task context.
This index routes retrieval; it does not activate a rule or repeat mutable state.

## Retrieve by the current task

| Need | Canonical owner / evidence domain |
|---|---|
| What to do, actor and gate | `PROJECT_STATE.md`, `NEXT_WORK_ITEM.md`, `WORKFLOW_ROUTER.md` |
| Resume without duplicate work | `WORKFLOW_CONTINUITY.md`, owning `workflow-runs/` |
| Source/artifact identity and secret discipline | `GIT_WORKFLOW.md`, exact handoff/manifest |
| Oracle, causal tests and design gaps | `TEST_STRATEGY.md`, `test-governance/`, exact phase contracts |
| Review independence and claims | `EXECUTION_LANES.md`, exact `reviews/` |
| Learning selection, invalidation and measurement | `SELF_LEARNING.md`, `learning/LEARNING_STATE.json` |
| Ineffective loops and comparable outcomes | `WORKFLOW_HEALTH.md`, `workflow-health/metrics/` |
| Workspace, recovery and environment scope | `WORKSPACE_WSL.md`, `RECOVERY_PLAYBOOK.md`, `SERVER_ENVIRONMENT.md` |
| Two-model context and delivery | `docs/DUAL_AI_COLLABORATION.md`, `docs/DUAL_AI_AUTOMATIC_HANDOFF.md` |

## Working view

Run `python3 tools/check_shared_workflow.py --knowledge` after lifecycle reconciliation.
Select relevant terminal lessons; attach exact bytes and successor warnings. An old
ACTIVE flag, a remembered rule or an index row never defeats current policy. A pending
measurement is disclosed; an ineffective/superseded record is not positive guidance.
Do not infer factual validity or complete relevance from structural filtering.

## Preserved provenance

The detailed MEM index remains byte-retrievable at exact Git commit
`5dbcaa5efbd27ee7ea4169328a38ef23fbb67b66:PROJECT_MEMORY.md`.
All original learning records and success metrics remain unchanged. This compaction
removes repeated rule summaries from default context, not safety rules or evidence.
New information uses existing finding/learning lifecycle; do not duplicate it by model.
