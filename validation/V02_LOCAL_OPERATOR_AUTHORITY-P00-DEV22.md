# Phase00 dev22 — V02 local-operator LAB authority

```yaml
V02_AUTHORITY_ID: V02-LOCAL-OPERATOR-AUTHORITY-P00-DEV22-001
RUN_ID: RUN-P00-VALIDATION-002
STEP_ID: V02_LOCAL_OPERATOR_LAB_AUTHORITY
STATUS: WSL_LOCAL_INBOX_DEPLOYED_DEV22_LAB_READY_AUTHORITY_PACKAGE_PENDING
AUTHORITY_MODEL: LOCAL_OPERATOR_SAME_WSL_TRUST_DOMAIN
ASSURANCE_CLASS: SAME_TRUST_DOMAIN_LOCAL_OPERATOR
CANDIDATE_ID: 6f895394-e0b4-5434-bebc-79ee4e576282
CANDIDATE_BINDING_SHA256: 4aaf09ec2ef8618a5680e147cd2eeac695f940d45ae5cb0446c7b7e5c2483384
SOURCE_COMMIT: 86bb64938a136e3f8d6cfd0266685a01cb832b77
PACKAGE_SHA256: c2ea52087039f4c7b98c53a7cc0eaf1a4a0f931645f86491bf2eb8ef12956aae
BUILD_DIGEST: 69fdc1840472a96bce8f8841e4d780543827e3cefdd3fe3bc8445f8a1fb4a0d6
TEST_SET_DIGEST: 47d4ae767b26b05ef16d6809ea9377ef4e1b21bfbc4c44093dbd1cc158b75698
CONTRACT_DIGEST: f259656c48ed24c15bd48da2bb040950ed94d8edcf1473cf6456b96578c933ee
TRUST_ANCHOR_STATUS: ACTIVE_REACTIVATION_DEPLOYED_ON_AUDIT_PROMOTION
TRUST_OPS_DEPLOYMENT_STATUS: PASS_ON_DEPLOYMENT_AUDIT_PROMOTION
LOCAL_KEY_ACTIVATION_REVIEW: reviews/VALIDATION-V02-LOCAL-KEY-ACTIVATION-DEV22-REVIEW-001_PASS.md
LOCAL_KEY_ACTIVATION_AUDIT: reviews/VALIDATION-V02-LOCAL-KEY-ACTIVATION-DEV22-AUDIT-001_PASS.md
LOCAL_KEY_ACTIVATION_DISPOSITION: HISTORICAL_SUPERSEDED_PRIVATE_KEY_IDENTITY_UNAVAILABLE
LOCAL_KEY_REACTIVATION_RECORD: validation/V02_LOCAL_KEY_REACTIVATION-P00-DEV22.md
LOCAL_KEY_REACTIVATION_DEPLOYMENT: validation/V02_LOCAL_KEY_REACTIVATION_DEPLOYMENT-P00-DEV22.md
LOCAL_KEY_REACTIVATION_DEPLOYMENT_REVIEW: reviews/VALIDATION-V02-LOCAL-KEY-REACTIVATION-DEPLOYMENT-DEV22-REVIEW-001_PASS.md
LOCAL_KEY_REACTIVATION_DEPLOYMENT_AUDIT: reviews/VALIDATION-V02-LOCAL-KEY-REACTIVATION-DEPLOYMENT-DEV22-AUDIT-001_PASS.md
KEY_PARITY_VERIFIER: validation/tooling/verify_local_authority_key_parity.py
AUTHORITY_INBOX_PATH: /home/dragon/ai-film-dev/local-authority/dev22/inbox
AUTHORITY_INBOX_STORAGE: WSL_LOCAL
AUTHORITY_INBOX_DEPLOYMENT: validation/V02_WSL_LOCAL_AUTHORITY_INBOX_DEPLOYMENT-P00-DEV22.md
AUTHORITY_INBOX_DEPLOYMENT_RECEIPT: validation/V02_WSL_LOCAL_AUTHORITY_INBOX_DEPLOYMENT_RECEIPT-P00.json
AUTHORITY_INBOX_DEPLOYMENT_RECEIPT_SHA256: 8bb2f75cfe493d3e4d50f5a78e16f77d902870a7607928cb58fe2a69dbedc014
PRIVATE_KEY_IN_GIT: false
NATIVE_EXECUTION_STARTED: false
```

## Assurance statement

This is intentionally **not external authority**. The owner requires all execution to remain on the same Windows/WSL trust domain. The previously promoted public trust identity is historical and superseded because no durable private key derives its fingerprint. The corrected reactivation selects the already durable owner-only WSL key and machine-binds private-derived public bytes, raw public file, metadata and candidate ACTIVE trust anchor. The signature proves local key possession and signed-byte integrity; it does not prove an independent controller or out-of-band provenance.

The lower provenance assurance does not remove the remaining gates. Registration and every native fixture must declare `controller_external=false` and retain `disposable=true`, `no_real_credentials=true`, `no_production_mappings=true`. The signed envelope binds exact source/build/test/contract/candidate identity plus direct refs and role pins. Every protected object is content-addressed, suite lifetime is <=24h, all 86 procedure digests/fixture/request mappings remain exact, and `authorize()` must accept each pinned plan.

## Local envelope contract

`approval-envelope.json` uses schema 1 and kind `P00_LAB_LOCAL_OPERATOR_AUTHORITY_INTAKE`, `approved_by_local_operator=true`, exact `authority_model=LOCAL_OPERATOR_SAME_WSL_TRUST_DOMAIN`, candidate/binding/source/build/test/contract fields, mandatory registration/owner/local-operator/fixture/recovery/lab-plan/suite refs, and complete `role_pins`. Old `P00_LAB_EXTERNAL_AUTHORITY_INTAKE` envelopes are rejected as `ENVELOPE_SCHEMA`.

`approval-envelope.sig.json` remains a detached Ed25519 signature over exact raw envelope bytes. The reactivation-candidate public trust anchor is hash-pinned by `v02_local_authority_signature.py` and additionally checked against the durable private/public key pair by `verify_local_authority_key_parity.py`. Runtime trust substitution, key-identity drift, payload drift, key-ID mismatch and invalid signatures fail closed.

## Remaining actions

1. generate a fresh local approval object graph inside the WSL-local inbox with `controller_external=false` and a current <=24h suite;
2. sign the exact envelope with the existing durable WSL-local key while keeping private bytes outside the inbox;
3. run read-only staging preflight, authoritative intake and pre-V03 stage;
4. only a successful current evaluation may close V02 and allow V03.
