# AI-FILM-SERVER — Workflow Router

This is the deterministic routing policy for a fresh chat. It exists so a user can say **“continue”** without restating the entire project.

## 1. Bootstrap before routing

```text
fetch origin/main + relevant lane refs
→ read PROJECT_STATE
→ read NEXT_WORK_ITEM
→ verify local selected worktree identity/status if used
→ read selected lane LANE_STATE
→ route
```

Never route from cached `origin/lane/*` refs without a fresh fetch.

## 2. Workflow status vocabulary

`READY | RUNNING | WIP | HANDED_OFF | WAITING_INPUT | BLOCKED | REVIEWING | FAILED | COMPLETE`

A workflow output is trusted only through its declared immutable output contract, never because another lane says “PASS”.

## 3. “Continue” algorithm

Use the first matching rule:

1. **Uncommitted WIP exists and state names it** → resume that WIP in its owning lane; do not reset to the last package.
2. **A candidate is HANDED_OFF and REVIEW has not reviewed that exact identity** → REVIEW exact candidate.
3. **Latest REVIEW is FAIL with open findings** → route findings to their producer workflow; IMPLEMENT fixes source findings, DESIGN handles genuine design gaps.
4. **Latest delta REVIEW passes but umbrella completeness blocker remains** → continue next roadmap implementation node.
5. **AUTHOR_COMPLETE=true and CODE_REVIEW_HANDOFF_READY=true** → formal CODE_REVIEW exact final candidate.
6. **CODE_REVIEW_PASS=true** → follow `PROJECT_ROADMAP.md` to VALIDATION; do not stay in implementation by habit.
7. **A workflow is BLOCKED** → follow its `RETURN_TO` / `USER_ACTION_REQUIRED` contract below.
8. If none match, state is inconsistent → create a documentation/state blocker; do not guess.

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

Informational comments that produce reusable knowledge go to `PROJECT_MEMORY.md`; they do not become findings unless they affect correctness/gate acceptance.

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
WORKFLOW_ID:
LANE:
STATUS:
INPUT_IDENTITY:
GOAL:
STEPS:
SUCCESS_OUTPUT:
ON_SUCCESS:
ON_FAIL:
ON_BLOCK:
EXIT_CONDITION:
```

This contract is what enables accurate cross-chat continuation.
