# AI-FILM-SERVER — Documentation Map and Freshness Contract

## Cold-start read path

```text
PROJECT_STATE
→ NEXT_WORK_ITEM
→ WORKFLOW_ROUTER
→ DOCUMENTATION_MAP
→ EXECUTION_LANES
→ fresh selected LANE_STATE
→ TEST_STRATEGY / SELF_LEARNING_SYSTEM as relevant
→ PROJECT_MEMORY
→ GIT_WORKFLOW / WORKSPACE_WSL / SERVER_ENVIRONMENT
→ task-specific contracts/source/evidence
```

## Source-of-truth matrix

| Artifact | Owns | Update trigger |
|---|---|---|
| `PROJECT_STATE.md` | global current truth, durable/WIP/review identities, gates | global truth changes |
| `NEXT_WORK_ITEM.md` | exact resumable workflow + test contract + return routes | active workflow changes |
| `PROJECT_ROADMAP.md` | milestone graph/closure | roadmap changes |
| `WORKFLOW_ROUTER.md` | deterministic routing, block/retro/test-failure return paths | routing changes |
| `EXECUTION_LANES.md` | independent workflow permissions/handoffs | trust model changes |
| `TEST_STRATEGY.md` | business-first test doctrine and test-change classification | test policy changes |
| `SELF_LEARNING_SYSTEM.md` | deadlock/inefficiency triggers, retrospective/recovery loop | learning policy changes |
| `KNOWLEDGE_LIFECYCLE.md` | policy/know-how/architecture lifecycle and pruning | knowledge governance changes |
| `SERVER_ENVIRONMENT.md` | observed environment + model-evaluation readiness rules | environment/readiness changes |
| `PROJECT_MEMORY.md` | compact reusable lessons not already fully owned by policy | reusable learning |
| `GIT_WORKFLOW.md` | Git/artifact/persistence policy | persistence policy changes |
| `WORKSPACE_WSL.md` | local paths/helpers/tool ownership | workspace changes |
| lane `LANE_STATE.md` | lane-local active target/output | lane state changes |
| `reviews/*` / `deliveries/*` | immutable exact review/delivery history | completion only |
| checkpoints | immutable milestone snapshot | milestone only |
| `activation/*` | pre-reviewed mechanical promotion payload; not current truth until applied | material governance activation |

## Freshness and anti-drift rules

1. Fresh-fetch relevant remote refs before consuming lane state.
2. Run runtime reconciliation in the prepared workspace before destructive reset, handoff or formal review.
3. Mutable dev/version numbers belong only to current state/work-item/lane/review/delivery/history owners; policy/router/roadmap docs stay version-agnostic.
4. WIP must be labeled mutable/non-reviewable with a durable base identity.
5. Environment facts are observations with timestamp/fingerprint; absence of a tool is not proof that the physical host lacks the capability.
6. README/CHAT_HANDOFF route; they do not duplicate current version/state.
7. Every root Markdown file must be an active mapped control-plane document or match the immutable checkpoint naming pattern; obsolete status files are removed from the active tree and remain recoverable through Git history.

## Documentation Sync Gate

Before a meaningful output is durable ask:

```text
global truth changed?        → PROJECT_STATE
next workflow/test contract? → NEXT_WORK_ITEM
roadmap changed?             → PROJECT_ROADMAP
routing/deadlock policy?     → WORKFLOW_ROUTER / SELF_LEARNING_SYSTEM
workflow trust changed?      → EXECUTION_LANES
business test doctrine?      → TEST_STRATEGY
environment changed?         → SERVER_ENVIRONMENT + snapshot
reusable lesson?             → PROJECT_MEMORY
knowledge obsolete/promoted? → KNOWLEDGE_LIFECYCLE compaction/pruning
workspace changed?           → WORKSPACE_WSL
review/delivery/milestone?   → immutable record/checkpoint
```

Run `/usr/bin/python3 tools/run_governance_checks.py`. Automated checks are guardrails; independent review/audit remains required for material governance change.
