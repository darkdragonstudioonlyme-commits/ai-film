# AI-FILM-SERVER — Workflow Health, Deadlock and Meta-Review

## Purpose

A workflow is itself an engineered system. Repeated mistakes, circular patching or low-information progress require a workflow/design review instead of more brute-force execution.

## Health states

`HEALTHY | DEGRADED | DEADLOCK_RISK | META_REVIEW_REQUIRED | RECOVERING`

## Automatic meta-review triggers

Any one of these requires at least a health assessment; repeated/severe cases force `META_REVIEW_REQUIRED`:

- same finding class reappears in 2 reviewed candidates;
- 3 consecutive patch/review cycles do not reduce blocker/high findings;
- tests are repeatedly edited to follow code without upstream business change;
- state/version drift recurs after reconciliation;
- a workflow performs substantial work but cannot name a new immutable output/evidence improvement;
- more than 2 failed attempts use the same approach without new evidence;
- frequent tool/parsing mistakes create rework or corrupt state interpretation;
- workflow waits on another lane whose input/output contract is ambiguous;
- WIP cannot be safely resumed by a fresh chat;
- documentation/policy grows while active guidance becomes harder to identify;
- repeated flaky/timeout/OOM behavior is treated with retries instead of root-cause isolation;
- a completed expensive/material step is repeated after interruption although its exact output identity was recoverable;
- two active RUN_IDs exist for the same workflow/base, or a new chat restarts work instead of adopting the active run;
- a reviewed reusable learning remains `PENDING_ACTIVATION` while the affected workflow continues and the same friction/incident class is still possible;
- documentation-governance promotion is blocked by branch/worktree identity that standing policy hard-coded instead of deriving from canonical governance state.

## Meta-review procedure

```text
STOP affected workflow at safe boundary
→ preserve WIP/evidence
→ classify failure: REQUIREMENT | DESIGN | TEST | PROCESS | TOOL | ENVIRONMENT | DATA | OWNERSHIP
→ identify repeated assumptions and wasted loops
→ inspect whether MD architecture/policy/router/test strategy caused or failed to prevent it
→ inspect whether a known learning exists but is not yet active
→ propose smallest systemic correction
→ independent review of workflow correction
→ activate the correction in canonical policy/tooling
→ resume original work from explicit RETURN_TO
```

## Health record

```yaml
HEALTH_REVIEW_ID:
TRIGGER:
WORKFLOW:
STATE_BEFORE:
SYMPTOMS:
ROOT_CAUSE_CLASS:
EVIDENCE:
WASTED_WORK_PATTERN:
SYSTEMIC_CHANGE:
DOCS_OR_POLICY_CHANGED:
TESTS_OR_CHECKERS_ADDED:
LEARNING_ACTIVATION_STATUS:
RETURN_TO:
RESULT:
```

## Efficiency metrics

Track trends, not vanity counts:

- review cycles per accepted increment;
- blocker/high findings opened vs closed;
- repeated finding rate;
- WIP recovery success from cold start;
- interruption resume-without-rework rate;
- duplicate logical-run count;
- repeated completed-step count after timeout;
- state-drift incidents;
- test flake/retry rate;
- documentation checker/audit failures;
- time/steps spent on tooling errors versus project work;
- percentage of reusable discoveries promoted into policy/checkers when warranted;
- **learning activation lag**: reviewed reusable learning → canonical activation;
- **learned-but-not-active backlog**: promoted learnings still pending activation/block resolution;
- **source-visibility friction**: review/operator work repeated or blocked because exact source cannot be conveniently inspected remotely.

Metrics diagnose workflow quality; they never lower acceptance.

## Deadlock breaker

When two workflows wait on each other, neither may invent the other's evidence. Create one owner and one immutable contract for the missing dependency. If ownership cannot be resolved from current policy, route to project governance/design review rather than bouncing comments indefinitely.

## Review of the documentation system itself

Material workflow/process failures must ask:

> Would a better `WORKFLOW_ROUTER`, `WORKFLOW_CONTINUITY`, `TEST_STRATEGY`, `SELF_LEARNING`, `POLICY_REGISTRY`, `DOCUMENTATION_MAP`, checker, environment contract or recovery playbook have prevented or shortened this failure?

If yes, update the documentation system through DOC-DESIGN → DOC-REVIEW → DOC-AUDIT before declaring the learning complete. A PASS review without canonical activation is still an activation backlog item, not proof that the workflow changed.

## Durable health records

Write immutable `workflow-health/HEALTH_REVIEW-<workflow>-<nnn>.md` records. Only health state that affects immediate routing is summarized in `PROJECT_STATE.md`. Detailed metrics/history stay out of bootstrap state.
