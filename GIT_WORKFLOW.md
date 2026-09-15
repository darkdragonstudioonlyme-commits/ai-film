# AI-FILM-SERVER Git + Documentation Persistence Workflow

This repository is the persistent cross-chat handoff for AI-FILM-SERVER.

## 1. Mandatory persistence rule

A coherent project increment is **not durable** until all applicable source/tests/evidence/docs have been synchronized, committed, pushed, and the remote state has been verified.

The standing workflow is:

```text
VERIFY REMOTE STATE
→ WORK IN THE CURRENT MODE ONLY
→ TEST / COLLECT EVIDENCE
→ DOCUMENTATION SYNC GATE
→ DIFF REVIEW
→ SECRET SCAN
→ COMMIT
→ PUSH
→ VERIFY REMOTE
→ ONLY THEN CONTINUE
```

This applies to code, design, review, validation, research, incident analysis and workflow improvements—not only implementation.

---

## 2. Canonical documentation roles

Do not duplicate mutable information everywhere. Each living file has one primary responsibility:

| File | Primary responsibility | Update style |
|---|---|---|
| `PROJECT_STATE.md` | **Current truth:** mode, phase, baseline, task, gates, blockers, test/review status, next action | Replace/update current state |
| `NEXT_WORK_ITEM.md` | **Next executable work:** exact scope, order, inputs, forbidden actions, exit condition | Replace when next work changes |
| `PROJECT_MEMORY.md` | **Reusable knowledge:** discoveries, optimizations, tooling lessons, risks and process knowledge | Append/supersede entries; do not erase history |
| `GIT_WORKFLOW.md` | **Standing persistence/documentation protocol** | Change only when the workflow itself improves |
| `CHAT_HANDOFF.md` | **Compact new-chat bootstrap instructions** | Keep short; point to canonical files |
| `SOURCE_IMPORT_STATUS.md` | Temporary exact-source bootstrap status while that prerequisite is open | Update only while source-import prerequisite exists |
| `AI_FILM_STATE_CHECKPOINT_Vn.md` + JSON | **Immutable milestone snapshot** | Create new version; never rewrite old checkpoint history |
| Git commits/diffs | Source/document change history | Do not copy full diffs into state files |

If information appears in more than one file, the table above determines which copy is authoritative and which copy is only a summary/history pointer.

---

## 3. Automatic Documentation Sync Gate

Before a meaningful work increment can be considered complete, the assistant MUST evaluate the following matrix and update every applicable file **without waiting for the user to request it**.

| Trigger discovered during work | Mandatory update |
|---|---|
| Mode, phase, baseline, gate, blocker, status or test/review result changed | `PROJECT_STATE.md` |
| Exact next action/scope/order changed | `NEXT_WORK_ITEM.md` |
| Reusable optimization, lesson, constraint, tooling behavior, failure pattern, risk or clarification discovered | `PROJECT_MEMORY.md` |
| Git/document process itself improved | `GIT_WORKFLOW.md` **and** a `PROJECT_MEMORY.md` entry |
| Source-import persistence state changed | `SOURCE_IMPORT_STATUS.md`, `PROJECT_STATE.md`, `NEXT_WORK_ITEM.md` |
| Implementation progress/remaining scope changed after source is in Git | `docs/IMPLEMENTATION_STATUS.md`, `docs/REMAINING_IMPLEMENTATION.md`, traceability/evidence as applicable |
| Review finding/disposition changed | Correct review/finding artifact **and** `PROJECT_STATE.md` |
| Validation failure changed | Correct `VALIDATION_FAILURE` artifact **and** `PROJECT_STATE.md` |
| A milestone/gate transition occurred | New immutable checkpoint MD + JSON, plus living state/task updates |
| Workflow or tool limitation could cause future duplicate work | `PROJECT_MEMORY.md` even if current task status did not change |

### No-silent-knowledge rule

If ending the current chat would cause a future chat to lose a fact that could prevent duplicated work, a wrong decision, a repeated failure, wasted investigation or a safety regression, the increment is **not documentation-complete** until that fact is persisted.

### Evidence discipline

A documentation update must preserve the distinction between:

- observed/tested fact;
- reviewed/approved decision;
- inference/hypothesis;
- proposed optimization;
- unresolved blocker.

Do not promote a hypothesis into a fact merely because it is written into Markdown.

---

## 4. Documentation Sync Checklist

Run this checklist before every delivery commit and after any milestone:

```text
[ ] Did project state change?           → PROJECT_STATE.md
[ ] Did next work change?               → NEXT_WORK_ITEM.md
[ ] Did we learn something reusable?    → PROJECT_MEMORY.md
[ ] Did workflow improve?               → GIT_WORKFLOW.md + PROJECT_MEMORY.md
[ ] Did implementation status change?   → implementation/remaining/traceability docs
[ ] Did review/validation state change? → relevant artifact + PROJECT_STATE.md
[ ] Is a checkpoint warranted?          → new Vn checkpoint MD/JSON
[ ] Are facts labeled by evidence level?
[ ] Are obsolete memory entries marked SUPERSEDED instead of silently deleted?
[ ] Would a fresh chat know exactly what to do next?
```

A commit is not considered delivery-ready while an applicable box is unresolved.

---

## 5. Commit sequence

1. Verify `main` remote head and current canonical state.
2. Read `PROJECT_STATE.md`, `NEXT_WORK_ITEM.md`, and relevant `PROJECT_MEMORY.md` entries.
3. Work only in the active mode/work-item scope.
4. Run targeted tests/evidence collection appropriate to the mode.
5. At a delivery boundary, run the required full regression/static checks for the current authoring environment.
6. Run the **Documentation Sync Gate** above.
7. Inspect the diff for unrelated changes and accidental contract drift.
8. Run a secret scan. Never commit real credentials, private keys, tokens, private customer material, licensed private assets or production secrets.
9. Commit with a message identifying the work item/coherent increment.
10. Push to GitHub.
11. Re-fetch/verify the remote commit/changed files.
12. If remote verification reveals drift/corruption, treat persistence as incomplete and do not continue on a false baseline.
13. Only then start the next coherent increment.

---

## 6. Commit granularity

Prefer one commit per coherent, tested increment. Examples:

- `feat(p00): complete executable trust integration`
- `feat(p00): add pre-C3 checkpoint evidence selection`
- `test(p00): complete causal lifecycle controller cases`
- `docs(memory): record non-direct transport constraint`
- `docs(state): checkpoint IMPL-P00-001 dev7`

A delivery may contain several commits, but the final delivery state must let a new chat resolve exact mode/task/baseline without consulting conversation history.

---

## 7. Default branch policy

Current project initialization uses `main` directly because the project is a single-user workflow.

Do not force-push or rewrite published history by default.

If future work introduces parallel contributors, protected branches, CI requirements or mandatory pull requests, record that as a workflow change and update this file plus `PROJECT_MEMORY.md`; do not silently switch development models.

---

## 8. State to preserve at delivery boundaries

`PROJECT_STATE.md` should always expose at least:

- repository/branch and persistence status;
- current mode and phase;
- current work item;
- authoritative/reviewed baseline;
- current implementation/delivery baseline;
- author-complete boolean;
- gate status;
- test/static/native/LAB/SITE status;
- open findings/design gaps/validation failures;
- open implementation items/blockers;
- exact next action;
- source/snapshot identity when applicable;
- whether implementation may resume.

Do not embed a self-referential "latest commit SHA" that becomes stale merely because the state file itself is committed. A new chat should query the current remote head directly.

---

## 9. Cross-chat startup

A new chat should use a layered bootstrap to minimize token waste:

1. Read `PROJECT_STATE.md` — current truth.
2. Read `NEXT_WORK_ITEM.md` — exact action.
3. Read relevant active entries in `PROJECT_MEMORY.md` — reusable lessons/optimizations.
4. Verify remote `main` head.
5. Read `GIT_WORKFLOW.md` before making persistent changes.
6. Read conditional files only when referenced by state, e.g. `SOURCE_IMPORT_STATUS.md` while that blocker is open.
7. Read authoritative design/contracts required by the current task.

`CHAT_HANDOFF.md` is a compact prompt/template, not another canonical state database.

---

## 10. Code-review boundary

Implementation commits are not review approval.

`CODE_REVIEW_PASS` can only be produced in `CODE_REVIEW` mode after reviewing the exact committed candidate. If fixes are required, follow the state machine (`PATCH` or the directed implementation path), then commit/push the fixes before re-review.

The review target must be identifiable by repository state and commit history, not an uncommitted workspace.

---

## 11. Native evidence boundary

Author workspace tests, synthetic ports, fixture controllers, static checks and Git persistence are not Windows/WSL/LAB/SITE validation evidence.

Every state/checkpoint must preserve this distinction.

---

## 12. Self-improving documentation rule

Documentation itself is a maintained system.

When work reveals that a file structure, checklist, naming convention, memory schema, bootstrap sequence or persistence rule could be improved:

1. record the reusable lesson in `PROJECT_MEMORY.md`;
2. update the standing workflow/document responsible for that behavior;
3. do not alter reviewed architecture/public contracts unless the mode system authorizes it;
4. commit/push the documentation improvement like any other project increment.

The goal is that **the repository becomes easier—not harder—to resume as the project grows**.
