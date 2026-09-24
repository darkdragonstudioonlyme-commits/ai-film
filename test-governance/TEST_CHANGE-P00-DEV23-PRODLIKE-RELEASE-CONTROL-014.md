# TEST_CHANGE — dev23 prodlike release-control producer/consumer compatibility 014

~~~yaml
TEST_CHANGE_ID: TEST_CHANGE-P00-DEV23-PRODLIKE-RELEASE-CONTROL-014
RUN_ID: RUN-P00-VALIDATION-002
WORK_ITEM: TEST-DESIGN-P00-DEV23-PRODLIKE-RELEASE-CONTROL-014
BASE_VALIDATION_COMMIT: 4850b4d2930d6f2eaad8065f306314ea8a352867
ORIGINAL_PRE_FIX_BASE: 9f341bea77d9e8e0df081f00a69315116822801f
REVISION: R2
PRIOR_TEST_REVIEW_COMMIT: 4850b4d2930d6f2eaad8065f306314ea8a352867
PRODUCT_SOURCE_COMMIT: 2f7da39984a7a582c7cf2a84f743299fc7fe735f
CANDIDATE_ID: acf18da3-4969-451c-8a4b-a7e46ad89c98
CANDIDATE_BINDING_SHA256: ed7823332afa96c3335f3353518ca0330b9e3c687b0022926c776319611c1890
RECONCILIATION_RECEIPT_REVIEW: reviews/CODE-REVIEW-P00-DEV23-PRODLIKE-ATTEMPT5-RECONCILIATION-RECEIPT-002.md
SOURCE_DEBT: RELEASE_CONTROL_V1_V2_PRODUCER_CONSUMER_MISMATCH
ORACLE_CHANGED: false
EXPECTED_BUSINESS_BEHAVIOR_CHANGED: false
NATIVE_EXECUTION_AUTHORIZED: false
AUTHORITY_SIGNING_AUTHORIZED: false
PRODLIKE_DEPLOYMENT_AUTHORIZED: false
LAB_MUTATION_AUTHORIZED: false
STATUS: PENDING_INDEPENDENT_TEST_REVIEW_R2
~~~

## Purpose

Transaction005 exposed a real producer/consumer contract failure after the corrected dev23 release had already switched `current`: candidate-generic `build_prodlike_control_bundle-v2.py` emitted a V2 release-control object, while the deployed `scripts/control_common.py` inside `prodlike_control_templates_v2.json` still enforced the historical dev22 V1 exact schema. Runtime-health therefore failed with `RuntimeError:release-control-schema`; reconciliation002 subsequently restored and independently verified exact dev22.

This TEST_CHANGE defines the smallest fail-closed correction. It does not authorize deployment or host mutation.

## Exact pre-fix evidence

At base validation commit `9f341bea77d9e8e0df081f00a69315116822801f`:

- producer SHA256 `d14320d8b11298d25cb3f9ecd8e5022c2eef842e9db14345da899d18012ec994` — `validation/tooling/build_prodlike_control_bundle-v2.py`;
- verifier SHA256 `3ed5953a601f099c2c6056354e48554e7f04ed5347ffbf4c7d319d8a7f845df8` — `validation/tooling/verify_prodlike_control_bundle-v2.py`;
- neutral-template SHA256 `4d46440639472de5207f76e08ead56a0675417f9659c6eb77755dca3d9975110` — `validation/tooling/prodlike_control_templates_v2.json`;
- control-bundle test SHA256 `5d84317e80272cbb07e546fb23413ac7f0f3d7b413383000a289aac114850572`;
- V2 template `scripts/control_common.py` is byte-identical to historical dev22 consumer SHA256 `edb692e833c084ea3b5dc9b0a812e518f5057deb5b9db349347a9932ad61feff`;
- failed transaction005 release-control evidence SHA256 `94b72e78a291265aad54e8da1bde0ae88b05e365b538b3fe951ee13dcebd852c`.

The historical consumer requires 25 exact keys. The V2 producer emitted 23 keys. It omitted operational fields still referenced by V2 scripts: `app_file_count`, `offhost_export_name`, `package_name`, `wheel_name`; and it added candidate-binding fields `candidate_id`, `candidate_binding_sha256`. This is not a host-only accident.

## Contract direction

Do **not** downgrade the candidate-generic producer to the historical V1 contract and do not modify historical dev22 bytes.

The dev23 successor contract is exact V2 and must preserve both:

1. candidate-bound identity (`candidate_id`, `candidate_binding_sha256`), and
2. all operational fields consumed by the V2 script set.

The exact V2 release-control key set after correction is 27 keys:

```text
schema_version
kind
release_name
candidate_id
candidate_binding_sha256
implementation_version
source_commit
source_digest
test_digest
contract_digest
package_name
package_sha256
wheel_name
wheel_sha256
app_file_count
runtime_root
rebuild_root
host_backup_root
offhost_export_root
offhost_export_name
authority_evidence_root
authority_model
verify_service
verify_timer
expected_timer_count
native_authority
native_execution_started
```

`kind` remains `AIFILM_P00_RELEASE_CONTROL_V2`; `schema_version` remains `1`.

## Authorized implementation scope

MODIFY only:

- `validation/tooling/build_prodlike_control_bundle-v2.py`
- `validation/tooling/verify_prodlike_control_bundle-v2.py`
- `validation/tooling/prodlike_control_templates_v2.json`
- `validation/tooling/tests/test_prodlike_control_bundle_v2.py`
- `validation/tooling/tests/test_prodlike_deployment_transaction_v2.py` — fixture-only update described below; no transaction semantics may change

Within `prodlike_control_templates_v2.json`, only the `scripts/control_common.py` template row may change. The other 62 template rows must remain byte/field-identical to the base.

Within `validation/tooling/tests/test_prodlike_deployment_transaction_v2.py`, only the synthetic candidate runtime-manifest fixture constructed in `ProdlikeTxnTests.setUp()` may change for this correction. It must add the three fields now required by the strict V2 producer contract: `package_name`, `wheel_name`, and positive integer `app_file_count`. No FakeRunner behavior, authorization logic, transaction assertions, command sets, fault-injection cases, user-bus checks, or deployment semantics may change.

Everything else remains byte-identical, including:

- `validation/tooling/build_prodlike_release-v2.py` and its reviewed verify-runtime correction 013;
- `validation/tooling/build_prodlike_rebuild_set-v2.py`;
- `validation/tooling/verify_prodlike_user_systemd-v2.py`;
- `validation/tooling/deployment_transaction_common.py`;
- `validation/tooling/deploy_prodlike_candidate-v2.py`;
- all reconciliation executors/support artifacts;
- `validation/prodlike-dev22/**`, including historical V1 `control_common.py` and `release-control.json`;
- all historical dev22 tooling/tests/evidence;
- accepted product source/contracts and private/local authority material.


## R2 implementation-scope correction after author precheck

The first reviewed four-file scope was proven insufficient by implementation evidence before any candidate was frozen or deployed. TV014 targeted tests passed 13/13, but the full predecessor regression stopped at all 22 `test_prodlike_deployment_transaction_v2.py` tests before their bodies executed because that predecessor fixture constructs a synthetic candidate runtime manifest without `package_name`, `wheel_name`, or `app_file_count`. The corrected producer properly rejects that manifest with `RUNTIME_PACKAGE_NAME`. Host before/after snapshots were identical; no deployment/native/LAB/signing/HKLM action occurred.

This is a **test-fixture constructibility gap**, not a reason to weaken the producer contract. The producer must continue requiring all three fields. R2 therefore expands the MODIFY allowlist by exactly one test file and only for its synthetic runtime-manifest fixture.

Required fixture values are deterministic test data, not live-host observations:

- `package_name`: safe basename derived for the synthetic candidate release (for example `AI-FILM-P00-dev23.tar.gz`);
- `wheel_name`: safe synthetic wheel basename consistent with the candidate implementation version;
- `app_file_count`: positive integer synthetic app count.

The fixture must continue deriving candidate ID/binding/version/source/digests/package SHA/wheel SHA from the same reviewed binding/profile as before. The new fields exist only so predecessor transaction tests can construct a V2 control bundle under the stricter producer precondition.

### R2 regression witness

After the fixture-only edit, author evidence must show:

1. the 13 TV014 tests remain PASS without relaxing any negative assertion;
2. all 22 predecessor prodlike transaction tests enter and complete their original test bodies rather than failing in `setUp()`;
3. current `test_prodlike_deployment_transaction_v2.py` differs from base only in the synthetic runtime-manifest fixture fields described above;
4. all other TV009/010/011/012/013 suites and 11 historical dev22 scripts remain PASS; and
5. host `current`, dev22, failed dev23, failed dev23-corrected and user-systemd snapshots remain byte-identical.

If the predecessor suite still requires any edit outside that fixture block, or producer strictness would need to be reduced, stop and return to TEST_DESIGN again.

## Required V2 producer behavior

`build_prodlike_control_bundle-v2.py` must continue taking the reviewed candidate binding plus exact V2 runtime manifest and neutral template set. It must:

- preserve current candidate ID/binding/source/build/test/contract/package/wheel identities;
- require runtime manifest `package_name`, `wheel_name`, and positive integer `app_file_count` and copy them exactly into release-control;
- derive `release_name` from the reviewed implementation version as today;
- derive `offhost_export_name` deterministically from `release_name` as `AI-FILM-P00-<RELEASE_NAME_UPPER>-OFFHOST-DR-EXPORT.zip`; no host observation or mutable workspace value may supply it;
- continue binding runtime/rebuild/backup/offhost/authority roots explicitly;
- continue `expected_timer_count=11`, `native_authority=false`, `native_execution_started=false`;
- emit exactly the 27-key V2 object above, with no additional permissive fields.

## Required V2 consumer behavior

The `scripts/control_common.py` row in `prodlike_control_templates_v2.json` must become a V2 consumer, not a copy of dev22 V1. Its `load_control(path=None)` must fail closed unless the object has exactly the 27-key V2 set and satisfies at least:

- `schema_version == 1` and `kind == AIFILM_P00_RELEASE_CONTROL_V2`;
- `release_name` matches `dev[0-9]+` and is consistent with `implementation_version` suffix;
- `source_commit` is 40 lowercase hex;
- `source_digest`, `test_digest`, `contract_digest`, `package_sha256`, `wheel_sha256`, and `candidate_binding_sha256` are 64 lowercase hex;
- `candidate_id` is a syntactically valid UUID string;
- `package_name`, `wheel_name`, and `offhost_export_name` are safe basenames, not absolute/traversal paths;
- `app_file_count` is a positive integer;
- `offhost_export_name` equals the deterministic release-name-derived filename;
- all five configured roots are absolute paths;
- `authority_model == LOCAL_OPERATOR_SAME_WSL_TRUST_DOMAIN`;
- `expected_timer_count == 11`; and
- `native_authority is false` and `native_execution_started is false`.

Historical dev22 V1 consumer semantics remain untouched.

## Required verifier behavior

`verify_prodlike_control_bundle-v2.py` must reject a bundle before deployment evidence can be accepted when the generated release-control violates the V2 contract. It must at minimum:

- require the exact 27-key set and V2 kind/schema;
- preserve exact candidate/profile identity checks already present;
- when a runtime manifest is supplied, require release-control `package_name`, `wheel_name`, and `app_file_count` to equal that manifest;
- require deterministic `offhost_export_name`; and
- continue all current source/deployed member/hash/mode/timer/candidate checks without live systemd.

The verifier must not execute native routes, mutate host state, or weaken existing candidate identity checks.

## Required tests

- `TV014-01` a successful bundle generated from a valid synthetic V2 runtime manifest is accepted by the **actual generated** `scripts/control_common.py::load_control()` when passed the generated `release-control.json`. This is the primary producer→consumer constructibility witness.
- `TV014-02` successful release-control has exactly the 27-key V2 set; candidate ID/binding and package/wheel/source/build/test/contract identities match the reviewed binding/runtime manifest.
- `TV014-03` `package_name`, `wheel_name`, and `app_file_count` are copied exactly from the runtime manifest; `offhost_export_name` is deterministically derived from `release_name`.
- `TV014-04` every static `CONTROL['field']` reference across all 63 V2 template rows is contained in the generated V2 release-control key set. Current operational consumers of `app_file_count`, `offhost_export_name`, `package_name`, and `wheel_name` therefore remain constructible.
- `TV014-05` generated V2 consumer rejects historical V1 kind, missing field, extra field, malformed UUID/hash/source commit, invalid release/version relation, unsafe names/paths, wrong deterministic export name, non-positive app count, wrong authority model/timer count, or native boundary bits set true.
- `TV014-06` bundle verifier rejects wrong V2 kind/schema/key set, candidate/binding drift, package/wheel/app-count drift against runtime manifest, deterministic export-name drift, and native boundary drift.
- `TV014-07` real generated consumer and verifier agree on the same valid V2 document; a document accepted by one but rejected by the other is a test failure.
- `TV014-08` within `prodlike_control_templates_v2.json`, the 62 rows other than `scripts/control_common.py` remain identical to base validation commit `9f341bea77d9e8e0df081f00a69315116822801f`.
- `TV014-09` historical dev22 `validation/prodlike-dev22/scripts/control_common.py` SHA256 remains `edb692e833c084ea3b5dc9b0a812e518f5057deb5b9db349347a9932ad61feff` and historical `release-control.json` SHA256 remains `2988b93eef37e9b18a14979902f6686f7fb2fb4bb9d1f0b34392ab01ac9c9803`.
- `TV014-10` corrected bundle/control tests retain TV010 source/deployed hash/mode/member/timer tests and full TV009/010/011/012/013 plus 11 historical dev22 regression coverage.
- `TV014-11` author/test paths use temporary/evidence roots only and prove current dev22, failed dev23, failed dev23-corrected and user-systemd host bytes are unchanged.
- `TV014-12` no author/test path creates deployment authorization, switches current, modifies failed evidence trees, mutates user-systemd/LAB, executes native routes, signs authority, writes HKLM, enters SITE, issues qualification, or marks HOST_READY.

## Planned constructibility evidence

After implementation, the test must construct one bundle from the real builder rather than hand-writing the control object:

1. build a synthetic valid V2 runtime manifest carrying the reviewed identity shape plus `package_name`, `wheel_name`, and `app_file_count`;
2. call the real `build_prodlike_control_bundle-v2.py::build()`;
3. dynamically import the generated, already-byte-produced `scripts/control_common.py` from that bundle without using the host deployed consumer;
4. call its pure `load_control(generated_release_control_path)` and require success;
5. run the real `verify_prodlike_control_bundle-v2.py::verify()` against the same bundle/runtime manifest and require success;
6. enumerate all template `CONTROL[...]` references and prove every referenced field exists in the accepted control object;
7. run negative schema/kind/field/type/path/identity matrices only in temporary roots.

This witness executes pure file/schema logic only. It must not call systemd or host mutation paths.

## Test-review questions

TEST_REVIEW 014 must explicitly decide:

1. whether the 27-key V2 contract is sufficient for every current V2 template consumer;
2. whether keeping V2 candidate ID/binding while restoring four operational fields preserves the intended candidate-bound semantics without oracle change;
3. whether deriving `offhost_export_name` from `release_name` is deterministic and compatible with existing operational scripts;
4. whether the R2 five-file scope is sufficient and the fifth file is constrained to the predecessor synthetic runtime-manifest fixture;
5. whether the generated-document-through-real-consumer witness would have caught transaction005 before deployment;
6. whether negative tests meaningfully reject mixed V1/V2 schemas instead of merely matching self-produced bytes; and
7. whether all historical dev22 bytes remain outside the correction.

## Oracle and lifecycle discipline

`ORACLE_CHANGED=false`: the correction makes reviewed candidate-generic producer and its own operational consumers agree before deployment. It does not alter Phase00 native/business expectations.

Transaction005 and both failed dev23 trees remain immutable historical evidence. Reconciliation002 restored exact dev22. No failed receipt/artifact is rewritten or deleted.

If implementation requires files outside the R2 five-file allowlist, changes any of the other 62 template rows, changes historical dev22, introduces a new control version, or changes native/business expectations, return to TEST_DESIGN/TEST_REVIEW rather than widening scope.

## Exit gate

Independent TEST_REVIEW R2 must PASS the exact 27-key V2 contract, R2 five-file scope and fixture-only fifth-file constraint, real producer→consumer witness, negative matrix, 62-row/historical byte hardcuts, predecessor regression retention, `ORACLE_CHANGED=false`, and no deployment/native/signing/LAB authority. Only then may implementation begin.
