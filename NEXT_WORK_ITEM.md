# NEXT WORK ITEM — complete dev22 V02 local-operator authority

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
  CODE_REVIEW_RECORD: reviews/CODE-REVIEW-P00-001_DEV22_LOCAL_AUTHORITY.md
  CODE_REVIEW_PASS: true
  AUTHORITY_MODEL: LOCAL_OPERATOR_SAME_WSL_TRUST_DOMAIN
  VALIDATION_EVIDENCE_HEAD: 66e5d30a6bde9dcdcb310fc1772bccb16702db24
  CANDIDATE_ID: 6f895394-e0b4-5434-bebc-79ee4e576282
  CANDIDATE_BINDING_SHA256: 4aaf09ec2ef8618a5680e147cd2eeac695f940d45ae5cb0446c7b7e5c2483384
  KEY_ID: AI-FILM-LOCAL-DEV22-20260918-5d5957324955
  PUBLIC_KEY_SHA256: 5d5957324955fb92d998aa7ab54bf551f580ef14b29cad0086274328526a285e
  TRUST_ANCHOR_SHA256: 93dd4d3d411fe60dc711a13ed010eb6d0e620271ec0c44a101603f2dba4bacf9
  LOCAL_KEY_GIT_STATUS: REVIEWED_AUDITED_PROMOTED
  TRUST_OPS_DEPLOYMENT_STATUS: NOT_CLAIMED_BY_GIT_EVIDENCE
  REMOTE_SOURCE_REF: source/p00-dev22-local-authority-exact
GOAL: "Complete current dev22 V02 local-operator authority without crossing into native execution: deploy/reverify reviewed trust/tooling, rebuild exact-dev22 prodlike/LAB state, create/sign the current authority graph and pass fail-closed intake/pre-V03 verification."
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

1. Deploy or independently reverify the exact reviewed V02 tooling and public trust identity on the WSL validation-ops surface; do not treat Git promotion alone as deployment evidence.
2. Rebuild/rebind production-like runtime and the stopped disposable LAB to exact dev22 source/package. Create fresh candidate-specific snapshots/seal and keep all 86 native cases NOT_RUN.
3. Build a fresh authority object graph for candidate `6f895394-e0b4-5434-bebc-79ee4e576282` with `controller_external=false`, all three containment barriers true, exact role pins/content hashes and a current <=24h suite.
4. Sign the exact envelope with the reviewed WSL-local Ed25519 key, run byte-aware staging preflight, then authoritative intake and pre-V03 fail-closed stage.
5. Advance to V03 only when the current V02 done-when succeeds. No dev21 authority object, READY artifact, native policy or native result is reusable as dev22 authority.

Local cryptographic approval remains same-trust-domain integrity/key-possession evidence, not independent external provenance.
