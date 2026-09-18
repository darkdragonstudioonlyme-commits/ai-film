# Phase00 dev22 — V02 local key activation

ACTIVATION_ID: V02-LOCAL-KEY-ACTIVATION-P00-DEV22-001
RUN_ID: RUN-P00-VALIDATION-002
STEP_ID: V02_LOCAL_OPERATOR_LAB_AUTHORITY
AUTHORITY_MODEL: LOCAL_OPERATOR_SAME_WSL_TRUST_DOMAIN
ASSURANCE_CLASS: SAME_TRUST_DOMAIN_LOCAL_OPERATOR
STATUS: DESIGN_CANDIDATE_PENDING_REVIEW
ALGORITHM: ED25519
KEY_ID: AI-FILM-LOCAL-DEV22-20260918-5d5957324955
PUBLIC_KEY_SHA256: 5d5957324955fb92d998aa7ab54bf551f580ef14b29cad0086274328526a285e
PROVENANCE_REF: WSL_LOCAL_OPERATOR_SELF_MANAGED:AI-FILM-LOCAL-DEV22-20260918-5d5957324955:5d5957324955fb92d998aa7ab54bf551f580ef14b29cad0086274328526a285e
PRIVATE_KEY_LOCATION_CLASS: WSL_OWNER_ONLY_OUTSIDE_GIT
PRIVATE_KEY_MODE: 0600
PRIVATE_KEY_IN_GIT: false
TRUST_ANCHOR_STATUS: ACTIVE_CANDIDATE
TRUST_ANCHOR_SHA256: 93dd4d3d411fe60dc711a13ed010eb6d0e620271ec0c44a101603f2dba4bacf9
NATIVE_EXECUTION_STARTED: false

## Assurance boundary

This transaction implements the owner's explicit Choice B. The signing key is self-managed inside the same Windows/WSL trust domain as validation. The detached Ed25519 signature therefore proves possession of the configured local key and byte integrity of the signed envelope; it does not prove independent, external, or out-of-band authorization.

The private key remains outside Git and outside the approval inbox with mode 0600. Only the public key identity, hash and truthful local provenance are committed. Existing exact candidate binding, content-addressed objects, role pins, <=24h suite lifetime, disposable LAB, no-real-credentials and no-production-mappings constraints remain unchanged.

## Activation transaction

The committed trust anchor changes from PENDING_LOCAL_KEY to ACTIVE and is re-pinned by v02_local_authority_signature.py. V02_TOOLING_MANIFEST.json binds the active trust-anchor hash and public key fingerprint. This design candidate alone does not approve an envelope, rebuild the LAB, create a READY flag, materialize native policy or advance V03.

Independent review must verify the exact public key against the WSL-local owner-only key metadata without exposing private bytes, repeat all V02 tooling regressions, and confirm no secret/private material entered Git. Audit must be verdict-only after design freeze.
