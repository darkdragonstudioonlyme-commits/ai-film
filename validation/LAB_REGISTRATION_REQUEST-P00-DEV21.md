# External LAB Registration / Authority Request — dev21

This public control-plane record is a **request**, not an approval. Sensitive/raw host identity, SID, credentials, private fixture paths or management secrets must remain in the protected external authority store; record only safe aliases and immutable protected refs/digests here.

```yaml
REQUEST_ID: LAB-AUTH-REQUEST-P00-DEV21-001
BLOCK_ID: BLOCK-P00-VAL-LAB-AUTH-001
STATUS: BLOCKED_AWAITING_EXTERNAL_RECORD
TARGET_VERSION: 0.1.0.dev21
SOURCE_COMMIT: 934659f535d81d9a4a07389531acc2b9c304fa6d
PACKAGE_SHA256: f6ee158a318614f8bbef28be7af82549e0a268425da28147a2fa7b14c7b3d3e3
BUILD_DIGEST: a284645e9eb60661f27eba1ea436d7ff7bbe60d6cd3e312850f1b108d32b1c62
TEST_SET_DIGEST: c645f3d9f88fcb716f78fcff9cd9b4144b320dc4f0c8c7082346a5cfbe6d9383
CONTRACT_DIGEST: f259656c48ed24c15bd48da2bb040950ed94d8edcf1473cf6456b96578c933ee
INVENTORY_SHA256: 2ab5944390d33e1f26476d68c2c742247eaf313fa4f9351650308f5127dbf4a6
CODE_REVIEW_RECORD: reviews/CODE-REVIEW-P00-001_DEV21_DELTA.md

EXTERNAL_AUTHORITY_REQUIRED:
  LAB_REGISTRATION_REF: PENDING_EXTERNAL
  LAB_HOST_SAFE_ALIAS: PENDING_EXTERNAL
  MACHINE_IDENTITY_PROTECTED_REF: PENDING_EXTERNAL
  OPERATOR_IDENTITY_PROTECTED_REF: PENDING_EXTERNAL
  OWNER_ATTESTATION_REF: PENDING_EXTERNAL
  CONTROLLER_ATTESTATION_REF: PENDING_EXTERNAL
  FIXTURE_SET_REF: PENDING_EXTERNAL
  SNAPSHOT_BASELINE_REF: PENDING_EXTERNAL
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

The validation consumer closes V02 only after it can independently verify the protected registration and suite/test-plan authority against the exact dev21 identities above, including host/operator scope, all containment assertions, exact case/procedure bindings, fixture/snapshot refs and validity interval.

A user statement such as “use this PC as lab”, a changed CLI flag, a repository file authored by the build itself, or elapsed time is **not** sufficient authority. If a real disposable LAB is designated, return its safe registration/approval refs; do not paste credentials or sensitive raw identity into this public repository.