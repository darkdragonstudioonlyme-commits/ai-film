# Documentation R9 V40 — Holistic Audit Criteria

A holistic audit may PASS only after R8 detailed review PASS and only on the same exact V40 design SHA.

The audit must confirm:

1. one canonical run/lifecycle register remains authoritative;
2. V02 remains external-authority-only and no non-native control grants LAB/SITE/native authority;
3. product implementation, package identities, native configuration and product test oracle are unchanged;
4. validation head `c615af57b7216e2fbb0b3c71a9431e442a4def59` durably supports the operational-maturity claims;
5. 11 timers, resource bounds, evidence ledger, user-manager reexec rehearsal and incident FAIL→PASS drill are real executable controls rather than documentation-only claims;
6. 85-file recovery state contains the evidence-ledger producer/verifier/history, 11 timer definitions and 11 resource-bound drop-ins;
7. the stricter recovery consumer rejected old state before producer migration and no check was weakened;
8. learning 006 is durably ACTIVE/PASS but remains pending effectiveness until V41;
9. aggregate lifecycle truth is backlog=0, unresolved ineffective=0, pending=1, overdue=0, historical ineffective=3;
10. exact-target executable checks and GitHub Actions pass;
11. only R8/A8 verdict records may be added during promotion and post-promotion CI is mandatory.

Audit FAILs on any open discrepancy, authority overstatement, stale evidence binding or weakened recovery/lifecycle predicate.