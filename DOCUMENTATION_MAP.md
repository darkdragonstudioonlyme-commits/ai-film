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
→ relevant PROJECT_MEMORY
→ GIT_WORKFLOW / WORKSPACE_WSL
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
| `PROJECT_MEMORY.md` | reusable learnings/optimizations/failure patterns | useful learning discovered/superseded | transient candidate status |
| `GIT_WORKFLOW.md` | commit/branch/artifact/persistence rules | persistence policy changes | project roadmap |
| `WORKSPACE_WSL.md` | current local paths/tools/environment facts | workspace changes | gate decisions |
| `reviews/*` | immutable review verdict/findings for exact target | review completes | mutable current state |
| `deliveries/*` | immutable delivery identity | delivery closes | next work |
| `AI_FILM_STATE_CHECKPOINT_Vn.*` | immutable milestone snapshot | milestone only | current truth |

## Freshness rules

1. Before reading lane state, fetch `main` and the relevant lane refs from origin.
2. `PROJECT_STATE.md` may describe an uncommitted WIP, but must label it `WIP / NOT_DURABLE / NOT_REVIEWABLE` and identify the durable base commit.
3. A durable candidate is a commit/package identity; a WIP is never promoted by wording alone.
4. `NEXT_WORK_ITEM.md` must point at the actual active WIP/candidate, not an older delivery number.
5. README/CHAT_HANDOFF must remain version-agnostic; they route to current state rather than repeating mutable versions.
6. Historical checkpoints/review records are evidence, not current pointers.

## Documentation Sync Gate

Before any meaningful workflow output is considered durable, answer:

```text
Did global truth change?      → PROJECT_STATE
Did exact next action change? → NEXT_WORK_ITEM
Did roadmap/closure change?   → PROJECT_ROADMAP
Did routing/process change?   → WORKFLOW_ROUTER / EXECUTION_LANES / GIT_WORKFLOW
Did reusable knowledge emerge?→ PROJECT_MEMORY
Did workspace facts change?   → WORKSPACE_WSL
Did review/delivery finish?   → immutable review/delivery record
Did a milestone occur?        → checkpoint MD + JSON
```

If a new chat would repeat an investigation, choose a wrong lane, lose a blocker, trust stale evidence or forget a useful optimization, documentation sync is incomplete.

## Anti-duplication rule

Mutable facts should have one owner. Other docs link to the owner. If the same version/status is repeated for convenience, it must be clearly marked as a snapshot and never used to override the owning artifact.

## Automated check

Run:

```bash
python3 tools/check_project_docs.py
```

It checks core-file presence and critical cross-document state/routing invariants. It is a guardrail, not a substitute for DOC-REVIEW.
