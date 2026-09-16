# Documentation System V2 R9 — Guarded Self-Learning Lifecycle

## Review finding that motivates R9

R8 materially improved continuity, release-selected governance, source-visibility disclosure and learning activation semantics. Cross-session review of the promoted system found one remaining control-plane gap: the **current lifecycle of a learning does not have one machine-readable owner**.

`PROJECT_STATE` can report `LEARNED_BUT_NOT_ACTIVE_BACKLOG: 0` while immutable learning records still contain stale snapshots such as `PENDING_ACTIVATION`, `PENDING_*REVIEW`, or omit activation fields entirely. Existing governance/audit checkers verify that learning concepts exist in policy, but do not reconcile every durable learning record with canonical activation/effectiveness state. This means the system can describe the correct learning loop while failing to prove that the loop actually closed.

## R9 correction

R9 introduces `learning/LEARNING_STATE.json` as the single machine-readable owner of **current learning lifecycle state**. Durable `learning/LEARNING-*.md` records remain evidence/provenance and are not trusted as current lifecycle truth after creation.

For every reusable learning, the lifecycle register owns:

- immutable record path and score;
- promotion/activation target;
- independent review status;
- activation status, activated release and **activation evidence**;
- effectiveness status and evidence;
- successor when ineffective/superseded;
- human-readable measurement trigger plus a **structured measurement gate**.

`PROJECT_STATE` stores only derived learning aggregates. `tools/check_learning_lifecycle.py` recomputes those aggregates from the register and fails closed on drift.

## Guarded automation contract

R9 deliberately automates **detection, reconciliation, due-state calculation and routing**, not unreviewed policy mutation.

```text
SESSION/WORKFLOW EVENT
→ detect reusable observation or lifecycle inconsistency
→ persist immutable learning/health evidence
→ update candidate lifecycle register
→ checker derives activation / ineffective / pending-measurement / overdue-measurement state
→ workflow-health trigger if actionable debt or ineffectiveness exists
→ propose smallest policy/tool/design correction
→ independent DOC-REVIEW
→ holistic DOC-AUDIT
→ canonical activation
→ measure effectiveness when gate becomes due
```

Automation MAY:

- detect missing/stale lifecycle fields;
- derive learning backlog, ineffective and measurement metrics;
- calculate whether a structured measurement gate is due;
- trigger meta-review routing;
- generate a candidate correction/design diff;
- block continuation when learning-control invariants are inconsistent.

Automation MUST NOT:

- mark its own correction reviewed;
- promote a documentation-system release without review/audit;
- rewrite immutable evidence to make metrics green;
- treat a proposed policy change as active before canonical promotion.

This is **guarded self-optimization**, not self-authorizing governance.

## Lifecycle state machine

Observation/provenance is immutable. Current lifecycle is mutable only through the register.

```text
DISCOVERED
→ REVIEW_PENDING
→ REVIEWED
→ PENDING_ACTIVATION | BLOCKED
→ ACTIVE_UNMEASURED
→ EFFECTIVE | INEFFECTIVE
→ SUPERSEDED | RETIRED
```

A learning may be `BLOCKED` before activation, with explicit owner/return path. `INEFFECTIVE` is not failure to record history; it is a mandatory meta-review trigger that must name a successor/correction path.

`ACTIVE` requires immutable activation evidence. Promotion-ready `ACTIVE_ON_PROMOTION` requires the predeclared final review and audit records in its activation-evidence set.

## Structured effectiveness measurement

Natural-language success metrics remain useful for meaning, but due-state must be machine-evaluable. R9 supports structured `measurement_gate` values, initially:

```json
{"kind":"COMPLETE"}
{"kind":"STATE_VERSION_AT_LEAST","value":36}
```

`PENDING_EFFECTIVENESS_MEASUREMENT` means measurement is planned. `OVERDUE_EFFECTIVENESS_MEASUREMENT` means the structured gate is already satisfied but evidence is still missing; only the latter is automatic workflow-health debt.

For the new R9 lifecycle correction, the first scheduled gate is V36 — three canonical state transitions after V33 — while any earlier lifecycle inconsistency triggers meta-review immediately.

## Cross-session bootstrap behavior

A fresh chat/session must not infer learning health from prose. During bootstrap it runs the lifecycle checker after state/runtime reconciliation and before final routing. The checker verifies:

1. every register entry references one existing durable learning record;
2. every durable active learning record is represented in the register;
3. register documentation-release identity matches canonical state;
4. review/activation/effectiveness transitions are internally valid;
5. active learning has activation evidence; promotion-conditional learning predeclares final review/audit evidence;
6. activation targets already active cannot remain silently pending;
7. `EFFECTIVE` requires evidence and `INEFFECTIVE` requires a successor;
8. pending measurement has a structured gate and overdue count is derived from current state version;
9. `PROJECT_STATE` learning aggregates equal derived register counts;
10. lifecycle drift, unresolved ineffectiveness or overdue measurement surfaces workflow-health debt.

## R8 learning reconciliation

R9 explicitly closes the stale-lifecycle inconsistency discovered during this review:

- `LEARNING-CONTROL-001` — active and effective; lifecycle-neutral checkers survived later state evolution;
- `LEARNING-WORKFLOW-CONTINUITY-001` — active and effective; repeated sessions resumed the same run without duplicate logical runs;
- `LEARNING-SOURCE-VISIBILITY-001` — active and effective; formal handoffs distinguish artifact-only/partial visibility from exact identity;
- `LEARNING-DOCSYS-ACTIVATION-001` — policy concept active, but enforcement was **ineffective** because stale durable lifecycle snapshots were not reconciled; successor is `LEARNING-LIFECYCLE-CONSISTENCY-002`.

## Non-goals / authority boundaries

R9 does not change Phase00 product contracts, source behavior, CODE_REVIEW, native LAB/SITE authority, qualification or HOST_READY. Learning automation cannot become a source of product gate authority.

## Promotion contract

The exact final R9 design tree must contain the intended post-promotion state, lifecycle register, policy/checker changes, and predeclared final review/audit IDs/paths. After final audit, promotion may add only those immutable verdict records. Any other policy/state/checker change reopens detailed review and holistic audit.