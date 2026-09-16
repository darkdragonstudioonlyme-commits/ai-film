# Documentation R9 V36 — Holistic Audit Criteria

A holistic audit may PASS only if it evaluates the same exact target as the required R4 detailed review and confirms:

1. R4 review is PASS with zero open findings and binds the exact V36 design SHA.
2. V36 remains a documentation/control-plane reconciliation; product implementation and native test oracle are unchanged.
3. Production-like operational readiness is descriptive evidence only and cannot satisfy V02 `DONE_WHEN`.
4. No public/canonical document exposes raw SID, MachineGuid, credentials, protected authority objects or private management secrets.
5. Same-host NTFS control mirror/rebuild set are not misrepresented as off-host or independent-device DR.
6. Lifecycle-consistency effectiveness evidence covers V34, V35 and the exact V36 candidate; no unreviewed correction was auto-promoted.
7. Historical ineffective learning retains a valid active/effective successor and is not deleted to improve aggregate status.
8. Learning aggregate values are machine-derived and lifecycle checker/adversarial suite PASS on the exact target.
9. Workflow continuity still resumes `RUN-P00-VALIDATION-001/V02`; all 86 native cases remain `NOT_RUN`.
10. Promotion is atomic verdict-only and post-promotion CI is required to resolve the predeclared verdict pair.

Any discrepancy between review target, audit target, lifecycle register and canonical state is an audit failure.