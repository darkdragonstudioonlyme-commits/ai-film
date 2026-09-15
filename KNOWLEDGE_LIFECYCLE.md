# AI-FILM-SERVER — Policy, Know-How and Knowledge Lifecycle

## Knowledge classes

| Class | Meaning | Authority |
|---|---|---|
| Approved architecture/design | reviewed structural/behavior decisions | Blueprint, FD, reviewed D00/design contracts |
| Policy | mandatory way work must be performed | owning reviewed policy MD |
| Know-how | reusable recommended technique | memory/know-how until promoted |
| Current state | what is true now | `PROJECT_STATE.md` / lane state |
| Environment fact | measured server/tool capability | `SERVER_ENVIRONMENT.md` + snapshot |
| History/evidence | what happened previously | reviews, deliveries, checkpoints, Git |

Do not copy architecture content into memory and later treat the copy as architecture authority.

## Active knowledge / authority index

| Layer | Active source | Role |
|---|---|---|
| Architecture authority | Blueprint V2 + FD-01…08 + exact reviewed Phase00 V2 contracts | product behavior/structure authority |
| Workflow routing policy | `WORKFLOW_ROUTER.md` | deterministic continuation/block/return routing |
| Workflow trust policy | `EXECUTION_LANES.md` | producer/consumer independence and handoff |
| Test policy | `TEST_STRATEGY.md` | business-first oracle/test-change rules |
| Learning/recovery policy | `SELF_LEARNING_SYSTEM.md` | deadlock/meta-review/self-improvement/recovery |
| Persistence policy | `GIT_WORKFLOW.md` | Git/artifact durability |
| Documentation ownership | `DOCUMENTATION_MAP.md` | source-of-truth/freshness/update owners |
| Knowledge lifecycle | this file | promotion/deprecation/pruning |
| Environment truth | `SERVER_ENVIRONMENT.md` + snapshot | measured server/model-eval readiness |
| Operational know-how | `PROJECT_MEMORY.md`, `WORKSPACE_WSL.md` | reusable techniques/environment usage |

Policy can change how work is performed but cannot silently change approved product architecture.

## Lifecycle states

Knowledge is `ACTIVE`, `DEPRECATED`, `SUPERSEDED` or `ARCHIVED`.

- `ACTIVE` — current and actionable.
- `DEPRECATED` — still temporarily referenced; replacement is named and migration is bounded.
- `SUPERSEDED` — no longer valid for current work; remove from active operational prose.
- `ARCHIVED` — retained only for history/audit.

Outdated rules must not remain mixed with active rules “for context”. Preserve history in Git/archive, not in the current operating instructions.

## Promotion and pruning

Reusable learning starts in `PROJECT_MEMORY.md`. When repeated, safety-critical or broadly useful, promote it into the owning policy/tool and leave only a compact provenance pointer in active memory.

Trigger knowledge compaction when any condition is met:

- active memory exceeds 40 entries;
- `PROJECT_MEMORY.md` exceeds 250 lines;
- more than 20% of active-memory entries are already promoted/superseded;
- a milestone closes a large class of work;
- a final audit finds duplicate/conflicting rules.

Compaction procedure:

```text
snapshot current memory to memory/archive/
→ keep ACTIVE/unresolved lessons in current memory
→ replace promoted detail with short index + policy link
→ remove superseded operational wording from active docs
→ run knowledge hygiene checker
→ independent review when policy meaning changes
```

Deletion from active docs is encouraged when the rule is obsolete; deletion from project history is not required.

## Version/freshness discipline

Mutable delivery/version numbers may live only in their owning current-state/work-item/lane/delivery/review records. Version-agnostic policy docs must not pin a current dev version.

Stale version/reference bugs are treated as `STATE_DRIFT` or `DOC_DRIFT`, never as harmless prose.

## Architecture index rule

Current architecture sources are referenced, not duplicated:

- authoritative Blueprint V2;
- FD-01…FD-08;
- exact reviewed Phase00 V2 design/acceptance/failure/evidence contracts;
- later reviewed architecture artifacts when created.

If implementation discovers a contradiction with these sources, route DESIGN_GAP instead of editing policy to hide it.
