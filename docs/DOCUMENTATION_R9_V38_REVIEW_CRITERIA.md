# Documentation R9 V38 — Detailed Review Criteria

A detailed review may PASS only if all conditions below hold on one exact design SHA:

1. `STATE_VERSION=38`, `DOCUMENTATION_SYSTEM=DOCSYS-V2-R9`, revision `R5_V38_LIFECYCLE_MEASUREMENT_RECONCILIATION`.
2. Accepted dev21 source/package/test/contract identities are unchanged.
3. `RUN-P00-VALIDATION-001` remains BLOCKED at `V02_LAB_EXECUTION_AUTHORITY`; all 86 native cases remain `NOT_RUN`; qualification/SITE/HOST_READY are absent.
4. Canonical validation evidence head is exactly `179c475007802bf61414f043a0cf189b0fdc371a`.
5. Learning 004 reaches its V38 gate and may be EFFECTIVE only if the exact target passes the unchanged 9-case adversarial lifecycle regression and all lifecycle/governance checks.
6. Learning 005 is durable `PASS / ACTIVE` after completed V37 promotion while its effectiveness remains `PENDING_MEASUREMENT` with gate 39.
7. Learning aggregates derive to backlog=0, unresolved ineffective=0, pending measurement=1, overdue=0, historical ineffective=3.
8. Production-like facts remain eight timers / 44 safe control files / deterministic transfer export / metadata-only off-host anchor; binary payload upload remains false and `OFF_HOST_DR_CLAIMED=false`.
9. Lifecycle checker, adversarial suite, documentation governance, docs consistency, holistic audit checker, workflow continuity and runtime-state checks PASS on the exact target.
10. Diff contains no product implementation, native configuration, package content or product test-oracle change.
11. R6/A6 verdict paths are predeclared and absent on the frozen design tree.
12. Promotion permits only the two immutable verdict records, followed by mandatory post-promotion CI.

Any discrepancy or open finding requires review FAIL or a new exact design SHA.
