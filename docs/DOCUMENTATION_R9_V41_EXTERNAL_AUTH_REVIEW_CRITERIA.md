# DOCSYS-V2-R9 V41 External Authenticity — R13 Detailed Review Criteria

R13 may PASS only if one exact `R12_V41_EXTERNAL_AUTHENTICITY_RECONCILIATION` design SHA satisfies all conditions below.

1. State remains V41/VALIDATION and exact dev21 source/package/test/contract identities are unchanged.
2. Validation evidence head is exactly `9a3854d80b7e4c35c5d2ec933709280ce0baa7fa` and R13 verifies that remote branch currently resolves to that commit.
3. Canonical V02 routing explicitly requires independently established Ed25519 public-key provenance, separate reviewed trust-anchor activation, and an externally signed exact approval envelope before V03.
4. Documentation does not claim an ACTIVE external key, approval envelope, READY flag, native trust, native execution, qualification, SITE evidence or HOST_READY.
5. `PROJECT_STATE.md`, JSON V41 and NEXT_WORK_ITEM agree on `DEPLOYED_PENDING_EXTERNAL_KEY`, `PENDING_EXTERNAL_KEY`, missing envelope and not-ready state.
6. R13/A13 identities, branch roles and active design record are predeclared; historical R12/A12 is not reused for the changed tree.
7. Learning 008 is finalized ACTIVE only from completed historical R12/A12 evidence; it remains PENDING_MEASUREMENT unless separately measured.
8. Learning 009 immutable metric matches the lifecycle register, is conditional `ACTIVE_ON_PROMOTION`, and remains PENDING_MEASUREMENT.
9. Derived learning aggregates equal the register: zero activation backlog, zero unresolved ineffective, five pending effectiveness measurements, zero overdue, three semantically verified EFFECTIVE and four historical INEFFECTIVE.
10. Current-authority prose passes stale-verdict detector using R13/A13 as the live pair; older verdict pairs are line-locally historical/superseded only.
11. Existing lifecycle, 16 adversarial lifecycle cases, documentation governance, active-doc + 4 adversarial active-doc cases, workflow continuity and holistic audit all PASS on the exact design target.
12. Platform main protection remains explicit external debt; no repository-enforcement claim is invented.

Any native/product advancement, local-key self-issuance, unsigned-approval allowance, stale validation head, stale live verdict pair or lifecycle mismatch requires R13 FAIL.
