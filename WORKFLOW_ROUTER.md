# AI-FILM-SERVER — Workflow Router

## Bootstrap

Fresh-fetch `main` and relevant lane refs, run runtime-state reconciliation when available, then read state → next-work → this router → selected lane state. Never route from cached refs or conversation memory alone.

## Continue algorithm

Use the first matching rule:

1. active documentation/design governance handoff → finish its independent review/audit before unrelated source work;
2. documented mutable WIP → resume its owning workflow, preserving WIP;
3. immutable candidate handed off and not reviewed at that identity → consumer REVIEW;
4. latest review FAIL/open findings → route findings to producer; design conflict goes to DESIGN, not implementation patching;
5. repeated failure/deadlock/self-learning trigger → `WORKFLOW_RETROSPECTIVE` before another blind retry;
6. delta review PASS but umbrella blocker remains → next roadmap node;
7. author-complete exact candidate → formal CODE_REVIEW;
8. CODE_REVIEW_PASS → VALIDATION;
9. state/lane/environment identity mismatch → `STATE_DRIFT` blocker and reconcile;
10. otherwise state is inconsistent → documentation/state blocker, never guess.

## Test-failure router

Before changing code or tests, classify a failing test as one of:

```text
APPROVED_BEHAVIOR_CHANGE
TEST_DEFECT
HARNESS_DEFECT
ENVIRONMENT_DEFECT
IMPLEMENTATION_DEFECT
DESIGN_GAP
```

The classification determines the owner. Never change expected behavior merely because current code differs. `TEST_STRATEGY.md` is authoritative for this route.

## Retrospective/deadlock route

Triggers are defined in `SELF_LEARNING_SYSTEM.md`. When triggered:

```text
preserve WIP
→ stop same-strategy retry
→ retrospective/root-cause classification
→ memory/policy/tool improvement
→ independent review if governance meaning changed
→ verify improvement
→ RETURN_TO original workflow
```

## Block contract

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

If user action is false, attempt safe in-scope resolution rather than asking the user to do project work.

## Review / design-gap / validation routes

Review findings bind exact candidate identities and close only on independent re-review. Genuine reviewed-behavior conflicts route DESIGN_GAP → DESIGN → DESIGN_REVIEW. Validation failures persist evidence and route back through implementation/patch and code review when code changes.

## Workflow instance contract

Every active workflow exposes:

```yaml
WORKFLOW_ID:
LANE:
STATUS:
INPUT_IDENTITY:
GOAL:
STEPS:
TEST_CONTRACT:
SUCCESS_OUTPUT:
ON_SUCCESS:
ON_FAIL:
ON_BLOCK:
EXIT_CONDITION:
RETURN_TO:
```
