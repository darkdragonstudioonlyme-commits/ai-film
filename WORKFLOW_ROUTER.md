# AI-FILM-SERVER — Workflow Router

This policy lets a user say **“continue”** without restating the project. Reconciliation identifies work; it does not authorize execution. An executable step has all applicable design, code-review, test-oracle, environment and authority prerequisites satisfied; an open design/test gap is not executable WIP.

## 1. Bootstrap before routing

Fresh-fetch canonical and relevant lane refs. Read `PROJECT_STATE.md`, `NEXT_WORK_ITEM.md`, the owning `LANE_STATE.md` and existing run record. Select additional requirements through `DOCUMENTATION_MAP.md` before using the corresponding capability. Run applicable state, workflow-continuity and learning checks. Verify the selected worktree before writes; preserve WIP.

`PROJECT_STATE.md:STATE_VERSION` selects exactly one JSON checkpoint. Never infer authority from the numerically largest snapshot. An unavailable remote/local check is `NOT_EVALUATED`, not proof of reconciliation. Formal handoff requires the applicable complete scope.

## 2. Workflow status vocabulary

`READY | RUNNING | WIP | HANDED_OFF | WAITING_INPUT | BLOCKED | REVIEWING | FAILED | COMPLETE`

Labels require the immutable evidence contract. The same active run may remain blocked while a separately scoped documentation excursion is processed.

## 3. “Continue” algorithm

Use the first matching rule **for the requested scope** after read-only identity reconciliation:

1. **Untrusted state, conflicting owner, unresolved mutation or STATE_DRIFT** → `RECOVERY_PLAYBOOK.md`; no affected normal execution. Reading and documenting the conflict remain allowed.
2. **Failed lifecycle guard, overdue measurement, unresolved ineffective learning, semantic evidence mismatch, or mandatory workflow-health intervention** → `WORKFLOW_REVIEW`; preserve the original run/cursor. An active run cannot bypass this guard.
3. **Explicit user request for another authorized scope** → select its workflow and record an excursion with `PARENT_RUN_ID`, immutable base, scope and `RETURN_TO`. A blocked product run is not replaced. Safety guards still apply to the requested scope; no implicit host changes or new spending.
4. **Affected workflow is BLOCKED / WAITING_INPUT** → apply the block protocol to that exact scope. An explicitly selected, authorized corrective work item may proceed while its parent product gate stays blocked. An unchanged external block has no new work: return it without regeneration, repeated polling or a release that only restates it.
5. **INTENT without COMPLETE, or output ahead of canonical state** → `CONTINUITY_RECOVERY`: inspect exact outputs and adopt/reuse before retry. Uncertain non-idempotent effects stay blocked.
6. **Existing run or documented WIP is executable** → continue the same RUN_ID at its verified cursor. Re-evaluate guards before each material side effect and before advancing a completed step.
7. **Unreviewed immutable handoff exists** → REVIEW that exact identity. A FAIL routes findings to the producer; design conflicts use DESIGN_GAP, not an acceptance rewrite.
8. **Residual implementation scope exists** → the next reviewed roadmap increment. Formal CODE_REVIEW requires `AUTHOR_COMPLETE` and `CODE_REVIEW_HANDOFF_READY`.
9. **CODE_REVIEW_PASS with no active/blocking validation cursor** → enter authorized VALIDATION via the roadmap. A code verdict never overrides native prerequisites or grants HOST_READY.
10. **Test oracle/business behavior must change** → TEST-DESIGN / TEST-REVIEW. Model comparison → MODEL-EVAL with exact environment and evaluation identity.
11. **No rule resolves the request** → explicit routing/state blocker; do not guess or silently restart.

Read-profile selection, the precedence above and excursion handling are procedural policy. Structural CI checks do not prove that a conversational agent followed every routing decision.

## 4. Block protocol

```yaml
BLOCK_ID:
WORKFLOW_ID:
OWNER_LANE:
REASON:
EVIDENCE:
USER_ACTION_REQUIRED: true|false
RETURN_TO:
STATUS: OPEN|RESOLVED
```

If `USER_ACTION_REQUIRED=false`, attempt the safe in-scope resolution. If true, request only the external action unavailable to the assistant. Resolution requires new evidence for the blocked predicate, not a user message alone. Expiring authority is generated only after durable prerequisites are verified. Do not reinterpret an unchanged blocker as a new failure or silently lower its gate.

## 5. Findings and design-gap routes

Candidate defects become immutable findings bound to exact target identity. The producer marks a correction `FIX_PENDING_REVIEW`; a subsequent reviewer verifies closure. Reusable lessons use `SELF_LEARNING.md`, not memory-based contract overrides.

```text
reviewed-contract conflict → preserve evidence → DESIGN_GAP
→ DESIGN → DESIGN_REVIEW → approved return to IMPLEMENT
```

## 6. Validation-failure route

```text
VALIDATION_FAILURE → immutable evidence → MASTER routing
→ IMPLEMENT/PATCH when approved → CODE_REVIEW → VALIDATION
```

Review/validation never patch production source in place.

## 7. Workflow instance contract

`NEXT_WORK_ITEM.md` or the explicit excursion run binds:

```yaml
RUN_ID:
WORKFLOW_ID:
LANE:
STATUS:
INPUT_IDENTITY:
GOAL:
STEPS:
CURRENT_STEP:
SUCCESS_OUTPUT:
ON_SUCCESS:
ON_FAIL:
ON_BLOCK:
EXIT_CONDITION:
```

Excursions additionally bind `PARENT_RUN_ID`, `RETURN_TO`, and the preserved product gates. Completion returns to reconciliation, not automatic execution of a formerly blocked action.

## 8. Workflow meta-review and interruption

Preserve WIP → identify repeated assumptions → smallest systemic correction → role-separated review → canonical activation → future effectiveness measurement → original return point. Use `WORKFLOW_HEALTH.md` to distinguish safety work from unmeasured process churn.

Timeout, model switch or chat boundary never creates a replacement logical run. `WORKFLOW_CONTINUITY.md` owns takeover, write-ahead journaling, conflict handling and output reuse.

## Current work and accepted baseline

`current_work` in the selected JSON owns the immediate work-item identity, mode, status, parent run and readiness. Its work item equals `PROJECT_STATE.md:CURRENT_TASK` and `NEXT_WORK_ITEM.md:WORK_ITEM`; its mode/status equal NEXT_WORK_ITEM. The parent's blocked V02 cursor is preserved and is not the corrective task's readiness. Root author/code-review flags describe only `READINESS_SCOPE: ACCEPTED_CODE_CANDIDATE`; they never authorize a successor candidate. Superseded work items must not remain READY in another current-state object. `tools/check_current_work.py` enforces this routing projection, not the semantic validity of every product gate.

## Actor routing and automatic delivery

Assign a single task actor after resolving scope and gates. Default responsibilities
are in `docs/DUAL_AI_COLLABORATION.md`; actual authorship determines the non-author
reviewer. The task envelope does not override current_work or product authority.
At handoff, use verified local dispatch capability when active; otherwise leave the
exact task BLOCKED_CAPABILITY. No recursive model-to-model task generation, forced
permission fallback or autonomous continuation outside the available runtime.
Consume a matching pending result before creating another paid call or task revision.
## Routing identity and capability are separate

Resolve the selected current_work for both actors, including assignee/author/role,
profile, blockers, context and return cursor. A capsule must match those fields before
work; NEXT_WORK_ITEM is a checked projection, not an independent competing task.
A tool-denied operation stays blocked; changing model does not change the permission.

Connection history is not profile activation. Use the capability matrix in
`docs/DUAL_AI_AUTOMATIC_HANDOFF.md`: a known installation is not reinstalled because
an older snapshot says absent, and a successful setup smoke does not authorize
implementation. Both actors use the deterministic decision model in
`tools/check_shared_workflow.py`; it is a tested reference, not a deployed scheduler.
The user need not specify actor/mode/next action. Tiếp tục starts a bounded turn;
there is no automatic activity without an invocation or a separately deployed runtime.
