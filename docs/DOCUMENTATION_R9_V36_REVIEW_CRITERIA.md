# Documentation R9 V36 — Detailed Review Criteria

A detailed review may PASS only if all conditions below hold on one exact design SHA:

1. `STATE_VERSION=36`, `DOCUMENTATION_SYSTEM=DOCSYS-V2-R9`, and revision is `R3_V36_PRODLIKE_EFFECTIVENESS_RECONCILIATION`.
2. Accepted dev21 source/package/test/contract identities are unchanged.
3. `RUN-P00-VALIDATION-001` remains `BLOCKED` at `V02_LAB_EXECUTION_AUTHORITY`; no native result, qualification, SITE result or HOST_READY claim is introduced.
4. Canonical production-like readiness accurately summarizes the validation-lane records without copying protected paths/identity or claiming off-host DR.
5. `LEARNING-LIFECYCLE-CONSISTENCY-002` moves to `EFFECTIVE` only with immutable V34/V35/V36 measurement evidence and `measurement_gate={kind: COMPLETE}`.
6. Learning aggregates derive to backlog=0, unresolved ineffective=0, pending measurement=0, overdue measurement=0 and historical ineffective=1.
7. The historical ineffective learning still points to the active/effective lifecycle-consistency successor.
8. Lifecycle checker and adversarial lifecycle regression PASS on the exact target; no checker semantics are weakened in this revision.
9. Documentation governance, active-doc consistency, holistic audit checker, workflow continuity and runtime-state checks PASS on the exact target.
10. Diff contains no product implementation/native/config/test-oracle change.
11. R4/A4 verdict paths and IDs are predeclared and absent on the frozen design tree.
12. Promotion contract permits only the two predeclared verdict records to be added after audit; post-promotion CI is mandatory.

Any open finding yields review FAIL or requires a new exact design SHA.