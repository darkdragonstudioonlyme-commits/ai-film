# NEXT WORK ITEM — activate dev22 validation run

```yaml
RUN_ID: RUN-P00-VALIDATION-002
WORKFLOW_ID: WF-P00-VALIDATION-ENTRY
LANE: VALIDATION
STATUS: READY_PENDING_VALIDATION_LANE_ACTIVATION
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
  REMOTE_SOURCE_REF: source/p00-dev22-local-authority-exact
  PREVIOUS_VALIDATION_RUN: RUN-P00-VALIDATION-001
  PREVIOUS_VALIDATION_BASE: 934659f535d81d9a4a07389531acc2b9c304fa6d
  LAST_VALIDATION_EVIDENCE_HEAD: cdb18e4b5a8f84ca0c89b9fe17a8a2d486234eaa
GOAL: "Activate candidate-specific dev22 validation, migrate V02 authority semantics to truthful local-operator same-WSL authority, and preserve all containment/native qualification boundaries."
STEPS:
  - V00_VALIDATION_LANE_ACTIVATION: PENDING
  - V01_CODE_REVIEW_GATE: COMPLETE
  - V02_LOCAL_OPERATOR_LAB_AUTHORITY: NOT_STARTED
  - V03_NATIVE_LAB_REGRESSION: NOT_STARTED
  - V04_QUALIFICATION_RECEIPT: NOT_STARTED
  - V05_SITE_VALIDATION: NOT_STARTED
  - V06_GATE_ASSESSMENT: NOT_STARTED
CURRENT_STEP: V00_VALIDATION_LANE_ACTIVATION
SUCCESS_OUTPUT: "RUN-P00-VALIDATION-002 canonically active on exact dev22 with dev21 run001 closed as superseded-before-native and local-authority migration plan bound."
ON_SUCCESS: RUN-P00-VALIDATION-002/V02_LOCAL_OPERATOR_LAB_AUTHORITY
ON_FAIL: VALIDATION_TRANSITION_FAILURE_ROUTE
ON_BLOCK: BLOCK-P00-VAL-DEV22-TRANSITION-001
EXIT_CONDITION: "Canonical validation lane binds exact dev22/run002; no native stage runs during candidate transition."
```

## Required sequence

1. Close dev21 `RUN-P00-VALIDATION-001` on the validation lane as `COMPLETE / SUPERSEDED_BY_DEV22_BEFORE_NATIVE_EXECUTION`; preserve all historical evidence.
2. Create and activate `RUN-P00-VALIDATION-002` with base identity `86bb64938a136e3f8d6cfd0266685a01cb832b77`. Do not reuse dev21 V02 authority receipts or candidate IDs.
3. Rebuild/rebind production-like runtime and stopped LAB to exact dev22 package/source; all 86 native cases remain NOT_RUN.
4. Replace external-authenticity wording/schema with truthful local-operator authority semantics. Keep content addressing, role pins, exact identity binding, <=24h suite, fail-closed watcher/pre-V03 and current-evaluation invalidation.
5. After tooling/schema design is independently reviewed/audited, generate the local Ed25519 private key inside WSL with mode `0600`; commit only the public trust anchor. Local signature proves integrity/key possession, not external independence.
6. Build/sign the exact dev22 approval object graph locally, run staging preflight, then authoritative intake. V03 begins only after the new V02 done-when succeeds.

No dev21 technical preparation is authority for dev22. No native execution is authorized by this transition document.
