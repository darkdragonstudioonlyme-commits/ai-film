# Phase00 dev21 — external LAB authority handoff

This is the final **approval request/handoff**, not an approval record.

```yaml
HANDOFF_ID: LAB-EXTERNAL-AUTH-HANDOFF-P00-DEV21-001
STATUS: AWAITING_EXTERNAL_DECISION
RUN_ID: RUN-P00-VALIDATION-001
STEP_ID: V02_LAB_EXECUTION_AUTHORITY
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
RESTORE_PROBE: PASS
LAB_CURRENT_STATE: STOPPED_PENDING_AUTHORITY
NATIVE_EXECUTION_STARTED: false
```

## External decision required

The external owner/controller must independently inspect the protected Windows-side bundle whose public identity is the bundle hash above. Approval must not be inferred from this repository or from the operator asking to continue work.

For an **APPROVE** decision, the protected authority system must return immutable references that satisfy all of the following:

```yaml
DECISION: APPROVE
LAB_REGISTRATION_REF: <protected ref>
LAB_HOST_SAFE_ALIAS: <safe alias>
MACHINE_IDENTITY_PROTECTED_REF: <protected ref>
OPERATOR_IDENTITY_PROTECTED_REF: <protected ref>
OWNER_ATTESTATION_REF: <protected ref>
CONTROLLER_ATTESTATION_REF: <protected ref>
FIXTURE_SET_REF: <protected ref>
MANAGEMENT_ISOLATION_RECOVERY_REF: <protected ref>
LAB_TEST_PLAN_APPROVAL_REF: <protected ref>
LAB_ACCEPTANCE_SUITE_REF: <protected ref>
SUITE_ISSUED_AT_UTC: <timestamp>
SUITE_EXPIRES_AT_UTC: <timestamp; issued <= expires; window <= 24h>
```

The protected registration must have `execution_class=LAB`, `controller_external=true`, `disposable=true`, `no_real_credentials=true`, `no_production_mappings=true`, `withdrawn=false`, exact host/operator scope, and bind this candidate. The approved suite must be schema 1, `source_kind=LAB`, `approved=true`, `withdrawn=false`, and bind the exact build/test/contract identities plus all 86 reviewed case procedure digests/approved fixture and request refs.

For a **REJECT** decision, return a protected decision ref plus the rejected assertion/identity. Validation will remain blocked or route a validation-preparation failure; it must not weaken the reviewed LAB predicates.

## Consumer rule

The VALIDATION consumer must independently retrieve and verify the protected references. Only a successful verification may produce `LAB_EXECUTION_AUTHORITY_VERIFIED` and advance this same run from V02 to V03. No public document, operator statement, elapsed time, pending candidate, pending bundle, or local draft can substitute for that verification.

Do not place passwords, raw SID, MachineGuid, private management paths, signing secrets or other protected identity material in GitHub.