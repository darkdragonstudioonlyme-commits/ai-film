# Phase00 dev21 — external authority envelope/object mapping

This record clarifies packaging only. It does **not** approve LAB execution, change the reviewed predicates, or replace `LAB_EXTERNAL_APPROVAL_HANDOFF-P00-DEV21.md`.

```yaml
MAPPING_ID: LAB-APPROVAL-ENVELOPE-MAPPING-P00-DEV21-001
RUN_ID: RUN-P00-VALIDATION-001
STEP_ID: V02_LAB_EXECUTION_AUTHORITY
CANDIDATE_ID: 336b12af-cada-4968-8083-8a5b41e479a2
PENDING_BUNDLE_INDEX_SHA256: fa38540df54df9ebb87929c43e9fe8fbcd09e290e93d8c5d53d7af991df8f615
VALIDATOR: /home/dragon/ai-film-dev/validation-ops/v02-authority-intake.py
STATUS: PACKAGING_CLARIFICATION_ONLY
NATIVE_EXECUTION_STARTED: false
```

## `approval-envelope.json` direct contract

The protected inbox consumer reads these top-level fields directly:

```yaml
schema_version: 1
kind: P00_LAB_EXTERNAL_AUTHORITY_INTAKE
decision: APPROVE
approved_by_external_authority: true
candidate_id: 336b12af-cada-4968-8083-8a5b41e479a2
pending_bundle_index_sha256: fa38540df54df9ebb87929c43e9fe8fbcd09e290e93d8c5d53d7af991df8f615
source_commit: 934659f535d81d9a4a07389531acc2b9c304fa6d
build_digest: a284645e9eb60661f27eba1ea436d7ff7bbe60d6cd3e312850f1b108d32b1c62
test_set_digest: c645f3d9f88fcb716f78fcff9cd9b4144b320dc4f0c8c7082346a5cfbe6d9383
contract_digest: f259656c48ed24c15bd48da2bb040950ed94d8edcf1473cf6456b96578c933ee
lab_registration_ref: <sha256 object ref>
owner_attestation_ref: <sha256 object ref>
controller_attestation_ref: <sha256 object ref>
fixture_set_ref: <sha256 object ref>
management_isolation_recovery_ref: <sha256 object ref>
lab_test_plan_approval_ref: <sha256 object ref>
lab_acceptance_suite_ref: <sha256 object ref>
role_pins: <role -> non-empty list of sha256 object refs>
```

Each ref resolves to `objects/<sha256>.json`; the file bytes must hash to the ref and the JSON `role` must match the role expected by the validator.

## Evidence carried inside protected objects

The handoff's safe alias / identity / time fields are evidence requirements, not additional trusted top-level envelope inputs:

- `LAB_HOST_SAFE_ALIAS` is external bookkeeping only. The validator trusts the exact `registration.host_id`, not an alias.
- machine identity provenance remains in the protected authority system; the validator binds the resulting exact host scope through `registration.host_id`.
- operator identity provenance remains protected; the validator requires the raw execution SID to be present in `registration.operator_sids` and verifies its domain-separated digest against the prepared candidate.
- `SUITE_ISSUED_AT_UTC` / `SUITE_EXPIRES_AT_UTC` are the `issued_at` / `expires_at` fields of the `lab_acceptance_suite` object. The validator requires current time within that interval and a maximum window of 24 hours.

The external system may retain safe aliases/protected identity refs as its own audit metadata, but duplicating them in the envelope does not substitute for the registration/suite assertions above.

## Required `role_pins` coverage

`role_pins` is part of the trust input, not a convenience index. At minimum it must make every document consumed by pure authorization trusted:

- `registration`: exactly the approved `lab_registration_ref`;
- `design`: exactly one reviewed design authority object for the accepted contract;
- `code`: exactly one reviewed code authority object bound to exact dev21 build/test/contract identities;
- `lab_plan`: include `lab_test_plan_approval_ref`;
- `lab_acceptance_suite`: include `lab_acceptance_suite_ref`;
- `execution_plan`: include every `plan_ref` used by the 85 native-case request rows;
- `lab_case_fixture_spec`: include every native case `fixture_spec_ref`;
- `approval`: include every per-plan `approval_ref` referenced by an execution plan;
- any additional role referenced by an execution plan (for example `payload`) must include the exact referenced object.

`owner_attestation`, `controller_attestation`, `lab_fixture_set`, and `management_isolation_recovery` are loaded and verified directly by the intake validator; they remain mandatory envelope refs even though they are not the documents passed to `authority.authorize()`.

## Fail-closed rule

Missing, unpinned, wrongly scoped, expired, withdrawn, hash-mismatched, wrong-role, wrong-procedure, wrong-route, wrong-fixture, or wrong-build authority remains `BLOCKED`. This mapping must never be used to relax validator checks or manufacture external approval.