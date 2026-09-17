# Documentation R9 V41 — Detailed Review Criteria

A detailed review may PASS only if all conditions hold on one exact final V41 design SHA:

1. `STATE_VERSION=41`, `DOCUMENTATION_SYSTEM=DOCSYS-V2-R9`, revision `R8_V41_RECOVERY_EFFECTIVENESS_RECONCILIATION`.
2. Exact dev21 source/package/test/contract identities are unchanged; no product implementation/native configuration/test oracle changes exist.
3. `RUN-P00-VALIDATION-001` remains BLOCKED at V02; all 86 native cases remain NOT_RUN; qualification/SITE/HOST_READY remain absent.
4. Canonical validation evidence head is `8024990809364168f7bd04cde44ccf7b30c60b66`.
5. Health supervises 11 service execution-freshness states in addition to timer state/results; stale and never-completed-after-grace negative tests are PASS.
6. Actual producer overflow tests prove backup retention=14 and evidence-ledger retention=30 with prune-anchor chain continuity.
7. Resource bounds are still `MemoryMax=256M` / `TasksMax=128`; safe cgroup binding probe confirms kernel materialization without destructive resource exhaustion.
8. The post-V40 recovery transition follows producer-first ordering and current verifiers/full-DR/fail-closed campaign/ledger/health are PASS.
9. Current backup count/SHA and export SHA are represented as rotating observed samples, not stable candidate identity.
10. Private off-host metadata still pins stable exact-candidate/rebuild identity only; binary payload remains on-host and `OFF_HOST_DR_CLAIMED=false`.
11. Learning 006 is EFFECTIVE only because its V41 gate and recovery-change trigger are both satisfied and the exact V41 executable suite/CI pass without weakened predicates.
12. Learning aggregates are backlog=0, unresolved ineffective=0, pending measurement=0, overdue=0, historical ineffective=3.
13. Lifecycle checker, 9-case adversarial suite, documentation governance, active-doc consistency, holistic audit checker, workflow continuity and runtime-state checks PASS on the exact target.
14. R9/A9 verdict paths are predeclared and absent from the frozen design tree.
15. Promotion may add only the immutable R9/A9 verdict records and must be followed by post-promotion CI.

Any discrepancy or open finding requires review FAIL or a new exact design SHA.
