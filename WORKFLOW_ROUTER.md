# AI-FILM-SERVER — Workflow Router

This is the deterministic routing policy for a fresh chat. It exists so a user can say **“continue”** without restating the entire project.

## 1. Bootstrap before routing

```text
fetch origin/main + relevant lane refs
→ read PROJECT_STATE + owning LANE_STATE
→ if ACTIVE_RUN_ID exists, read its workflow-runs ledger first
→ run workflow-continuity + runtime-state reconciliation
→ run learning lifecycle reconciliation
→ read NEXT_WORK_ITEM
→ verify local selected worktree identity/status if used
→ evaluate WORKFLOW_HEALTH triggers
→ route
```

Run `python3 tools/check_learning_lifecycle.py` during bootstrap. Lifecycle drift or unresolved learning debt is routing evidence; an old learning record or stale memory note cannot override the lifecycle register.

Never route from cached `origin/lane/*` refs without a fresh fetch.

## 2. Workflow status vocabulary

`READY | RUNNING | WIP | HANDED_OFF | WAITING_INPUT | BLOCKED | REVIEWING | FAILED | COMPLETE`

A workflow output is trusted only through its declared immutable output contract, never because another lane says “PASS”.

## 3. “Continue” algorithm

Use the first matching rule:

1. **Active RUN_ID is not COMPLETE** → resume/reconcile that same run via `WORKFLOW_CONTINUITY.md`; never create a duplicate run for the same workflow/base.
2. **INTENT exists without COMPLETE or producer output is ahead of canonical state** → classify `CONTINUITY_RECOVERY`; verify/adopt exact output before rerunning any step.
3. **STATE_DRIFT or recovery condition exists** → use `RECOVERY_PLAYBOOK.md` first; do not route normal work on untrusted state.
4. **Learning lifecycle checker fails, unresolved ineffective learning exists, or measurement debt is due** → route `WORKFLOW_REVIEW`/DOC-DESIGN before more affected work; preserve the current run return point.
5. **Workflow health is META_REVIEW_REQUIRED** → route `WORKFLOW_REVIEW` before more brute-force patches.
6. **Uncommitted WIP exists and state names it** → resume that WIP in its owning lane; do not reset to the last package.
7. **A candidate is HANDED_OFF and REVIEW has not reviewed that exact identity** → REVIEW exact candidate.
8. **Latest REVIEW is FAIL with open findings** → route findings to their producer workflow; IMPLEMENT fixes source findings, DESIGN handles genuine design gaps.
9. **Latest delta REVIEW passes but umbrella completeness blocker remains** → continue next roadmap implementation node.
10. **AUTHOR_COMPLETE=true and CODE_REVIEW_HANDOFF_READY=true** → formal CODE_REVIEW exact final candidate.
11. **CODE_REVIEW_PASS=true** → follow `PROJECT_ROADMAP.md` to VALIDATION; do not stay in implementation by habit.
12. **A workflow is BLOCKED** → follow its `RETURN_TO` / `USER_ACTION_REQUIRED` contract below.
13. **Test oracle/business expectation is proposed to change** → route TEST-DESIGN/TEST-REVIEW using `TEST_STRATEGY.md`; implementation code is not test authority.
14. **Model comparison/benchmark requested** → verify `SERVER_ENVIRONMENT.md`/`MODEL_EVALUATION.md`; block claims whose environment facts are unavailable.
15. If none match, state is inconsistent → create a documentation/state blocker; do not guess.

## 4. Block protocol

A block record must contain:

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

If `USER_ACTION_REQUIRED=false`, the assistant must attempt the safe in-scope resolution and continue. Do not ask the user to solve implementation work.

If `USER_ACTION_REQUIRED=true`, request only the minimum external action that cannot be performed by available tools. Persist the block before ending the turn.

## 5. Review finding/comment protocol

Candidate-specific defects become immutable findings bound to target SHA/package identity. They route back to the producing lane as `FIX_PENDING_REVIEW` and close only when REVIEW verifies a new immutable candidate.

Reusable observations go through `SELF_LEARNING.md`: immutable learning evidence plus lifecycle register update. A memory note alone does not close learning lifecycle.

## 6. Design-gap route

If correct implementation requires changing reviewed FD/D00/public behavior:

```text
IMPLEMENT detects DESIGN_GAP
→ persist exact evidence
→ stop affected implementation scope
→ DESIGN
→ DESIGN_REVIEW
→ only approved design returns to IMPLEMENT
```

Never “fix” a reviewed-contract conflict by silently changing code acceptance or documentation wording.

## 7. Validation-failure route

```text
VALIDATION_FAILURE
→ persist failure/evidence
→ MASTER/routing decision
→ IMPLEMENT or PATCH as directed
→ CODE_REVIEW if code changed
→ VALIDATION again
```

Review and validation do not patch production source in-place.

## 8. Workflow instance contract

Every active work item should expose in `NEXT_WORK_ITEM.md`:

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

This contract is what enables accurate cross-chat continuation.

## 9. Workflow meta-review route

When `WORKFLOW_HEALTH.md` triggers `META_REVIEW_REQUIRED`:

```text
preserve WIP/evidence
→ stop affected loop
→ create health review
→ reconcile learning lifecycle state
→ classify root cause
→ update workflow/test/policy/docs/tooling if systemic
→ independent review of correction
→ canonical activation
→ effectiveness measurement trigger
→ RETURN_TO original workflow
```

Repeated failure is information about the workflow itself; do not merely increase patch count.

## 10. Interruption invariant

Chat timeout, model/tool disconnect or execution-window exhaustion never starts a replacement workflow. Persist/recover the same `RUN_ID`; see `WORKFLOW_CONTINUITY.md`.
