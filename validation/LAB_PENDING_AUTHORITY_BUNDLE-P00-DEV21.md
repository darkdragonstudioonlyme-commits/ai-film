# Phase00 dev21 — pending external LAB authority bundle

```yaml
BUNDLE_ID: LAB-PENDING-AUTHORITY-BUNDLE-P00-DEV21-001
STATUS: SEALED_PENDING_EXTERNAL_APPROVAL
NATIVE_CONSUMABLE: false
APPROVED: false
EXTERNAL_APPROVAL_REF: null
CANDIDATE_ID: 336b12af-cada-4968-8083-8a5b41e479a2
PENDING_BUNDLE_INDEX_SHA256: fa38540df54df9ebb87929c43e9fe8fbcd09e290e93d8c5d53d7af991df8f615
PROTECTED_REGISTRATION_CANDIDATE_SHA256: 28ec95c3ecdd8ea7615843601c4657e25b503248fa2c93582cadb86c45488916
TECHNICAL_FACTS_SHA256: bca858e356faa2430a04ca2c8a069d02f3f4468927b130ef5a860fa844ecec79
AUTHORITY_DRAFT_SHA256: 746a2939d2b8983a952dcedf69ff173cc05f458ac7032a7001aff96c911450b5
SOURCE_COMMIT: 934659f535d81d9a4a07389531acc2b9c304fa6d
BUILD_DIGEST: a284645e9eb60661f27eba1ea436d7ff7bbe60d6cd3e312850f1b108d32b1c62
TEST_SET_DIGEST: c645f3d9f88fcb716f78fcff9cd9b4144b320dc4f0c8c7082346a5cfbe6d9383
CONTRACT_DIGEST: f259656c48ed24c15bd48da2bb040950ed94d8edcf1473cf6456b96578c933ee
INVENTORY_SHA256: 2ab5944390d33e1f26476d68c2c742247eaf313fa4f9351650308f5127dbf4a6
BASELINE_SNAPSHOT_SHA256: 0b91d4947754be40bdb4fd3d07c8eb452dde1b6bc160829923c8e0ef005dfffd
PRISTINE_SNAPSHOT_SHA256: 552d6cf0ec7158ebebc5385f7dfeb7b0b3216f3536d2915877bc9425ad02127d
PRISTINE_RESTORE_PROBE: PASS
APP_MANIFEST_SHA256: 2282f89da136ca54838379bdae8d9edc4b8e9c6a66770c732d8b3555eb4276f5
PRE_V03_INVENTORY_SHA256: 7ef70d5cb5134b3328dee96747a7a7d4b26c5b8e7f2dcaffa39aa96e0556851a
OWNER_ATTESTATION_REF: null
CONTROLLER_ATTESTATION_REF: null
FIXTURE_SET_REF: null
LAB_TEST_PLAN_APPROVAL_REF: null
LAB_ACCEPTANCE_SUITE_REF: null
NATIVE_EXECUTION_STARTED: false
```

The protected Windows-side pending store contains three byte-verified inputs: a non-consumable registration candidate, the safe technical-facts document, and the exact 86-case authority draft. Its index binds those hashes to exact dev21, the two external LAB snapshots, the restore proof and the pre-V03 inventory.

The protected registration candidate contains the raw operator SID only inside the ACL-protected Windows store; this public record exposes only its SHA-256. The pending bundle intentionally uses a non-production role, `approved=false` and `native_consumable=false`. It is not pinned into the Phase00 HKLM trust anchor and cannot satisfy `NativeStore` registration or `lab_acceptance_suite` selection.

External authority must review the protected bundle, independently bind/attest the raw host/operator identities and containment facts, approve protected fixture/plan refs, and issue the exact <=24h suite. Until then V02 remains `BLOCKED` and all 86 acceptance procedures remain `NOT_RUN`.