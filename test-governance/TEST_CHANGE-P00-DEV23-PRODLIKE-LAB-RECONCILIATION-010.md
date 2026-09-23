# TEST_CHANGE — dev23 prodlike/LAB reconciliation successor 010

~~~yaml
TEST_CHANGE_ID: TEST_CHANGE-P00-DEV23-PRODLIKE-LAB-RECONCILIATION-010
RUN_ID: RUN-P00-VALIDATION-002
WORK_ITEM: TEST-DESIGN-P00-DEV23-PRODLIKE-LAB-RECONCILIATION-010
BASE_VALIDATION_COMMIT: 77cb3860eba2554c02f26fa93ab79dcd2d25f7d9
PRODUCT_SOURCE_COMMIT: 2f7da39984a7a582c7cf2a84f743299fc7fe735f
CANDIDATE_ID: acf18da3-4969-451c-8a4b-a7e46ad89c98
CANDIDATE_BINDING_SHA256: ed7823332afa96c3335f3353518ca0330b9e3c687b0022926c776319611c1890
PACKAGE_SHA256: d60433b2b559c975dd93378db7c3c8481ba80896deb539d8227b28b169a83dbf
WHEEL_SHA256: 55853acf55374db3e8da6159ae6fe26dcad2d0a6b7f022aef79b2009c40253df
TOOLING_REVIEW: reviews/CODE-REVIEW-P00-DEV23-V02-V03-TOOLING-REBIND-001.md
ORACLE_CHANGED: false
EXPECTED_BUSINESS_BEHAVIOR_CHANGED: false
NATIVE_EXECUTION_AUTHORIZED: false
AUTHORITY_SIGNING_AUTHORIZED: false
PRODLIKE_DEPLOYMENT_AUTHORIZED: false
LAB_MUTATION_AUTHORIZED: false
STATUS: PENDING_INDEPENDENT_TEST_REVIEW
~~~

## Purpose

Current prodlike runtime and sealed LAB are exact dev22 evidence. They remain valid historical/baseline evidence but cannot satisfy dev23 candidate gates. Define the smallest candidate-generic successor needed to build and verify dev23 prodlike release/control artifacts and to prepare/verify a later dev23 LAB reseed/rebuild transaction without repurposing historical dev22 tooling or beginning native execution.

## Reusable reviewed components

Reuse byte-identically from TEST_CHANGE/REVIEW 009:
- `validation/tooling/v02_candidate_profile.py`
- `validation/tooling/build_lab_payload-v2.py`
- `validation/tooling/verify-lab-artifact-seal-v2.py`
- `validation/tooling/dev23-candidate-binding.json`
- active trust/key-parity primitives as data/verification dependencies only.

These reusable tools do not prove prodlike deployment or LAB reseed/rebuild merely by existing.

## Authorized successor files

ADD candidate-generic prodlike tooling:
- `validation/tooling/build_prodlike_release-v2.py`
- `validation/tooling/build_prodlike_rebuild_set-v2.py`
- `validation/tooling/build_prodlike_control_bundle-v2.py`
- `validation/tooling/verify_prodlike_control_bundle-v2.py`
- `validation/tooling/verify_prodlike_user_systemd-v2.py`
- `validation/tooling/prodlike_control_templates_v2.json`.

ADD candidate-generic LAB reconciliation tooling:
- `validation/tooling/plan_lab_candidate_rebuild-v2.py`
- `validation/tooling/verify_lab_candidate_rebuild_receipt-v2.py`.

ADD tests:
- `validation/tooling/tests/test_prodlike_release_v2.py`
- `validation/tooling/tests/test_prodlike_control_bundle_v2.py`
- `validation/tooling/tests/test_prodlike_user_systemd_v2.py`
- `validation/tooling/tests/test_lab_candidate_rebuild_v2.py`.

Historical dev22 tooling/evidence stays byte-identical, including `build_prodlike_dev22_release.py`, `build_prodlike_dev22_rebuild_set.py`, `verify_prodlike_dev22_control_bundle.py`, `verify_prodlike_user_systemd.py`, `build_lab_dev22_payload.py`, `verify-lab-artifact-seal.py`, their dev22 regression scripts and all dev22 deployment/review/audit records.

## Required tests

- `TV010-01` prodlike release builder requires explicit reviewed candidate binding plus exact package/wheel identities; wrong source/package/wheel/build/test/contract/version fails before output.
- `TV010-02` release output reproduces exact package app bytes, wheel modules and immutable app manifest; workspace preflight remains `host_ready=false`; 86-case native inventory remains `NOT_RUN`, zero parent cases, no qualification/HOST_READY.
- `TV010-03` release/rebuild receipts carry dev23 candidate ID/binding/source/package/wheel and `native_execution_started=false`; no dev22 identity can satisfy dev23 verification.
- `TV010-04` rebuild-set builder contains only reviewed package/wheel/app/runtime manifests required for recovery and excludes private keys, approval envelopes, native policy, protected host identity and mutable host venv.
- `TV010-05` control-bundle builder renders from neutral reviewed templates + explicit dev23 control data; generated scripts/units contain no dev21/dev22 candidate hashes, version paths or old authority evidence roots.
- `TV010-06` control-bundle verifier checks exact member set, hashes, deploy modes, release-control identity, timer/service inventory and candidate runtime identity; wrong/mixed dev22/dev23 deployed bytes fail closed.
- `TV010-07` user-systemd verifier checks archive/deployed byte equality in user scope; static fixture tests do not call live systemd. Any later live timer/service verification is deployment evidence under a separately reviewed transaction.
- `TV010-08` existing `build_lab_payload-v2.py` is reused byte-identically and binds exact reviewed dev23 runtime/package/wheel/source/test/contract; payload contains no host venv and performs no native execution.
- `TV010-09` LAB rebuild planner requires explicit stopped-LAB observation, exact dev23 payload identity, current dev22 rollback/export/seal identities and target candidate binding; it emits a plan/expected-evidence contract only and cannot start/import/register/unregister WSL.
- `TV010-10` LAB rebuild receipt verifier accepts only exact target candidate ID/binding/source/package plus stopped final LAB, exact app manifest/payload, 86-case `NOT_RUN` inventory, fresh pristine export identity, restore-probe PASS, candidate-bound artifact seal and `authority_envelope_created=false`.
- `TV010-11` stale dev22 LAB seal/runtime/payload/rebuild receipt cannot be relabeled or reused as dev23 proof even when host/key identities are unchanged.
- `TV010-12` no author/test path reads private signing bytes, signs authority, writes HKLM, mutates canonical authority inbox, starts LAB, executes native routes, enters SITE, issues qualification or marks HOST_READY.
- `TV010-13` all historical dev22 prodlike/LAB tools, tests and deployment evidence remain byte-identical and their existing regressions stay green.
- `TV010-14` tests separately prove successful candidate-generic build/verification and rejection of mixed-candidate, stale-manifest, writable-artifact, extra-member, wrong-mode, rollback-loss, restore-probe-fail and inventory-status drift.

## Deployment boundary

Passing TEST_CHANGE/TEST_REVIEW 010 authorizes implementation and code review of the listed successor tooling only. It does not authorize switching `/home/dragon/ai-film-runtime/current`, changing user-systemd deployment, mutating/exporting/importing/unregistering the LAB distro, replacing LAB facts/seal, signing an authority graph, writing HKLM or running native cases.

After implementation CODE_REVIEW PASS, prodlike deployment and LAB rebuild/reseed remain explicit reviewed/audited execution transactions with before/after receipts and rollback identity. Native authority remains a later gate.

## Exit gate

Independent TEST_REVIEW must confirm `ORACLE_CHANGED=false`, exact ADD-only successor scope, byte-identical historical dev22 scope, reuse of 009 generic LAB tools without modification, TV010-01..14 coverage and no deployment/native/signing authority. Only that PASS authorizes implementation of the reconciliation successor.
