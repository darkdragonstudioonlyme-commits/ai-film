# NEXT WORK ITEM — rebuild exact dev22 LAB/runtime and complete V02 local authority

```yaml
RUN_ID: RUN-P00-VALIDATION-002
WORKFLOW_ID: WF-P00-VALIDATION-ENTRY
LANE: VALIDATION
STATUS: BLOCKED_DEV22_LAB_REBUILD_AND_LOCAL_AUTHORITY_PACKAGE
MODE: VALIDATION
PHASE: "00 — Host / WSL"
WORK_ITEM: M-P00-VALIDATION-DEV22
INPUT_IDENTITY:
  ACCEPTED_VERSION: 0.1.0.dev22
  SOURCE_COMMIT: 86bb64938a136e3f8d6cfd0266685a01cb832b77
  PACKAGE_SHA256: c2ea52087039f4c7b98c53a7cc0eaf1a4a0f931645f86491bf2eb8ef12956aae
  SOURCE_DIGEST: 69fdc1840472a96bce8f8841e4d780543827e3cefdd3fe3bc8445f8a1fb4a0d6
  TEST_DIGEST: 47d4ae767b26b05ef16d6809ea9377ef4e1b21bfbc4c44093dbd1cc158b75698
  CONTRACT_DIGEST: f259656c48ed24c15bd48da2bb040950ed94d8edcf1473cf6456b96578c933ee
  VALIDATION_EVIDENCE_HEAD: c5f2d43aaa0d2e0ae796ea7981f578bcb2b0a148
  CANDIDATE_ID: 6f895394-e0b4-5434-bebc-79ee4e576282
  CANDIDATE_BINDING_SHA256: 4aaf09ec2ef8618a5680e147cd2eeac695f940d45ae5cb0446c7b7e5c2483384
  AUTHORITY_MODEL: LOCAL_OPERATOR_SAME_WSL_TRUST_DOMAIN
  KEY_ID: AI-FILM-P00-DEV22-LOCAL-001
  PUBLIC_KEY_SHA256: 7f14c158dd09ec9e40572131538bab6818e768cc9f33cb1ec3708a09df9a8a69
  TRUST_ANCHOR_SHA256: 0af4f9adadcd64bbc2b23a51d572d01af08bdf197c7d96150abdf1ffc9acbbe8
  TRUST_OPS_DEPLOYMENT_STATUS: DEPLOYED_VERIFIED_KEY_PARITY
  DEPLOYMENT_RECEIPT_SHA256: 9f4fed765335b7aba64358b0f76be83b8bdf51a07218230483326cb74d1bdc60
  REMOTE_SOURCE_REF: source/p00-dev22-local-authority-exact
GOAL: "Complete current dev22 V02 without crossing into native execution: rebuild/seal exact-dev22 runtime/LAB, create/sign a fresh candidate-specific local authority graph and pass fail-closed staging/intake/pre-V03 verification."
STEPS:
  - V00_VALIDATION_LANE_ACTIVATION: COMPLETE
  - V01_CODE_REVIEW_GATE: COMPLETE
  - V02_LOCAL_OPERATOR_LAB_AUTHORITY: BLOCKED
  - V03_NATIVE_LAB_REGRESSION: NOT_STARTED
  - V04_QUALIFICATION_RECEIPT: NOT_STARTED
  - V05_SITE_VALIDATION: NOT_STARTED
  - V06_GATE_ASSESSMENT: NOT_STARTED
CURRENT_STEP: V02_LOCAL_OPERATOR_LAB_AUTHORITY
SUCCESS_OUTPUT: "Current evaluation returns LAB_LOCAL_OPERATOR_AUTHORITY_VERIFIED for exact dev22/candidate 6f895394-e0b4-5434-bebc-79ee4e576282 with local signature verified and containment intact; no native case has run before V02 closure."
ON_SUCCESS: RUN-P00-VALIDATION-002/V03_NATIVE_LAB_REGRESSION
ON_FAIL: VALIDATION_FAILURE_ROUTE
ON_BLOCK: BLOCK-P00-VAL-LOCAL-AUTH-DEV22-001
EXIT_CONDITION: "Exact-dev22 runtime/LAB and the current signed local-authority object graph pass authoritative V02 verification; V03 has not started before this condition."
```

## Required sequence

1. Preserve the reviewed/audited/deployed V02 tooling/trust bytes and verify current key parity before and after runtime/LAB work.
2. Rebuild/rebind the production-like runtime and stopped disposable `AI-FILM-P00-LAB` to exact dev22 source/package. Create fresh candidate-specific snapshots/seal while all 86 native cases remain NOT_RUN.
3. Build a fresh authority object graph for candidate `6f895394-e0b4-5434-bebc-79ee4e576282` with `controller_external=false`, all containment barriers true, exact role pins/content hashes and a current <=24h suite.
4. Sign the exact envelope with durable reviewed WSL-local key `AI-FILM-P00-DEV22-LOCAL-001`; run byte-aware staging preflight, then authoritative intake and pre-V03 fail-closed stage.
5. Advance to V03 only when current V02 done-when succeeds. No dev21 authority object, old `5d595732...` key identity, READY artifact, native policy or native result is reusable as dev22 authority.

Local cryptographic approval remains same-trust-domain integrity/key-possession evidence, not independent external provenance.
