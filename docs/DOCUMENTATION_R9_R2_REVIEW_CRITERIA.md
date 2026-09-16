# DOCSYS-V2-R9 Reconciliation R2 — detailed review criteria

1. V35 is a data/lifecycle reconciliation, not a semantic weakening of `tools/check_learning_lifecycle.py`.
2. `LEARNING-ADVERSARIAL-FIXTURE-ISOLATION-003` may become EFFECTIVE only with immutable `HEALTH_REVIEW-DOCSYS-R9-CI-003` plus post-correction promotion CI evidence.
3. The corrected adversarial regression must be proven on both promoted-base and post-correction-promotion repository states.
4. `stale_activation` test fixture must not assume an `ACTIVE_ON_PROMOTION` record always exists; it must derive a current-release active learning.
5. `LEARNING-LIFECYCLE-CONSISTENCY-002` remains ACTIVE/PENDING_MEASUREMENT with V36 gate.
6. V35 aggregates must derive exactly: backlog 0, unresolved ineffective 0, pending measurement 1, overdue measurement 0, historical ineffective 1.
7. Canonical NEXT_ACTION must point back to unchanged `RUN-P00-VALIDATION-001/V02_LAB_EXECUTION_AUTHORITY`.
8. R1/A1 and R2/A2 records remain immutable historical evidence; V35 uses distinct R3/A3 review/audit IDs/paths.
9. Exact V35 design CI must pass all portable governance steps.
10. No Phase00 source/native/test-oracle/LAB authority/qualification/HOST_READY change occurs.
11. Promotion adds only predeclared R3 review/audit records to the exact V35 target.
12. Post-promotion CI on main must pass before this documentation review/recovery loop is considered closed.
