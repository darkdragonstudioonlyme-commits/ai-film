# Phase00 dev22 — V02 local-operator LAB authority

```yaml
V02_AUTHORITY_ID: V02-LOCAL-OPERATOR-AUTHORITY-P00-DEV22-001
RUN_ID: RUN-P00-VALIDATION-002
STEP_ID: V02_LOCAL_OPERATOR_LAB_AUTHORITY
STATUS: LOCAL_KEY_REVIEWED_AUDITED_DEV22_LAB_AND_AUTHORITY_PACKAGE_PENDING
AUTHORITY_MODEL: LOCAL_OPERATOR_SAME_WSL_TRUST_DOMAIN
ASSURANCE_CLASS: SAME_TRUST_DOMAIN_LOCAL_OPERATOR
CANDIDATE_ID: 6f895394-e0b4-5434-bebc-79ee4e576282
CANDIDATE_BINDING_SHA256: 4aaf09ec2ef8618a5680e147cd2eeac695f940d45ae5cb0446c7b7e5c2483384
SOURCE_COMMIT: 86bb64938a136e3f8d6cfd0266685a01cb832b77
PACKAGE_SHA256: c2ea52087039f4c7b98c53a7cc0eaf1a4a0f931645f86491bf2eb8ef12956aae
BUILD_DIGEST: 69fdc1840472a96bce8f8841e4d780543827e3cefdd3fe3bc8445f8a1fb4a0d6
TEST_SET_DIGEST: 47d4ae767b26b05ef16d6809ea9377ef4e1b21bfbc4c44093dbd1cc158b75698
CONTRACT_DIGEST: f259656c48ed24c15bd48da2bb040950ed94d8edcf1473cf6456b96578c933ee
TRUST_ANCHOR_STATUS: ACTIVE_REVIEWED_AUDITED
TRUST_OPS_DEPLOYMENT_STATUS: NOT_CLAIMED_BY_GIT_EVIDENCE
LOCAL_KEY_ACTIVATION_REVIEW: reviews/VALIDATION-V02-LOCAL-KEY-ACTIVATION-DEV22-REVIEW-001_PASS.md
LOCAL_KEY_ACTIVATION_AUDIT: reviews/VALIDATION-V02-LOCAL-KEY-ACTIVATION-DEV22-AUDIT-001_PASS.md
PRIVATE_KEY_IN_GIT: false
NATIVE_EXECUTION_STARTED: false
```

## Assurance statement

This is intentionally **not external authority**. The owner requires all execution to remain on the same Windows/WSL trust domain. The reviewed Ed25519 private key is stored locally under an owner-only WSL path and the committed public trust identity is independently reviewed/audited. The signature proves local key possession and signed-byte integrity; it does not prove an independent controller or out-of-band provenance.

The lower provenance assurance does not remove the remaining gates. Registration and every native fixture must declare `controller_external=false` and retain `disposable=true`, `no_real_credentials=true`, `no_production_mappings=true`. The signed envelope binds exact source/build/test/contract/candidate identity plus direct refs and role pins. Every protected object is content-addressed, suite lifetime is <=24h, all 86 procedure digests/fixture/request mappings remain exact, and `authorize()` must accept each pinned plan.

## Local envelope contract

`approval-envelope.json` uses schema 1 and kind `P00_LAB_LOCAL_OPERATOR_AUTHORITY_INTAKE`, `approved_by_local_operator=true`, exact `authority_model=LOCAL_OPERATOR_SAME_WSL_TRUST_DOMAIN`, candidate/binding/source/build/test/contract fields, mandatory registration/owner/local-operator/fixture/recovery/lab-plan/suite refs, and complete `role_pins`. Old `P00_LAB_EXTERNAL_AUTHORITY_INTAKE` envelopes are rejected as `ENVELOPE_SCHEMA`.

`approval-envelope.sig.json` remains a detached Ed25519 signature over exact raw envelope bytes. The reviewed public trust anchor is hash-pinned by `v02_local_authority_signature.py`. Runtime trust substitution, payload drift, key-ID mismatch and invalid signatures fail closed.

## Remaining actions

1. deploy/reverify the exact reviewed tooling and public trust identity on the WSL validation-ops surface; Git promotion alone is not deployment evidence;
2. rebuild prodlike runtime and stopped LAB to exact dev22, create fresh candidate-specific snapshots/seal and keep all native cases NOT_RUN;
3. generate a new local approval object graph with `controller_external=false` and current <=24h suite;
4. sign exact envelope locally, run read-only staging preflight, then authoritative intake and pre-V03 stage;
5. only a successful current evaluation may close V02 and allow V03.
