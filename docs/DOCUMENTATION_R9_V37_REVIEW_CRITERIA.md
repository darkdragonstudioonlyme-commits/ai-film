# Documentation R9 V37 — Detailed Review Criteria

A detailed review may PASS only if all conditions below hold on one exact design SHA:

1. `STATE_VERSION=37`, `DOCUMENTATION_SYSTEM=DOCSYS-V2-R9`, revision `R4_V37_PHASED_PRODLIKE_EXPORT_RECONCILIATION`.
2. Accepted dev21 source/package/test/contract identities are unchanged.
3. `RUN-P00-VALIDATION-001` remains BLOCKED at `V02_LAB_EXECUTION_AUTHORITY`; all 86 native cases remain `NOT_RUN`; qualification/SITE/HOST_READY are absent.
4. Canonical production-like facts match the reconciled validation lane: eight supervised timers, 44-file safe control backup, verified NTFS mirror/rebuild and supervised deterministic transfer export.
5. Transfer export is deterministic for identical payload state, health-gated, bounded to ten minutes, hardened to the same production-like service class and heavy-drill verified.
6. Private Google Drive evidence is only an off-host metadata/checksum anchor; binary payload upload remains false and `OFF_HOST_DR_CLAIMED=false`.
7. The initial V37 lifecycle failure is preserved as health evidence; checker semantics are not weakened.
8. Learning 004 is finalized from transition-only `ACTIVE_ON_PROMOTION / PASS_ON_FINAL_REVIEW` to durable `ACTIVE / PASS` while retaining R4/A4/V36 activation evidence and remaining `PENDING_MEASUREMENT` until V38.
9. `LEARNING-LIFECYCLE-CONSISTENCY-002` becomes `INEFFECTIVE` because its zero-drift metric was violated and must point to successor `LEARNING-PROMOTION-STATE-FINALIZATION-005`.
10. Learning 005 is predeclared `ACTIVE_ON_PROMOTION / PENDING_MEASUREMENT`, bound to R5/A5 and V37, with effectiveness gate V39.
11. Learning aggregates are backlog=0, unresolved ineffective=0, pending measurement=2, overdue=0, historical ineffective=3.
12. Lifecycle checker, 9-case adversarial suite, documentation governance, docs consistency, holistic audit checker, workflow continuity and runtime-state checks PASS on the exact target.
13. Diff contains no product implementation, native configuration, package content or product test-oracle change.
14. R5/A5 verdict paths are predeclared and absent on the frozen design tree.
15. Promotion permits only the two immutable verdict records, followed by mandatory post-promotion CI.

Any discrepancy or open finding requires review FAIL or a new exact design SHA.