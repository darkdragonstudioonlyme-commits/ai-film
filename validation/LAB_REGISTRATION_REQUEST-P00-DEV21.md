# External LAB Registration / Authority Request — dev21

This public control-plane record is a **request**, not an approval. Sensitive/raw host identity, SID, credentials, private fixture paths or management secrets must remain in the protected external authority store; record only safe aliases and immutable protected refs/digests here.

```yaml
REQUEST_ID: LAB-AUTH-REQUEST-P00-DEV21-001
BLOCK_ID: BLOCK-P00-VAL-LAB-AUTH-001
STATUS: TECHNICAL_LAB_READY_AWAITING_EXTERNAL_AUTHORITY
TARGET_VERSION: 0.1.0.dev21
SOURCE_COMMIT: 934659f535d81d9a4a07389531acc2b9c304fa6d
PACKAGE_SHA256: f6ee158a318614f8bbef28be7af82549e0a268425da28147a2fa7b14c7b3d3e3
BUILD_DIGEST: a284645e9eb60661f27eba1ea436d7ff7bbe60d6cd3e312850f1b108d32b1c62
TEST_SET_DIGEST: c645f3d9f88fcb716f78fcff9cd9b4144b320dc4f0c8c7082346a5cfbe6d9383
CONTRACT_DIGEST: f259656c48ed24c15bd48da2bb040950ed94d8edcf1473cf6456b96578c933ee
INVENTORY_SHA256: 2ab5944390d33e1f26476d68c2c742247eaf313fa4f9351650308f5127dbf4a6
CODE_REVIEW_RECORD: reviews/CODE-REVIEW-P00-001_DEV21_DELTA.md

TECHNICAL_CANDIDATE:
  RECORD: validation/LAB_CANDIDATE-P00-DEV21.md
  CANDIDATE_ID: 336b12af-cada-4968-8083-8a5b41e479a2
  TECHNICAL_FACTS_SHA256: bca858e356faa2430a04ca2c8a069d02f3f4468927b130ef5a860fa844ecec79
  DISTRO: AI-FILM-P00-LAB
  CURRENT_DISTRO_STATE: STOPPED_PENDING_AUTHORITY
  WSL_VERSION: 2
  OS: Ubuntu 24.04.5 LTS
  MACHINE_IDENTITY_SHA256: 0705fb633dc0155a9f501e007e6ede7bcb85c17491f7ebcbe183391051bfecf6
  OPERATOR_SID_SHA256: 8d4b658f3bc550b3b867adfc19c85b42a754899fec6fe19f323db56b3aed5026
  BASELINE_SNAPSHOT_SHA256: 0b91d4947754be40bdb4fd3d07c8eb452dde1b6bc160829923c8e0ef005dfffd
  PRISTINE_DEV21_SNAPSHOT_SHA256: 552d6cf0ec7158ebebc5385f7dfeb7b0b3216f3536d2915877bc9425ad02127d
  SNAPSHOT_RESTORE_PROBE: PASS
  NO_REAL_CREDENTIALS_TECHNICALLY_VERIFIED: true
  NO_PRODUCTION_MAPPINGS_TECHNICALLY_VERIFIED: true
  WINDOWS_AUTOMOUNT_ENABLED: false
  NATIVE_EXECUTION_STARTED: false
  APPROVED: false
  EXTERNAL_AUTHORITY_ATTESTED: false

PENDING_PROTECTED_BUNDLE:
  RECORD: validation/LAB_PENDING_AUTHORITY_BUNDLE-P00-DEV21.md
  INDEX_SHA256: fa38540df54df9ebb87929c43e9fe8fbcd09e290e93d8c5d53d7af991df8f615
  REGISTRATION_CANDIDATE_SHA256: 28ec95c3ecdd8ea7615843601c4657e25b503248fa2c93582cadb86c45488916
  TECHNICAL_FACTS_SHA256: bca858e356faa2430a04ca2c8a069d02f3f4468927b130ef5a860fa844ecec79
  AUTHORITY_DRAFT_SHA256: 746a2939d2b8983a952dcedf69ff173cc05f458ac7032a7001aff96c911450b5
  WINDOWS_STORE_ACL_PROTECTED: true
  WINDOWS_STORE_ACL_RULE_COUNT: 2
  WINDOWS_STORE_FILE_COUNT: 4
  NATIVE_CONSUMABLE: false
  APPROVED: false
  EXTERNAL_APPROVAL_REF: null

EXTERNAL_AUTHORITY_REQUIRED:
  LAB_REGISTRATION_REF: PENDING_EXTERNAL
  LAB_HOST_SAFE_ALIAS: PENDING_EXTERNAL
  MACHINE_IDENTITY_PROTECTED_REF: PENDING_EXTERNAL
  OPERATOR_IDENTITY_PROTECTED_REF: PENDING_EXTERNAL
  OWNER_ATTESTATION_REF: PENDING_EXTERNAL
  CONTROLLER_ATTESTATION_REF: PENDING_EXTERNAL
  FIXTURE_SET_REF: PENDING_EXTERNAL
  MANAGEMENT_ISOLATION_RECOVERY_REF: PENDING_EXTERNAL
  LAB_TEST_PLAN_APPROVAL_REF: PENDING_EXTERNAL
  LAB_ACCEPTANCE_SUITE_REF: PENDING_EXTERNAL

REQUIRED_REGISTRATION_ASSERTIONS:
  execution_class: LAB
  controller_external: true
  disposable: true
  no_real_credentials: true
  no_production_mappings: true
  withdrawn: false

REQUIRED_SUITE_BINDING:
  schema_version: 1
  approved: true
  withdrawn: false
  source_kind: LAB
  build_digest: a284645e9eb60661f27eba1ea436d7ff7bbe60d6cd3e312850f1b108d32b1c62
  test_set_digest: c645f3d9f88fcb716f78fcff9cd9b4144b320dc4f0c8c7082346a5cfbe6d9383
  contract_digest: f259656c48ed24c15bd48da2bb040950ed94d8edcf1473cf6456b96578c933ee
  case_count: 86
  validity_max_hours: 24
```

## V02 closure check

The disposable LAB environment, exact dev21 deployment, isolation settings, baseline/pristine snapshots, independent restore probe and a protected pending authority bundle are now technically prepared. The LAB itself is stopped pending authority. These artifacts materially reduce V02 preparation work but **do not constitute authority**.

The validation consumer closes V02 only after it can independently verify an externally approved protected registration and suite/test-plan authority against the exact dev21 identities above, including host/operator scope, all containment assertions, exact case/procedure bindings, fixture refs and validity interval. The existing pending bundle is deliberately non-consumable and unapproved.

A user statement such as “use this PC as lab”, a changed CLI flag, a repository file authored by the build itself, or elapsed time is **not** sufficient authority. External owner/controller registration and approved suite/test-plan authority remain required before any native LAB stage.