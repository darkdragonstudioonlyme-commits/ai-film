# AI-FILM-SERVER — Documentation Map and Freshness Contract

## Purpose

This file tells a fresh chat **what each document means, when to read it, when to update it, and what must never be duplicated as mutable truth**.

## Canonical read path

```text
PROJECT_STATE
→ NEXT_WORK_ITEM
→ WORKFLOW_ROUTER
→ EXECUTION_LANES
→ DOCUMENTATION_MAP
→ selected remote LANE_STATE
→ relevant PROJECT_MEMORY / SELF_LEARNING
→ GIT_WORKFLOW / POLICY_REGISTRY / WORKSPACE_WSL
→ TEST_STRATEGY when judging/changing tests
→ SERVER_ENVIRONMENT / MODEL_EVALUATION for benchmark/model work
→ RECOVERY_PLAYBOOK / WORKFLOW_HEALTH when degraded or recovering
→ task-specific contracts/source/evidence
```

## Source-of-truth matrix

| Artifact | Owns | Must update when | Must NOT own |
|---|---|---|---|
| `PROJECT_STATE.md` | current global mode/phase/gates, durable candidate, WIP pointer, last review, open blockers/findings | any global truth changes | long history, detailed how-to |
| `NEXT_WORK_ITEM.md` | exact resumable action, input identity, success/fail/block routes | active work or routing changes | project history |
| `PROJECT_ROADMAP.md` | ordered phase/work milestones and completion criteria | roadmap/order/closure criteria change | current low-level WIP details |
| `WORKFLOW_ROUTER.md` | deterministic task routing and return paths | routing/process policy changes | source implementation details |
| `EXECUTION_LANES.md` | workflow permissions, independence, handoff contracts | lane/trust model changes | current candidate result details |
| lane `LANE_STATE.md` | lane-local active/waiting candidate and lane output | lane state changes | global gate authority |
| `PROJECT_MEMORY.md` | compact active learning index/provenance | useful learning discovered/superseded | detailed policy/procedure |
| `SELF_LEARNING.md` | learning lifecycle, promotion, measurement and compaction | learning process changes | candidate state |
| `TEST_STRATEGY.md` | business-first test authority and test-change rules | test philosophy/oracle policy changes | candidate-specific test results |
| `WORKFLOW_HEALTH.md` | deadlock/inefficiency triggers and meta-review | workflow health policy changes | implementation fixes |
| `POLICY_REGISTRY.md` | active/deprecated/superseded/retired operating policy index | policy lifecycle changes | historical full text |
| `SERVER_ENVIRONMENT.md` | observed server/environment snapshots and fact status | environment facts/profile changes | model recommendations |
| `MODEL_EVALUATION.md` | reproducible model benchmark workflow/result identity | model-eval methodology changes | current server facts |
| `RECOVERY_PLAYBOOK.md` | recovery routes for context/state/tool/artifact failures | recovery policy changes | normal next-work queue |
| `OPERATING_ARCHITECTURE.md` | process/trust architecture and separation of concerns | operating architecture changes | mutable status |
| `GIT_WORKFLOW.md` | commit/branch/artifact/persistence rules | persistence policy changes | project roadmap |
| `WORKSPACE_WSL.md` | current local paths/tools/worktree facts | workspace changes | gate decisions |
| `test-governance/*` | immutable TEST_CHANGE/TEST_GAP/TEST_REVIEW records | material test governance event | active test policy |
| `workflow-health/*` | immutable health/meta-review records | workflow meta-review completes | current routing state |
| `reviews/*` | immutable review verdict/findings for exact target | review completes | mutable current state |
| `deliveries/*` | immutable delivery identity | delivery closes | next work |
| `AI_FILM_STATE_CHECKPOINT_Vn.*` | immutable milestone snapshot | milestone only | current truth |

## Freshness rules

1. Before reading lane state, fetch `main` and the relevant lane refs from origin.
2. `PROJECT_STATE.md` may describe an uncommitted WIP, but must label it `WIP / NOT_DURABLE / NOT_REVIEWABLE` and identify the durable base commit.
3. A durable candidate is a commit/package identity; a WIP is never promoted by wording alone.
4. `NEXT_WORK_ITEM.md` must point at the actual active WIP/candidate, not an older delivery number.
5. README/CHAT_HANDOFF must remain version-agnostic; they route to current state rather than repeating mutable versions.
6. Historical checkpoints/review records are evidence, not current pointers. Superseded documentation-system designs live under `history/` and must not be used as active policy.

## Documentation Sync Gate

Before any meaningful workflow output is considered durable, answer:

```text
Did global truth change?      → PROJECT_STATE
Did exact next action change? → NEXT_WORK_ITEM
Did roadmap/closure change?   → PROJECT_ROADMAP
Did routing/process change?   → WORKFLOW_ROUTER / EXECUTION_LANES / GIT_WORKFLOW
Did reusable knowledge emerge?→ PROJECT_MEMORY + SELF_LEARNING lifecycle
Did test philosophy/oracle change?→ TEST_STRATEGY + `test-governance/*` + independent TEST_REVIEW
Did policy become stale/duplicate? → POLICY_REGISTRY + prune active docs
Did workflow become ineffective?   → WORKFLOW_HEALTH + `workflow-health/*` meta-review
Did environment/model context change?→ SERVER_ENVIRONMENT / MODEL_EVALUATION
Did recovery behavior change?       → RECOVERY_PLAYBOOK
Did workspace facts change?         → WORKSPACE_WSL
Did review/delivery finish?   → immutable review/delivery record
Did a milestone occur?        → checkpoint MD + JSON
```

If a new chat would repeat an investigation, choose a wrong lane, lose a blocker, trust stale evidence or forget a useful optimization, documentation sync is incomplete.

## Anti-duplication rule

Mutable facts should have one owner. Other docs link to the owner. If the same version/status is repeated for convenience, it must be clearly marked as a snapshot and never used to override the owning artifact.

## Automated check

Run the portable documentation check:

```bash
python3 tools/check_project_docs.py
```

In the prepared WSL workspace also run the runtime-state reconciliation check:

```bash
python3 tools/check_runtime_state.py
```

The first checks document structure/invariants. The second fresh-fetches lane refs and compares canonical state with remote lane state, local worktree identity/dirty set and the current durable artifact. Both are guardrails, not substitutes for DOC-REVIEW.
