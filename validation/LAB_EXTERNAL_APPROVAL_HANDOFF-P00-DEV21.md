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
APPROVAL_ENVELOPE_MAPPING: validation/LAB_APPROVAL_ENVELOPE_MAPPING-P00-DEV21.md
AUTHORITY_PREFLIGHT_RECORD: validation/V02_AUTHORITY_PREFLIGHT-P00-DEV21.md
```

## External decision required

The external owner/controller must independently inspect the protected Windows-side bundle whose public identity is the bundle hash above. Approval must not be inferred from this repository or from the operator asking to continue work.

For an **APPROVE** decision, the external authority must establish the following protected evidence:

```yaml
DECISION: APPROVE
LAB_REGISTRATION_REF: <protected ref>
LAB_HOST_SAFE_ALIAS: <safe alias; bookkeeping only, not trusted instead of host_id>
MACHINE_IDENTITY_PROTECTED_REF: <protected authority provenance ref>
OPERATOR_IDENTITY_PROTECTED_REF: <protected authority provenance ref>
OWNER_ATTESTATION_REF: <protected ref>
CONTROLLER_ATTESTATION_REF: <protected ref>
FIXTURE_SET_REF: <protected ref>
MANAGEMENT_ISOLATION_RECOVERY_REF: <protected ref>
LAB_TEST_PLAN_APPROVAL_REF: <protected ref>
LAB_ACCEPTANCE_SUITE_REF: <protected ref>
SUITE_ISSUED_AT_UTC: <lab_acceptance_suite.issued_at>
SUITE_EXPIRES_AT_UTC: <lab_acceptance_suite.expires_at; issued <= expires; window <= 24h>
```

The exact packaging contract for `approval-envelope.json`, object roles and `role_pins` is `validation/LAB_APPROVAL_ENVELOPE_MAPPING-P00-DEV21.md`. The safe alias, protected provenance refs and suite timestamps are evidence/audit concepts; authority is bound by the protected registration/suite objects rather than duplicated top-level summaries.

The protected registration must have `execution_class=LAB`, `controller_external=true`, `disposable=true`, `no_real_credentials=true`, `no_production_mappings=true`, `withdrawn=false`, exact host/operator scope, and bind this candidate. The approved suite must be schema 1, `source_kind=LAB`, `approved=true`, `withdrawn=false`, and bind the exact build/test/contract identities plus all 86 reviewed case procedure digests/approved fixture and request refs.

`role_pins` must cover all documents used by pure authorization, including exact registration/design/code, approved `lab_plan`, exact `lab_acceptance_suite`, every execution plan, every native fixture spec, every per-plan approval object, and any additional plan-referenced role such as payload. A correct object that is not pinned remains untrusted and cannot advance V02.

## Optional read-only staging preflight

Before moving a proposed package into the protected authoritative inbox, the external owner/controller may lint a staging directory using:

```bash
/home/dragon/ai-film-dev/validation-ops/v02-authority-preflight.py --inbox /path/to/staging --json
```

This wrapper executes the exact V02 validator semantics and verifies that staging metadata is unchanged before/after. `READY_FOR_INTAKE` means the package satisfies the current validator when read from staging; it **does not** approve the package, create the authoritative READY flag, install trust or advance V02. `MISSING` and `INVALID` return the exact normalized failure reason so the external owner can correct/reissue the package without operator-side edits to protected objects.

For a **REJECT** decision, return a protected decision ref plus the rejected assertion/identity. Validation will remain blocked or route a validation-preparation failure; it must not weaken the reviewed LAB predicates.

## External authenticity prerequisite

Forensic review found that the local approved inbox is writable by the current operator, so content-addressed refs alone cannot prove external authorship. Before any APPROVE package can be consumable, the external owner/controller must first establish an **Ed25519 public-key identity out-of-band**:

```yaml
EXTERNAL_AUTHORITY_KEY_ID: <stable non-secret key id>
EXTERNAL_AUTHORITY_PUBLIC_KEY_B64: <raw 32-byte Ed25519 public key, base64>
EXTERNAL_AUTHORITY_PUBLIC_KEY_SHA256: <sha256 of raw public-key bytes>
EXTERNAL_AUTHORITY_KEY_PROVENANCE_REF: <independently verifiable protected/out-of-band provenance ref>
```

The private key must never be placed on this host or in GitHub. Key activation is a separate reviewed trust-anchor update; the current anchor remains `PENDING_EXTERNAL_KEY`. After activation, the external authority signs the **exact raw bytes** of `approval-envelope.json` and supplies `approval-envelope.sig.json` containing schema 1, `algorithm=ED25519`, the activated `key_id`, exact payload SHA-256 and the detached signature in base64.

An unsigned envelope, a locally substituted public key, trust-config drift, key-id mismatch, payload tamper or invalid signature remains BLOCKED before any protected object is consumed.

## Consumer rule

The VALIDATION consumer must independently retrieve and verify the protected references. Only a successful verification may produce `LAB_EXECUTION_AUTHORITY_VERIFIED` and advance this same run from V02 to V03. No public document, operator statement, elapsed time, pending candidate, pending bundle, preflight result or local draft can substitute for that verification.

Do not place passwords, raw SID, MachineGuid, private management paths, signing secrets or other protected identity material in GitHub.
