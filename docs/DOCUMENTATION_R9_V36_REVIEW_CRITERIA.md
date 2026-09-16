# Documentation R9 V36 — Detailed Review Criteria

A detailed review may PASS only if all conditions below hold on one exact design SHA:

1. `STATE_VERSION=36`, `DOCUMENTATION_SYSTEM=DOCSYS-V2-R9`, and revision is `R3_V36_PRODLIKE_EFFECTIVENESS_RECONCILIATION`.
2. Accepted dev21 source/package/test/contract identities are unchanged.
3. `RUN-P00-VALIDATION-001` remains `BLOCKED` at `V02_LAB_EXECUTION_AUTHORITY`; no native result, qualification, SITE result or HOST_READY claim is introduced.
4. Canonical production-like readiness accurately summarizes the validation-lane records without copying protected paths/identity or claiming off-host DR.
5. `LEARNING-LIFECYCLE-CONSISTENCY-002` moves to `EFFECTIVE` only with immutable V34/V35/V36 measurement evidence and `measurement_gate={kind: COMPLETE}`.
6. The V36 adversarial regression recurrence is preserved as evidence: learning 003 becomes `INEFFECTIVE`, points to successor 004, and successor 004 is `ACTIVE_ON_PROMOTION / PENDING_MEASUREMENT` with a future V38 gate.
7. Learning aggregates derive to backlog=0, unresolved ineffective=0, pending measurement=1, overdue measurement=0 and historical ineffective=2.
8. Both historical ineffective learnings retain valid successor/meta-review paths; no failed learning is deleted or silently reset to effective.
9. `overdue_measurement_drift` constructs its own pending-measurement preconditions and fails the checker as `learning-overdue-measurement-drift` even when the ambient canonical register has zero other pending measurements.
10. Lifecycle checker and all adversarial lifecycle regression cases PASS on the exact target; lifecycle checker acceptance semantics are not weakened in this revision.
11. Documentation governance, active-doc consistency, holistic audit checker, workflow continuity and runtime-state checks PASS on the exact target.
12. Diff contains no product implementation/native/config/test-oracle change.
13. R4/A4 verdict paths and IDs are predeclared and absent on the frozen design tree.
14. Promotion contract permits only the two predeclared verdict records to be added after audit; post-promotion CI is mandatory.

Any open finding yields review FAIL or requires a new exact design SHA.