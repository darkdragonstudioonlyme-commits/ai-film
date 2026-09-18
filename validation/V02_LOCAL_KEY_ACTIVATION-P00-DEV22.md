# Phase00 dev22 — V02 local key activation

ACTIVATION_ID: V02-LOCAL-KEY-ACTIVATION-P00-DEV22-001
RUN_ID: RUN-P00-VALIDATION-002
STEP_ID: V02_LOCAL_OPERATOR_LAB_AUTHORITY
AUTHORITY_MODEL: LOCAL_OPERATOR_SAME_WSL_TRUST_DOMAIN
ASSURANCE_CLASS: SAME_TRUST_DOMAIN_LOCAL_OPERATOR
STATUS: HISTORICAL_SUPERSEDED_PRIVATE_KEY_IDENTITY_UNAVAILABLE
ALGORITHM: ED25519
KEY_ID: AI-FILM-LOCAL-DEV22-20260918-5d5957324955
PUBLIC_KEY_SHA256: 5d5957324955fb92d998aa7ab54bf551f580ef14b29cad0086274328526a285e
PROVENANCE_REF: WSL_LOCAL_OPERATOR_SELF_MANAGED:AI-FILM-LOCAL-DEV22-20260918-5d5957324955:5d5957324955fb92d998aa7ab54bf551f580ef14b29cad0086274328526a285e
PRIVATE_KEY_LOCATION_CLASS: WSL_OWNER_ONLY_OUTSIDE_GIT
PRIVATE_KEY_MODE: 0600
PRIVATE_KEY_IN_GIT: false
TRUST_ANCHOR_STATUS: HISTORICAL_SUPERSEDED
TRUST_ANCHOR_SHA256: 93dd4d3d411fe60dc711a13ed010eb6d0e620271ec0c44a101603f2dba4bacf9
REVIEW_RECORD: reviews/VALIDATION-V02-LOCAL-KEY-ACTIVATION-DEV22-REVIEW-001_PASS.md
AUDIT_RECORD: reviews/VALIDATION-V02-LOCAL-KEY-ACTIVATION-DEV22-AUDIT-001_PASS.md
PROMOTED_VALIDATION_HEAD: 9673283c3a8422485db4c3e48baa481dd720551d
PROMOTED_VALIDATION_CI_RUN: 35315862290
TRUST_OPS_DEPLOYMENT_STATUS: DEPLOYED_PRIOR_ANCHOR_KEY_PARITY_FAILED
NATIVE_EXECUTION_STARTED: false
SUPERSEDED_BY: validation/V02_LOCAL_KEY_REACTIVATION-P00-DEV22.md
SUPERSEDE_REASON: V02-LOCAL-KEY-PARITY-001

## Assurance boundary

This transaction implements the owner's explicit Choice B. The signing key is self-managed inside the same Windows/WSL trust domain as validation. The detached Ed25519 signature therefore proves possession of the configured local key and byte integrity of the signed envelope; it does not prove independent, external, or out-of-band authorization.

The private key remains outside Git and outside the approval inbox with mode 0600. Only the public key identity, hash and truthful local provenance are committed. Existing exact candidate binding, content-addressed objects, role pins, <=24h suite lifetime, disposable LAB, no-real-credentials and no-production-mappings constraints remain unchanged.

## Activation disposition

Design head `8760fd8636b77b7cb4f4f56d5cadadddd11ea3f0`, independent review `804df8a0df75ec004ec0a9c3f84f2d2d1bfc1425`, audit/promoted validation head `9673283c3a8422485db4c3e48baa481dd720551d` and promoted CI run `35315862290` are PASS. That public identity was reviewed/audited and promoted at the time, but subsequent V02-LOCAL-KEY-PARITY-001 proved that no durable private key derives its fingerprint. It remains immutable historical evidence and is no longer current signing authority.

The prior tooling/public trust bytes were later found deployed, but deployment verification had checked only private-key mode rather than private-derived public identity. The corrected reactivation adds that missing parity proof. Exact-dev22 runtime/LAB rebuild, approval-envelope creation/signing, READY/native policy materialization and V03 remain separate gated work.
