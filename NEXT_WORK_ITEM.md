# NEXT WORK ITEM — resume Phase00 validation authority run

```yaml
RUN_ID: RUN-P00-VALIDATION-001
WORKFLOW_ID: WF-P00-VALIDATION-ENTRY
LANE: VALIDATION
STATUS: BLOCKED_EXTERNAL_AUTHENTICITY_AND_AUTHORITY
MODE: VALIDATION
PHASE: "00 — Host / WSL"
WORK_ITEM: M-P00-VALIDATION
INPUT_IDENTITY:
  ACCEPTED_VERSION: 0.1.0.dev21
  SOURCE_COMMIT: 934659f535d81d9a4a07389531acc2b9c304fa6d
  PACKAGE_SHA256: f6ee158a318614f8bbef28be7af82549e0a268425da28147a2fa7b14c7b3d3e3
  SOURCE_DIGEST: a284645e9eb60661f27eba1ea436d7ff7bbe60d6cd3e312850f1b108d32b1c62
  TEST_DIGEST: c645f3d9f88fcb716f78fcff9cd9b4144b320dc4f0c8c7082346a5cfbe6d9383
  CONTRACT_DIGEST: f259656c48ed24c15bd48da2bb040950ed94d8edcf1473cf6456b96578c933ee
  INVENTORY_SHA256: 2ab5944390d33e1f26476d68c2c742247eaf313fa4f9351650308f5127dbf4a6
  CODE_REVIEW_RECORD: reviews/CODE-REVIEW-P00-001_DEV21_DELTA.md
  CODE_REVIEW_PASS: true
  VALIDATION_LANE: lane/validation-p00
  VALIDATION_EVIDENCE_HEAD: 9a3854d80b7e4c35c5d2ec933709280ce0baa7fa
  RUN_RECORD: workflow-runs/RUN-P00-VALIDATION-001.md
  VALIDATION_PLAN: validation/VALIDATION_PLAN-P00-DEV21.md
  AUTHORITY_REQUEST: validation/LAB_REGISTRATION_REQUEST-P00-DEV21.md
  LAB_CANDIDATE: validation/LAB_CANDIDATE-P00-DEV21.md
  LAB_AUTHORITY_DRAFT: validation/LAB_AUTHORITY_DRAFT-P00-DEV21.md
  LAB_PENDING_AUTHORITY_BUNDLE: validation/LAB_PENDING_AUTHORITY_BUNDLE-P00-DEV21.md
  LAB_EXTERNAL_APPROVAL_HANDOFF: validation/LAB_EXTERNAL_APPROVAL_HANDOFF-P00-DEV21.md
  V02_EXTERNAL_AUTHENTICITY_HARDENING: validation/V02_EXTERNAL_AUTHENTICITY_HARDENING-P00-DEV21.md
  V02_EXTERNAL_AUTHENTICITY_DEPLOYMENT: validation/V02_EXTERNAL_AUTHENTICITY_DEPLOYMENT-P00-DEV21.md
  V02_DEPLOYMENT_REVIEW: reviews/VALIDATION-V02-AUTHENTICITY-DEPLOYMENT-REVIEW-001_PASS.md
  EXTERNAL_TRUST_ALGORITHM: ED25519
  EXTERNAL_TRUST_CONFIG_STATUS: PENDING_EXTERNAL_KEY
  APPROVAL_ENVELOPE_STATUS: MISSING
  READY_TO_ADVANCE: false
  LAB_CANDIDATE_ID: 336b12af-cada-4968-8083-8a5b41e479a2
  LAB_PENDING_BUNDLE_INDEX_SHA256: fa38540df54df9ebb87929c43e9fe8fbcd09e290e93d8c5d53d7af991df8f615
  LAB_PROTECTED_REGISTRATION_CANDIDATE_SHA256: 28ec95c3ecdd8ea7615843601c4657e25b503248fa2c93582cadb86c45488916
  LAB_BASELINE_SNAPSHOT_SHA256: 0b91d4947754be40bdb4fd3d07c8eb452dde1b6bc160829923c8e0ef005dfffd
  LAB_PRISTINE_SNAPSHOT_SHA256: 552d6cf0ec7158ebebc5385f7dfeb7b0b3216f3536d2915877bc9425ad02127d
  LAB_SNAPSHOT_RESTORE_PROBE: PASS
  LAB_CURRENT_STATE: STOPPED_PENDING_AUTHORITY
GOAL: "Close V02 only after independently established external Ed25519 public-key provenance is separately reviewed/activated and the external authority signs the exact approval envelope binding the protected registration/attestation/fixture/plan/suite graph for the prepared LAB; then execute the mandatory 86-case reviewed LAB inventory before qualification or SITE activity."
STEPS:
  - V01_CODE_REVIEW_GATE: COMPLETE
  - V02_LAB_EXECUTION_AUTHORITY: BLOCKED_EXTERNAL_AUTHENTICITY_AND_AUTHORITY
  - V03_NATIVE_LAB_REGRESSION: NOT_STARTED
  - V04_QUALIFICATION_RECEIPT: NOT_STARTED
  - V05_SITE_VALIDATION: NOT_STARTED
  - V06_GATE_ASSESSMENT: NOT_STARTED
CURRENT_STEP: V02_LAB_EXECUTION_AUTHORITY
SUCCESS_OUTPUT: "Verified independently rooted external Ed25519 signature over the exact approval envelope plus protected LAB registration/owner-controller attestation, fixture/plan refs and approved <=24h exact-dev21 lab_acceptance_suite bound to candidate 336b12af-cada-4968-8083-8a5b41e479a2."
ON_SUCCESS: WF-P00-VALIDATION-LAB
ON_FAIL: VALIDATION_FAILURE_ROUTE
ON_BLOCK: BLOCK-P00-VAL-LAB-AUTH-001
EXIT_CONDITION: "External key provenance is independently verified and separately activated; the exact signed authority graph passes V02 intake; no native stage has run before this condition."
```

## Preparation completed

A real disposable LAB candidate is already installed and prepared. `AI-FILM-P00-LAB` is fresh Ubuntu 24.04.5 WSL2 rather than a clone of development, has a dedicated password-locked user, Windows-drive automount disabled, no appended Windows PATH, no copied real credentials and no production storage mapping. Exact dev21 is deployed read-only and byte-verified; source/test/contract identities reproduce exactly. The LAB is currently stopped pending authority.

The baseline and pristine-dev21 LAB snapshots exist outside the guest and the pristine snapshot has been independently restored into a temporary probe distro, exact app/inventory verified, then the probe unregistered. Pre-V03 inventory remains 86 `NOT_RUN`, zero native parent cases, no qualification, `HOST_READY=false`.

An authority draft generated from exact reviewed `PROCEDURES` covers 86 cases (85 native fixture templates + 1 document case), SHA-256 `746a2939d2b8983a952dcedf69ff173cc05f458ac7032a7001aff96c911450b5`, self-check PASS and `approved=false`.

The Windows-side protected pending store is ACL-protected (inheritance protected, two access rules) and contains exactly four byte-verified files. Its non-consumable pending index SHA-256 is `fa38540df54df9ebb87929c43e9fe8fbcd09e290e93d8c5d53d7af991df8f615`; it is `approved=false`, `native_consumable=false`, and all external approval refs remain null.

## Block record

```yaml
BLOCK_ID: BLOCK-P00-VAL-LAB-AUTH-001
WORKFLOW_ID: WF-P00-VALIDATION-ENTRY
OWNER_LANE: VALIDATION
REASON: "Technical LAB infrastructure and V02 authenticity enforcement are complete. Remaining V02 requirements are independently established external Ed25519 public-key provenance, separate reviewed trust-anchor activation, then an externally signed exact approval envelope and protected authority graph."
TECHNICAL_LAB_ENVIRONMENT_MISSING: false
PENDING_AUTHORITY_BUNDLE_READY: true
EXTERNAL_APPROVAL_HANDOFF: "lane/validation-p00:validation/LAB_EXTERNAL_APPROVAL_HANDOFF-P00-DEV21.md"
EVIDENCE:
  - "lane/validation-p00:validation/LAB_CANDIDATE-P00-DEV21.md"
  - "lane/validation-p00:validation/LAB_REGISTRATION_REQUEST-P00-DEV21.md"
  - "lane/validation-p00:validation/LAB_AUTHORITY_DRAFT-P00-DEV21.md"
  - "lane/validation-p00:validation/LAB_PENDING_AUTHORITY_BUNDLE-P00-DEV21.md"
  - "accepted dev21 contracts/DESIGN_REVIEW_APPROVAL_V2.json"
USER_ACTION_REQUIRED: true
RETURN_TO: RUN-P00-VALIDATION-001/V02_LAB_EXECUTION_AUTHORITY
STATUS: OPEN
```

## Minimum external action

Do **not** create another LAB and do not start the stopped LAB for native execution. The next external action is **not** to write an `APPROVE` file into the local inbox. The external owner/controller must first establish an Ed25519 public-key identity and protected/out-of-band provenance. That public key is then activated only through a separate reviewed trust-anchor transaction; the private key never belongs on this host or in GitHub.

After activation, the external authority reviews the sealed bundle `fa38540df...`, returns the protected refs required by `LAB_EXTERNAL_APPROVAL_HANDOFF-P00-DEV21.md`, and signs the **exact raw bytes** of `approval-envelope.json`. Only a signature under the activated external key plus the fully verified hash-addressed authority graph may advance this same run V02 → V03. Credentials, raw SID/MachineGuid and private signing material stay out of GitHub.