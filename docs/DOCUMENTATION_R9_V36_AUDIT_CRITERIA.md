# Documentation R9 V36 — Holistic Audit Criteria

A holistic audit may PASS only if it evaluates the same exact target as the required R4 detailed review and confirms:

1. R4 review is PASS with zero open findings and binds the exact V36 design SHA.
2. V36 remains a documentation/control-plane reconciliation; product implementation and native test oracle are unchanged.
3. Production-like operational readiness is descriptive evidence only and cannot satisfy V02 `DONE_WHEN`.
4. No public/canonical document exposes raw SID, MachineGuid, credentials, protected authority objects or private management secrets.
5. Same-host NTFS control mirror/rebuild set are not misrepresented as off-host or independent-device DR.
6. Lifecycle-consistency effectiveness evidence covers V34, V35 and the exact V36 candidate; no unreviewed correction was auto-promoted.
7. The V36 adversarial-fixture recurrence is preserved: learning 003 is `INEFFECTIVE`, successor 004 is promotion-gated and pending later effectiveness measurement, and neither failure nor historical evidence is deleted to improve status.
8. The corrected overdue-measurement negative test constructs its own semantic preconditions and the full adversarial suite PASSes on the exact target with no lifecycle-checker predicate weakening.
9. Learning aggregate values are machine-derived: backlog=0, unresolved ineffective=0, pending measurement=1, overdue=0, historical ineffective=2.
10. Workflow continuity still resumes `RUN-P00-VALIDATION-001/V02`; all 86 native cases remain `NOT_RUN`.
11. Promotion is atomic verdict-only and post-promotion CI is required to resolve the predeclared verdict pair and activate successor learning 004.

Any discrepancy between review target, audit target, lifecycle register and canonical state is an audit failure.