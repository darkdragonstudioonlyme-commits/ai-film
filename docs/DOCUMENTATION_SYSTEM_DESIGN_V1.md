# Documentation System Design V1

## Goal

Make a fresh chat resume AI-FILM-SERVER quickly and correctly without previous conversation history, while making the control plane improve as work accumulates.

## User requirement mapping

| Requirement | Design response | Review proof |
|---|---|---|
| 1. Fresh chat knows current state/next work | `PROJECT_STATE` distinguishes durable candidate/WIP/review; `NEXT_WORK_ITEM` is exact resumable workflow | cold-start simulation |
| 2. Git/repository/know-how/policy | `GIT_WORKFLOW`, `DOCUMENTATION_MAP`, `WORKSPACE_WSL` | persistence/read-order audit |
| 3. Self-learning | memory lifecycle + policy promotion | learning/promotion simulation |
| 4. Independent workflows | immutable handoffs; source and docs lane pairs | trust-boundary review |
| 5. “Continue” auto-resumes and handles blockers/comments | deterministic `WORKFLOW_ROUTER` + workflow instance contract | continue/block/finding simulations |
| 6. Documentation roadmap | `PROJECT_ROADMAP` + `DOCUMENTATION_MAP` | navigation/coverage audit |

## Design principles

1. **One owner per mutable fact.** Other files link rather than copy version/status details.
2. **WIP is first-class.** Last durable candidate and current dirty worktree are separate facts.
3. **Immutable handoff.** Consumer workflows never inspect producer WIP as formal input.
4. **Distrust between workflows.** A consumer independently verifies identities and relevant checks.
5. **State drives action.** “Continue” means apply router rules, not ask the user to restate known work.
6. **Learning graduates to policy.** Memory is not a graveyard; recurring lessons become standing rules.
7. **History is immutable.** Reviews/deliveries/checkpoints preserve evidence but never override current state.

## Cold-start budget

A normal fresh chat should determine the next action by reading at most these control files before task-specific source/contracts:

```text
PROJECT_STATE
NEXT_WORK_ITEM
WORKFLOW_ROUTER
EXECUTION_LANES
DOCUMENTATION_MAP
selected LANE_STATE
relevant PROJECT_MEMORY entries
```

README and CHAT_HANDOFF exist only to route into this sequence.

## Anti-drift controls

- fresh fetch before lane-state reads;
- version-agnostic README/handoff;
- explicit WIP vs durable/review identities;
- automated `tools/check_project_docs.py`;
- independent DOC-REVIEW before material documentation-system changes reach `main`.

## Non-goals

This design does not change FD/D00/public contracts, does not close CR-P00 findings, does not convert author tests to native evidence, and does not make documentation itself proof of implementation correctness.
