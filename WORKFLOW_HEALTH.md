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
- `tools/check_learning_lifecycle.py` reports lifecycle/register/project-state drift;
- a reusable learning remains `PENDING_ACTIVATION`/`BLOCKED` while the affected workflow continues;
- an `INEFFECTIVE` learning has no active successor/meta-review path;
- `OVERDUE_EFFECTIVENESS_MEASUREMENT > 0` after a structured measurement gate is reached;
- an `EFFECTIVE` learning has only path-existence/structural evidence and no independently reviewable proof of its metric scope, sample requirement and predicate;
- the lifecycle register silently changes or weakens the success metric owned by an immutable learning record;
- a DOC-REVIEW/DOC-AUDIT artifact declares PASS while the verdict-bearing commit has a required governance CI failure;
- a canonical `TEST_REVIEW` references a `TEST_CHANGE`/`TEST_GAP` that cannot be resolved from the canonical tree or an exact immutable commit locator;
- documentation-governance promotion is blocked by branch/worktree identity hard-coded in standing policy instead of canonical governance state.

A merely pending measurement is visible planning state, not a blocker. Learning debt is derived from `learning/LEARNING_STATE.json`; prose or an old learning record cannot override the register.

## Meta-review procedure

```text
STOP affected workflow at safe boundary
→ preserve WIP/evidence
→ classify failure: REQUIREMENT | DESIGN | TEST | PROCESS | TOOL | ENVIRONMENT | DATA | OWNERSHIP
→ identify repeated assumptions and wasted loops
→ inspect whether MD architecture/policy/router/test strategy caused or failed to prevent it
→ run learning lifecycle reconciliation
→ inspect pending/ineffective/overdue-measurement learning
→ propose smallest systemic correction
→ independent review of workflow correction
→ activate the correction in canonical policy/tooling
→ measure successor effectiveness
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
LEARNING_IDS:
LEARNING_ACTIVATION_STATUS:
LEARNING_EFFECTIVENESS_STATUS:
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
- learning activation lag;
- learned-but-not-active backlog;
- unresolved ineffective learning count;
- pending effectiveness measurement count;
- **overdue effectiveness measurement count**;
- lifecycle-state drift count;
- source-visibility friction;
- semantic-effectiveness verification rate (`verified metric receipts / EFFECTIVE claims`);
- unsupported/self-reported PASS count;
- verdict-branch CI contradiction count;
- canonical test-governance provenance closure rate.

The learning lifecycle counts are derived/reconciled through `learning/LEARNING_STATE.json`; semantic effectiveness is a separate proof obligation and must not be inferred from those counts. Metrics diagnose workflow quality; they never lower acceptance.

Periodically persist an immutable workflow-health measurement snapshot when enough comparable executions exist. A snapshot must state its population/time window and source artifacts; without a baseline and comparable later measurement, a change is not yet proven to be an improvement.

## Deadlock breaker

When two workflows wait on each other, neither may invent the other's evidence. Create one owner and one immutable contract for the missing dependency. If ownership cannot be resolved from current policy, route to project governance/design review rather than bouncing comments indefinitely.

## Review of the documentation system itself

Material workflow/process failures must ask:

> Would a better `WORKFLOW_ROUTER`, `WORKFLOW_CONTINUITY`, `TEST_STRATEGY`, `SELF_LEARNING`, `POLICY_REGISTRY`, `DOCUMENTATION_MAP`, checker, environment contract or recovery playbook have prevented or shortened this failure?

If yes, update the documentation system through DOC-DESIGN → DOC-REVIEW → DOC-AUDIT before declaring the learning complete. Automatic detection may produce the candidate correction, but it cannot independently review or promote that correction.

## Durable health records

Write immutable `workflow-health/HEALTH_REVIEW-<workflow>-<nnn>.md` records. Only health state that affects immediate routing is summarized in `PROJECT_STATE.md`. Detailed metrics/history stay out of bootstrap state.

## Session effectiveness and no-change blocks

Git commits, branches, PASS labels and state versions are not sessions, accepted product increments or proof of efficiency. Separate product progress, risk reduction, tooling repair and editorial activity. A blocked external prerequisite may explain elapsed time; do not count that wait as author rework or hide it inside active execution time.

At a material run boundary record a compact receipt in `workflow-health/metrics/` (or reference the owning run):

```yaml
METRIC_VERSION:
POPULATION_AND_WINDOW:
RUN_IDS_AND_EXACT_BASES:
OBSERVED_OUTPUT_IDENTITIES:
NEW_EVIDENCE_OR_RISK_REDUCTION:
OPENED_CLOSED_AND_REOPENED_FINDINGS:
REVIEW_CYCLES:
REUSED_OUTPUTS_AND_JUSTIFIED_RERUNS:
ACTIVE_WORK_MEASUREMENT: measured_value|NOT_COLLECTED
EXTERNAL_WAIT_MEASUREMENT: measured_value|NOT_COLLECTED
READ_PROFILE_AND_BYTES: measured_value|NOT_COLLECTED
KNOWN_MISSING_DATA:
NEXT_COMPARABLE_MEASUREMENT:
```

Use the same denominators and classification in before/after comparisons. Include failures, abandoned attempts and non-events; do not report success-only samples as a success rate. When no comparable later sample exists, report `IMPROVEMENT_NOT_PROVEN`. A corpus byte reduction proves only less text in that measured scope, not token cost, latency or higher quality.

An unchanged external blocker is a valid no-op result with the same return point. Record its changed evidence only when there is some; avoid a new design/review/audit loop just to rediscover the same block. An explicit user-requested review remains meaningful work when it has separate evidence and a bounded objective.

## Boundary receipts and repeated-gap intervention

At each completed handoff, failed review, interruption takeover or blocked-to-corrective transition, persist one compact receipt under `workflow-health/metrics/` or the owning continuation. Bind a stable boundary ID, parent run, current work item, exact input/output commit or local-WIP digest, classification (`PRODUCT_PROGRESS`, `RISK_REDUCTION`, `TOOLING_REPAIR`, `EDITORIAL`, `BLOCKED_NO_CHANGE`), outcome, new/escaped findings, reuse/rerun decision, missing measurements and next comparable boundary. One boundary is not one chat/session. Reuse its ID when retrying publication; do not count review/audit commits as extra successful executions.

After the second escaped finding in the same design/producer family, perform one consolidated end-to-end constructibility review before another implementation attempt. It covers all currently known dependency classes, including temporal identities, hash dependencies, permission/guard ordering and producer/consumer schema. Classify the result as risk reduction until later comparable runs prove lower recurrence. An additional PASS document alone is not the exit condition.

Missing historical receipts remain `EVENT_NOT_INSTRUMENTED` or `UNKNOWN`, not synthetic successes. `tools/check_current_work.py` checks the current audit receipt's declared scope/denominator and current routing identity. It cannot establish unobserved session counts or future improvement. Unchanged 0/3 resume counters after observed continuation opportunities trigger an instrumentation assessment; they are not proof of no interruptions and do not silently change the immutable learning metric.

## Cross-actor effectiveness and dispatch health

Boundary receipts add task/attempt, actor/model/tool, supplied knowledge identity,
lesson application evidence, delivery/retry outcomes, escaped findings and user
context interventions. Provider-reported cost remains an estimate; unknown usage
stays UNKNOWN. Neither a successful dispatch nor a second model's agreement is
product progress, interrupted-resume success or improved learning effectiveness.

Missing or stale context, duplicate workers, unsafe permission fallback, self-review,
or repeated unchanged correction rounds require intervention. After two failed
premises, consolidate the causal family rather than automate an infinite dialogue.
Any future daemon/API controller must supply actual deployment evidence; this chat
cannot promise continued work after its turn solely because a queue exists.
## Measure useful learning without paperwork growth

For both actors record only material boundaries and changed evidence. The same receipt
can carry handoff, lesson application, escaped-findings and pruning information; do
not add one state version, release or lesson per model reply. Track accepted scoped
outputs and validated risk reduction separately from document/commit/test counts.

Evaluate shared learning on the first eligible cross-actor opportunities with the
same frozen metric, scope and denominator. Include blocked attempts, failures, missing
usage/time and exclusions. Report recurrence, valid findings, attributable rework,
reused outputs and user context interventions. Time saved, quality improved or one
model being better requires a comparable baseline; delivery success is insufficient.

A known-invalid lesson in operative context, actor disagreement over scope/oracle,
reopened design after repeated PASS, stale capability state or active guidance growing
without a new invariant is a health finding. Stop the affected path and consolidate
its correction. Historical 0/3 continuity data stays unchanged until genuine qualified
receipts exist. No effectiveness claim is added by this pre-Claude correction.
