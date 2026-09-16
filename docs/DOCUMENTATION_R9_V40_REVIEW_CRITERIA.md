# Documentation R9 V40 — Detailed Review Criteria

A detailed review may PASS only if all conditions hold on one exact final V40 design SHA:

1. `STATE_VERSION=40`, `DOCUMENTATION_SYSTEM=DOCSYS-V2-R9`, revision `R7_V40_OPERATIONAL_MATURITY_RECONCILIATION`.
2. Exact dev21 source/package/test/contract identities and product/native test oracle are unchanged.
3. Same run `RUN-P00-VALIDATION-001` remains BLOCKED at V02; all 86 native cases remain NOT_RUN; qualification/SITE/HOST_READY remain absent.
4. Canonical validation evidence head is `c615af57b7216e2fbb0b3c71a9431e442a4def59`.
5. Operational maturity facts match validation evidence: 11 timers, 10 supervised previous-job results, 11 resource-bound services, 85-file backup/mirror, deterministic 85-file transfer export, full DR PASS, evidence-ledger chain PASS, incident drill PASS and 8/8 negative campaign.
6. Resource limits were selected from measured peak RSS and remain materially above observed usage; health verifies effective `MemoryMax=256M` and `TasksMax=128`.
7. Evidence ledger may contain historical FAIL snapshots but its chain/sidecars/state/freshness must verify.
8. Incident drill preserved a health FAIL record before recovery and a subsequent chained PASS record; temporary fault configuration is absent from current recovery state.
9. Recovery-schema migration preserved the old-payload failure and migrated producers before consumer success; no recovery predicate was weakened.
10. Learning 006 is normalized to durable `PASS / ACTIVE`, preserves R7/A7/V39 activation evidence, remains `PENDING_MEASUREMENT`, and retains V41 effectiveness gate.
11. Lifecycle aggregates remain backlog=0, unresolved ineffective=0, pending=1, overdue=0, historical ineffective=3.
12. Lifecycle checker, 9-case adversarial suite, governance, docs consistency, holistic audit, workflow continuity and runtime-state checks PASS on the exact target.
13. R8/A8 verdict paths are predeclared and absent from the frozen design tree.
14. Promotion may add only R8/A8 immutable verdicts and requires post-promotion CI.

Any discrepancy or open finding requires review FAIL or a new exact design SHA.