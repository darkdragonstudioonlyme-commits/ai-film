# AI-FILM-SERVER — Documentation Map and Freshness Contract

## Purpose

This file tells a fresh chat **what each document means, when to read it, when to update it, and what must never be duplicated as mutable truth**.

## Canonical read profiles

**CORE (every new session):** fresh canonical/lane refs; `PROJECT_STATE.md`, `NEXT_WORK_ITEM.md`, `WORKFLOW_ROUTER.md`; the selected lane and existing run. Read the current policy profile below before the corresponding action. Compact prompts reduce user typing, not evidence obligations.

| Profile | Additional required reads |
|---|---|
| Resume / write / handoff | `WORKFLOW_CONTINUITY.md`, `GIT_WORKFLOW.md`, `EXECUTION_LANES.md`; relevant workspace and contract identities |
| Implement / code review / validation | exact accepted Blueprint + phase contracts/approved changes, `TEST_STRATEGY.md`, scoped source/evidence and applicable safety/recovery rules |
| Documentation change | this map, affected policy owners, `POLICY_REGISTRY.md`, `SELF_LEARNING.md` when learning semantics change |
| Full DOC-AUDIT | **all 20 active root control documents**, every changed artifact, referenced current governance/learning/test/measurement evidence and exact relevant product contracts; no summary-only audit |
| Health / recovery | `WORKFLOW_HEALTH.md`, `RECOVERY_PLAYBOOK.md`, relevant immutable learning records and current lifecycle entries |
| Model / film quality | `MODEL_EVALUATION.md`, `SERVER_ENVIRONMENT.md`, exact evaluation baseline and relevant film design contract |

Machine lifecycle reconciliation still runs at bootstrap; selective prose loading does not skip it. Read active policy content before applying it. Within one session, unchanged blobs already read may be reused by exact identity; a new session must retrieve its required profile again. Record selected profile, actual file identities and omitted non-applicable scopes in the run/review. A digest or summary alone is not a substitute for first reading required semantics. Expand context when a reference is ambiguous; never truncate a safety contract to meet a token target.

Product contracts live in the **exact source commit** selected by `SOURCE_VISIBILITY.EXACT_SOURCE_IDENTITY`, not necessarily on `main`. Resolve `contracts/AI_VIDEO_SERVER_SINGLE_CHAT_WORKFLOW_BLUEPRINT_V2.md`, the phase approval's normative set, and approved candidate-specific changes there. Historical candidate wording in an immutable contract is interpreted with its external approval record, not rewritten in place.

## Source-of-truth matrix

| Artifact | Owns | Must update when | Must NOT own |
|---|---|---|---|
| `PROJECT_STATE.md` | current snapshot selector and current global mode/phase/gates, durable candidate, active run, blockers, documentation release, **derived learning aggregates** | any global truth changes | detailed learning lifecycle/history |
| `NEXT_WORK_ITEM.md` | exact resumable action, input identity, success/fail/block routes | active work or routing changes | project history |
| `PROJECT_ROADMAP.md` | ordered phase/work milestones and completion criteria | roadmap/order/closure criteria change | current low-level WIP details |
| `WORKFLOW_ROUTER.md` | deterministic task routing, bootstrap reconciliation and return paths | routing/process policy changes | source implementation details |
| `WORKFLOW_CONTINUITY.md` | logical run identity, write-ahead step journal, idempotent resume/reconciliation | interruption/continuation semantics change | product acceptance/current candidate verdict |
| lane `workflow-runs/*` | live per-run step cursor, intents, exact outputs, replay policy | before/after duplicate-prone steps and interruption recovery | global gate authority |
| `EXECUTION_LANES.md` | workflow permissions, independence, generic handoff contracts | lane/trust model changes | release-specific branch/worktree names or current candidate details |
| lane `LANE_STATE.md` | lane-local active/waiting candidate, lane output and source-visibility status | lane state changes | global gate authority |
| `PROJECT_MEMORY.md` | compact active lesson index/provenance pointers | useful learning activated/superseded | current learning lifecycle state |
| `learning/LEARNING-*.md` | immutable learning observation/provenance | new reusable learning is discovered | current review/activation/effectiveness state |
| `learning/LEARNING_STATE.json` | canonical current learning review/activation/effectiveness lifecycle | learning lifecycle changes | observation/root-cause prose |
| `learning/measurements/*` | immutable semantic effectiveness receipts: metric, scope, sample, predicate, evidence identities and review | effectiveness is measured | mutable lifecycle state |
| `SELF_LEARNING.md` | learning process, guarded automation, lifecycle ownership and measurement | learning process changes | candidate state |
| `TEST_STRATEGY.md` | business-first test authority and test-change rules | test philosophy/oracle policy changes | candidate-specific test results |
| `WORKFLOW_HEALTH.md` | deadlock/inefficiency/learning-debt triggers and meta-review | workflow health policy changes | implementation fixes |
| `POLICY_REGISTRY.md` | active/deprecated/superseded/retired operating policy index | policy lifecycle changes | historical full text |
| `SERVER_ENVIRONMENT.md` | environment methodology + current development-environment pointer | environment methodology/current pointer changes | historical snapshot details/model recommendations |
| `environments/*` | immutable exact environment snapshots | new material environment identity | mutable methodology |
| `MODEL_EVALUATION.md` | reproducible model benchmark methodology/result schema | model-eval methodology changes | historical results/current server facts |
| `model-evaluations/*` | immutable reviewed model evaluation results | evaluation completes | methodology |
| `RECOVERY_PLAYBOOK.md` | recovery routes for context/state/tool/artifact failures | recovery policy changes | normal next-work queue |
| `OPERATING_ARCHITECTURE.md` | process/trust architecture and separation of concerns | operating architecture changes | mutable status |
| `GIT_WORKFLOW.md` | commit/branch/artifact/persistence/source-addressability rules | persistence policy changes | project roadmap |
| `WORKSPACE_WSL.md` | stable local paths/tools/worktree capabilities | workspace changes | release-specific documentation worktree names or mutable candidate state |
| `test-governance/*` | immutable TEST_CHANGE/TEST_GAP/TEST_REVIEW records; every review must resolve its proposal/gap in the canonical tree or by exact immutable commit locator | material test governance event | active test policy |
| `workflow-health/*` | immutable health/meta-review records | workflow meta-review completes | current routing state |
| `workflow-health/metrics/*` | immutable comparable workflow-health measurement snapshots/baselines | comparable metric population/window closes | mutable current routing state |
| `reviews/*` | immutable review verdict/findings for exact target | review completes | mutable current state |
| `deliveries/*` | immutable delivery identity | delivery closes | next work |
| `AI_FILM_STATE_CHECKPOINT_Vn.md` / `AI_FILM_PROJECT_STATE_Vn.json` | immutable milestone snapshot; only the explicitly selected JSON is the current machine projection | milestone only | independent current authority without the selector |

## Freshness rules

1. Before reading lane state, fetch `main` and relevant lane refs from origin.
2. Documentation governance branch/worktree identities come from `PROJECT_STATE.md:DOCUMENTATION_GOVERNANCE`; standing prose must not pin one release's names.
3. A durable candidate is a commit/package identity; WIP is never promoted by wording alone.
4. `NEXT_WORK_ITEM.md` must point at the actual active WIP/candidate.
5. README/CHAT_HANDOFF remain version-agnostic and route to current state.
6. Historical checkpoints/reviews are evidence, not current pointers. Superseded designs live under `history/`.
7. A reusable learning is not applied merely because an immutable learning record exists; current lifecycle comes from `learning/LEARNING_STATE.json`.
8. `PROJECT_STATE` learning aggregates are derived from the lifecycle register and must be checker-equal.
9. An ineffective learning with no active successor/meta-review path is process debt.
10. `EFFECTIVE` requires semantic proof of the immutable success metric; evidence path existence or lifecycle-check PASS alone is not effectiveness proof.
11. Root/control-plane package metadata such as `pyproject.toml` is not current candidate/version/review authority unless `PROJECT_STATE` explicitly delegates that role. Current candidate truth comes from `PROJECT_STATE` and the exact source/package handoff.
12. A canonical TEST_REVIEW whose TEST_CHANGE/TEST_GAP cannot be resolved is provenance debt, even if the review verdict itself is present.
13. CI path-filter coverage is part of documentation governance: changes to lifecycle domains must either trigger their required checker or carry explicit manual audit evidence until automation is extended.

## Documentation Sync Gate

Before any meaningful workflow output is considered durable, answer:

```text
Did global truth change?      → PROJECT_STATE
Did exact next action change? → NEXT_WORK_ITEM
Did roadmap/closure change?   → PROJECT_ROADMAP
Did routing/process change?   → WORKFLOW_ROUTER / EXECUTION_LANES / GIT_WORKFLOW
Did reusable knowledge emerge?→ immutable learning record + PROJECT_MEMORY pointer
Did learning lifecycle change?→ learning/LEARNING_STATE.json + derived PROJECT_STATE aggregates
Did learning become ineffective or due for measurement?→ WORKFLOW_HEALTH + health record/meta-review
Did learning become EFFECTIVE? → semantic measurement receipt/health record proving metric scope + sample + predicate
Did test philosophy/oracle change?→ TEST_STRATEGY + canonical TEST_CHANGE/TEST_GAP + independent TEST_REVIEW
Did policy become stale/duplicate? → POLICY_REGISTRY + prune active docs
Did environment/model context change?→ SERVER_ENVIRONMENT/environments or MODEL_EVALUATION/model-evaluations
Did recovery behavior change?       → RECOVERY_PLAYBOOK
Did workflow step/progress change?  → owning lane workflow-runs ledger
Did source visibility/addressability change? → owning lane state + GIT_WORKFLOW
Did workspace facts change?         → WORKSPACE_WSL
Did review/delivery finish?         → immutable review/delivery record
Did a milestone occur?              → checkpoint MD + JSON
```

If a new chat would repeat an investigation, choose a wrong lane, lose a blocker, trust stale evidence, mistake a partial source snapshot for a full candidate, or trust stale learning lifecycle state, documentation sync is incomplete.

## Anti-duplication rule

Mutable facts have one owner. Other docs link to it. Historical fields embedded in immutable records are snapshots and may never override their current lifecycle/state owner.

## Automated checks

Portable documentation checks:

```bash
python3 tools/check_state_contract.py
python3 tools/check_project_docs.py
python3 tools/check_documentation_governance.py
python3 tools/check_learning_lifecycle.py
python3 tools/audit_documentation_v2.py
```

Prepared WSL reconciliation additionally runs:

```bash
python3 tools/check_workflow_continuity.py --require-remote
python3 tools/check_runtime_state.py
```

These guardrails do not substitute for independent DOC-REVIEW or holistic DOC-AUDIT. A checker PASS proves only the invariants it actually evaluates; reviewers must not elevate structural existence checks into semantic effectiveness proof.

## State projection and check scope

A current-state transaction prepares the intended Markdown, selected JSON and checkpoint together. `STATE_VERSION` is the sole selector; unrelated higher-numbered snapshots cannot select a different run. Do not edit historical snapshots. The shared state-contract guard rejects missing/duplicate selectors, malformed JSON and mismatched versions. Field-specific guards still own their stated parity checks; this is not complete schema validation of every nested business field.

`check_workflow_continuity.py` reports `SCHEMA_ONLY` when lane access is unavailable and no strict scope was requested. That result cannot close a handoff. CI and formal reconciliation use `--require-remote`; unavailable/failing lane retrieval then fails closed. Local worktree and live host checks remain distinct from remote ledger verification.

When a run binds a local worktree, formal local handoff also uses `--require-local`; remote-only CI may report `local=NOT_EVALUATED` and cannot close that local obligation. A local success checks HEAD identity only; dirty-tree/native status belongs to its applicable runtime/workspace guards.
