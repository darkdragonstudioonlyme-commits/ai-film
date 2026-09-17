# AI-FILM-SERVER — Self-Learning and Guarded Continuous Improvement

## Objective

Every meaningful failure or improvement should make future work cheaper, safer or more accurate. Logging history without changing future behavior is not sufficient learning.

The system may automatically **detect, reconcile, measure and route** learning debt. It must never automatically promote its own unreviewed governance correction.

## Learning loop

```text
OBSERVE
→ EXPLAIN
→ GENERALIZE
→ SCORE REUSABILITY
→ PERSIST IMMUTABLE EVIDENCE
→ PROPOSE POLICY/TOOL/CHECKER CHANGE WHEN WARRANTED
→ INDEPENDENTLY REVIEW
→ ACTIVATE THE REVIEWED CHANGE
→ APPLY
→ MEASURE WHETHER RECURRENCE/FRICTION DECREASES
→ RETIRE/SUPERSEDE OR REOPEN META-REVIEW
```

A reviewed learning is **not operational learning** until its successor policy/tool/checker is canonically active, or activation is explicitly blocked with owner/return path. An active learning is **not proven effective** until its success metric has evidence. Evidence-file existence is necessary but not sufficient: the evidence must semantically prove the declared metric for the declared scope and sample requirement. A checker that only proves that an evidence path exists proves structural lifecycle integrity, not effectiveness.

## Two-layer ownership model

R9 separates immutable provenance from mutable lifecycle state.

### Immutable learning evidence

`learning/LEARNING-<scope>-<nnn>.md` owns:

```yaml
LEARNING_ID:
DISCOVERED_IN:
CLASS:
OBSERVATION:
ROOT_CAUSE:
EVIDENCE:
REUSABLE_RULE:
SCORE:
CURRENT_ACTION:
POLICY_OR_TOOL_PROMOTION:
SUCCESS_METRIC:
STATUS: ACTIVE|SUPERSEDED|RETIRED
```

These files explain **what was learned and why**. Historical activation/review fields in pre-R9 records are snapshots only and no longer own current lifecycle truth.

### Canonical lifecycle register

`learning/LEARNING_STATE.json` is the sole machine-readable owner of current lifecycle state. Every active reusable learning has exactly one register entry with:

- immutable record path and score;
- activation target;
- review status + immutable review record;
- activation status, activated release, **activation evidence**, and blocker;
- effectiveness status + evidence;
- human-readable measurement trigger plus a **structured measurement gate**;
- immutable success-metric binding: if the register repeats `success_metric`, it must match the immutable learning record; a changed metric requires a successor/new reviewed learning, not silent register editing;
- successor when ineffective/superseded.

`PROJECT_STATE` carries only **derived aggregates** such as pending activation, unresolved ineffective learning, pending measurement and overdue measurement. Those numbers must match the register; they are never maintained as an independent authority.

## Evidence-gated lifecycle transactions

The register is mutable state, but it is **not self-authorizing mutable state**. Each transition has an evidence gate:

- **DISCOVERED / REVIEW_PENDING** — may be created from immutable learning/health evidence; grants no active policy authority.
- **REVIEWED / PASS** — requires an immutable independent review record bound to the exact proposed correction.
- **ACTIVE** — requires canonical activation evidence for the declared target release/policy and no activation blocker.
- **EFFECTIVE** — requires immutable effectiveness/health evidence that evaluates the declared success metric.
- **INEFFECTIVE** — requires immutable evidence and an explicit successor or meta-review route.
- **SUPERSEDED / RETIRED** — requires successor/removal evidence when applicable.

A data-only lifecycle transition that follows these existing rules does not itself require a new documentation-system release. Changing the lifecycle **schema, transition semantics, checker rules or policy meaning** is a DOCSYS design change and must go through DOC-DESIGN → DOC-REVIEW → DOC-AUDIT.

Automation may prepare a candidate register transition and its evidence links, but the checker must be able to independently prove the transition from immutable evidence. Automation cannot manufacture the review/audit evidence that authorizes its own policy change.

## Discovery classes

`DEFECT | TOOLING | TEST | PROCESS | SECURITY | RECOVERY | PERFORMANCE | ENVIRONMENT | ARCHITECTURE | BUSINESS_CLARIFICATION`.

## Learning score

Score 0–2 for each: recurrence likelihood, impact, generality, safety relevance, cost avoided.

- 0–3: candidate-specific note/finding only;
- 4–6: memory entry;
- 7–10: durable learning + proposed policy/checker/workflow change, independently reviewed and activated.

Critical security/correctness lessons may be promoted regardless of score.

## Lifecycle state machine

```text
DISCOVERED
→ REVIEW_PENDING
→ REVIEWED
→ PENDING_ACTIVATION | BLOCKED
→ ACTIVE_UNMEASURED
→ EFFECTIVE | INEFFECTIVE
→ SUPERSEDED | RETIRED
```

Promotion-ready documentation trees may use `PASS_ON_FINAL_REVIEW` / `ACTIVE_ON_PROMOTION` when exact final review/audit record paths are predeclared. These are conditional states, not permission to skip review/audit.

An `ACTIVE` learning must carry immutable activation evidence. `ACTIVE_ON_PROMOTION` must predeclare both final review and final audit evidence paths.

## Proof and measurement of learning

A promoted learning defines a future detector or behavior change: checker, router rule, test, schema, policy, workflow or recovery step. It is counted as **applied** only after canonical activation. Later workflow-health review evaluates the success metric.

### Semantic effectiveness proof

An `EFFECTIVE` transition must bind the metric to what was actually observed. Use an immutable measurement receipt (normally `learning/measurements/MEASUREMENT-<learning-id>-<nnn>.md`) or an equivalent independently reviewed health record containing at least:

```yaml
LEARNING_ID:
METRIC_ID:
METRIC_VERSION:
SCOPE:
SAMPLE_REQUIREMENT:
OBSERVATIONS:
EXPECTED_PREDICATE:
RESULT: PASS|FAIL
EVIDENCE_IDENTITIES:
MEASUREMENT_COMMIT:
REVIEW_ID:
```

The receipt must make sample cardinality and scope explicit. A metric that requires three interrupted workflows is not satisfied by one recovered run plus a later state number. An unrelated existing file, a state-version increment, or a checker PASS that does not evaluate the metric predicate cannot prove effectiveness.

If current tooling cannot machine-express an event-count or semantic predicate, the measurement remains human-reviewed evidence debt until independent review proves the receipt. Do not weaken the metric to fit the current checker.

For machine-evaluable time/state progression, `measurement_gate` uses structured forms. R9 supports:

```json
{"kind":"COMPLETE"}
{"kind":"STATE_VERSION_AT_LEAST","value":36}
```

A pending measurement is informative but is not automatically a blocker. It becomes **overdue measurement debt** only when its structured gate is satisfied and effectiveness evidence is still absent. Event-based incidents such as lifecycle-check failure independently trigger meta-review immediately.

Tracked failure modes:

- **LEARNED_BUT_NOT_ACTIVE** — reusable correction is reviewed/proposed but not canonically active;
- **ACTIVE_BUT_NOT_EFFECTIVE** — correction is active but recurrence/friction did not improve;
- **LIFECYCLE_STATE_DRIFT** — immutable record, lifecycle register and project aggregate disagree;
- **MEASUREMENT_DEBT** — activated correction has reached its structured measurement gate without effectiveness evidence.
- **SEMANTIC_EVIDENCE_MISMATCH** — evidence paths exist or structural checks pass, but the evidence does not prove the immutable success metric, scope or sample requirement.
- **METRIC_DEFINITION_DRIFT** — the lifecycle register and immutable learning record disagree on the success metric or silently change its meaning.

`ACTIVE_BUT_NOT_EFFECTIVE` must name a successor or explicit meta-review return path; it is never silently counted as success.

## Guarded automation

Every fresh session/bootstrap runs `tools/check_learning_lifecycle.py` before final routing. The checker may fail/route work when it finds lifecycle drift or **overdue** learning debt.

Automation MAY:

- discover schema/lifecycle inconsistencies;
- derive activation, ineffective, pending-measurement and overdue-measurement counts;
- create candidate health/learning evidence and semantic measurement receipts;
- trigger `WORKFLOW_HEALTH` meta-review;
- generate a candidate documentation-system correction.

Automation MUST NOT:

- mark its own correction independently reviewed;
- write PASS review/audit verdicts into its own design step;
- promote a documentation-system release without the declared review/audit sequence;
- delete or rewrite evidence merely to remove a failed metric;
- mark a learning EFFECTIVE merely because referenced files exist or a structural lifecycle checker passes.

## Activation and effectiveness debt

`WORKFLOW_HEALTH.md` treats any of the following as process debt:

- pending/blocked activation while affected work continues;
- unresolved ineffective learning;
- lifecycle-state drift;
- **overdue** effectiveness measurement.

`PENDING_EFFECTIVENESS_MEASUREMENT` is visible planning state; `OVERDUE_EFFECTIVENESS_MEASUREMENT` is the machine-routable debt count.

An active successor may close the **unresolved ineffective** count for an older learning, but historical ineffectiveness remains in provenance/evidence.

## Durable learning and compaction

`PROJECT_MEMORY.md` is a compact active lesson index, not lifecycle authority and not an ever-growing diary.

- durable observation/provenance stays in `learning/LEARNING-*.md` or immutable review/health records;
- current lifecycle stays in `learning/LEARNING_STATE.json`;
- detailed historical reasoning stays in Git/review/health records;
- obsolete active guidance is removed after successor activation;
- evidence explaining an active safety rule is never deleted.

## Anti-overfitting

Do not create global policy from one accidental tool quirk unless the rule generalizes or materially improves safety. Repeated incidents sharing one root cause become one systemic learning, not many near-duplicate rules.
