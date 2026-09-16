# Documentation R9 V37 — Holistic Audit Criteria

A holistic audit may PASS only if it evaluates the same exact design SHA as the required R5 detailed review and confirms:

1. R5 review is PASS with zero findings and binds the exact V37 design SHA.
2. Product implementation/native test oracle remain unchanged; V37 is documentation/control-plane reconciliation only.
3. Production-like readiness cannot satisfy V02 `DONE_WHEN` and all native execution counts remain zero.
4. Eight supervised timers and 44-file control state are supported by validation evidence and do not include protected authority, protected identity or credentials.
5. Deterministic transfer export is supervised, freshness-checked, heavy-drill verified and reproducible for identical payload state.
6. Private Google Drive evidence contains metadata/checksum identity only; the binary export remains on-host and `OFF_HOST_DR_CLAIMED=false`.
7. The initial V37 lifecycle failure is retained as durable evidence and the checker was not weakened to hide it.
8. Learning 004 is finalized to durable `ACTIVE / PASS` while preserving immutable R4/A4/V36 activation evidence and remains pending until V38.
9. Lifecycle-consistency learning 002 is reclassified `INEFFECTIVE` because its zero-drift metric failed; successor learning 005 is explicit, R5/A5-gated and pending until V39.
10. Aggregate truth is backlog=0, unresolved ineffective=0, pending measurement=2, overdue=0, historical ineffective=3.
11. Lifecycle/adversarial/governance/docs/audit/continuity/runtime-state executable checks PASS on the exact target.
12. Phased execution record preserves A→F boundaries and Phase F cannot advance without independently verified external authority.
13. Promotion is verdict-only and post-promotion CI is mandatory.

Any mismatch between review target, audit target, lifecycle state, canonical state or product/native boundary is an audit failure.