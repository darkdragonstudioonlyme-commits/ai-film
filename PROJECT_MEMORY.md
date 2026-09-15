# AI-FILM-SERVER — Living Project Memory

> Reusable knowledge only. Current state is `PROJECT_STATE.md`; routing policy is `WORKFLOW_ROUTER.md`; documentation ownership is `DOCUMENTATION_MAP.md`.

## Learning lifecycle

```text
discovery
→ classify
→ persist memory entry
→ apply to current work
→ if repeatedly useful / safety-critical: promote into standing policy
→ if superseded: mark SUPERSEDED, never silently delete history
```

A memory entry cannot approve architecture, close a gate or override reviewed contracts.

## Active Memory Index

| ID | Type | Rule / lesson | Policy promotion |
|---|---|---|---|
| MEM-20260915-001 | PROCESS | Separate current state, next work, reusable memory and immutable history. | `DOCUMENTATION_MAP.md` |
| MEM-20260915-002 | TOOLING | Exact baselines need byte-preserving transport + independent identity verification. | `GIT_WORKFLOW.md` |
| MEM-20260915-003 | TESTING | Author/review tests are not Windows/WSL/LAB/SITE proof. | router/lane policy |
| MEM-20260915-004 | PROCESS | Increment durable only after remote/artifact verification. | `GIT_WORKFLOW.md` |
| MEM-20260915-005 | SECURITY | Secret-scan public-repo deliveries. | `GIT_WORKFLOW.md` |
| MEM-20260915-010 | TESTING | Use documented src-layout runner; invocation failure ≠ source regression. | workspace policy |
| MEM-20260915-011 | SECURITY | Executable trust binds path + exact bytes + policy + pinned handle + witness. | implementation rule |
| MEM-20260915-015 | TESTING | Keep run evidence outside source baseline; restore generated tracked evidence. | workspace policy |
| MEM-20260915-016 | LIFECYCLE | Process terminal ≠ lifecycle terminal when reboot remains pending. | implementation/recovery rule |
| MEM-20260915-017 | RECOVERY | Reboot resume requires changed boot witness + cleared pending state. | implementation/recovery rule |
| MEM-20260915-021 | SECURITY | Re-authorize immediately before durable recovery-state changes. | implementation rule |
| MEM-20260915-024 | PROCESS | IMPLEMENT and REVIEW require separate mutable/immutable workspaces. | `EXECUTION_LANES.md` |
| MEM-20260915-025 | REVIEW | Review target identity never floats. | `EXECUTION_LANES.md` |
| MEM-20260915-027 | REVIEW | Delta finding closure is separate from full-gate verdict. | `WORKFLOW_ROUTER.md` |
| MEM-20260915-028 | TOOLING | Fresh fetch is mandatory before reading remote lane state; cached origin refs can be stale. | `GIT_WORKFLOW.md`, router |
| MEM-20260915-029 | PROCESS | Canonical state must distinguish durable candidate, uncommitted WIP and review target. | `PROJECT_STATE.md` schema |
| MEM-20260915-030 | LEARNING | Reusable discoveries graduate from memory into standing policy when recurring/safety-critical. | docs/git/router policy |
| MEM-20260915-031 | PROCESS | “Continue” is deterministic state routing, not a request for the user to restate the task. | `WORKFLOW_ROUTER.md` |
| MEM-20260915-032 | GOVERNANCE | Documentation design and documentation review must be independent like source implement/review. | `EXECUTION_LANES.md` |

## New governance lessons

### MEM-20260915-028 — Fetch before trusting lane state

Audit found a stale local remote-tracking `origin/lane/*` cache that still showed dev8 while GitHub's actual review lane was dev17. Future bootstrap must fetch relevant refs before reading lane state.

### MEM-20260915-029 — WIP is first-class state, not an error

Audit found canonical docs lagging while IMPLEMENT contained valid dev18 uncommitted work. State must preserve both last durable candidate and current WIP so a fresh chat neither loses work nor formally reviews mutable source.

### MEM-20260915-030 — Self-learning needs a promotion path

Storing lessons only in a growing memory file eventually makes them invisible. Recurring or safety-critical lessons are promoted into router/lane/git/documentation policy while memory retains provenance.

### MEM-20260915-031 — “Continue” should route automatically

When state is sufficient, a fresh chat should resume the active WIP, review handed-off candidate, fix review findings or advance the roadmap without asking the user to restate known context.

### MEM-20260915-032 — Documentation governance also needs independent review

The same author-bias problem applies to project-control Markdown. Material documentation-system changes use DOC-DESIGN → immutable commit → DOC-REVIEW before `main` promotion.

## Entry format for future learning

```yaml
MEMORY_ID:
TYPE:
STATUS: ACTIVE|SUPERSEDED
DISCOVERED_IN:
SUMMARY:
EVIDENCE:
IMPACT:
REUSABLE_RULE:
ACTION_TAKEN:
POLICY_PROMOTION:
SUPERSEDED_BY:
```
