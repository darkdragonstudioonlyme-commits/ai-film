# TEST_CHANGE — dev23 V02/V03 candidate tooling rebind 009

~~~yaml
TEST_CHANGE_ID: TEST_CHANGE-P00-DEV23-TOOLING-REBIND-009
RUN_ID: RUN-P00-VALIDATION-002
WORK_ITEM: TEST-DESIGN-P00-DEV23-TOOLING-REBIND-009
BASE_VALIDATION_COMMIT: 2230531593b44e1960317c88f91fcbcde633a3c5
DEV23_CANDIDATE_BINDING: validation/tooling/dev23-candidate-binding.json
DEV23_CANDIDATE_BINDING_SHA256: ed7823332afa96c3335f3353518ca0330b9e3c687b0022926c776319611c1890
DEV23_BINDING_REVIEW: reviews/VALIDATION-V02-DEV23-CANDIDATE-BINDING-REVIEW-001.md
PREDECESSOR_TEST_CHANGE: TEST_CHANGE-P00-V03-AUTHORITY-BINDING-PRODUCER-006
CONSTRUCTIBILITY_TEST_CHANGE: TEST_CHANGE-P00-V03-AUTHORITY-CONSTRUCTIBILITY-007
ORACLE_CHANGED: false
EXPECTED_BUSINESS_BEHAVIOR_CHANGED: false
NATIVE_EXECUTION_AUTHORIZED: false
AUTHORITY_SIGNING_AUTHORIZED: false
STATUS: PENDING_INDEPENDENT_TEST_REVIEW
~~~

## Purpose

Rebind V02/V03 validation tooling to the reviewed dev23 candidate without mutating or repurposing historical dev22 tooling. The successor is candidate-profile driven so future candidate changes replace reviewed data/config rather than cloning every validator. Existing dev22 files remain historical evidence and continue to pass their original regressions.

## Authorized validation tooling

ADD candidate-generic V02 successor files only:
- `validation/tooling/v02_candidate_profile.py`
- `validation/tooling/v02-authority-intake-v2.py`
- `validation/tooling/v02-authority-preflight-v2.py`
- `validation/tooling/materialize-v02-native-policy-v2.py`
- `validation/tooling/pre-v03-authority-stage-v2.sh`
- `validation/tooling/watch-v02-authority-v2.sh`
- `validation/tooling/verify-lab-artifact-seal-v2.py`
- `validation/tooling/build_lab_payload-v2.py`
- `validation/tooling/V02_TOOLING_MANIFEST_DEV23.json`
- `validation/tooling/approval-envelope.dev23.template.json`
- `validation/tooling/AUTHORITY_INBOX_README_DEV23.txt`.

ADD the six V03 tools already authorized by TEST_CHANGE 006 and refined by V3/007:
- `validation/tooling/v03_binding_producer_common.py`
- `validation/tooling/v02b-authority-graph-compiler.py`
- `validation/tooling/verify-v03-binding-producer.py`
- `validation/tooling/v03-fixture-preparation-controller.py`
- `validation/tooling/update-v03-native-policy.py`
- `validation/tooling/materialize-v03-late-proof.py`.

ADD tests:
- `validation/tooling/tests/test_v02_candidate_profile.py`
- `validation/tooling/tests/test_v02_dev23_generic_tooling.py`
- `validation/tooling/tests/test_v02_dev23_candidate_hardcuts.py`
- `validation/tooling/tests/test_v03_binding_producer.py`
- `validation/tooling/tests/test_v03_policy_generation.py`
- `validation/tooling/tests/test_v03_fixture_preparation_controller.py`
- `validation/tooling/tests/test_v03_late_proof_materializer.py`.

Do not modify any historical dev22 tooling file in this change, including `v02-authority-intake.py`, `v02-authority-preflight.py`, `materialize-v02-native-policy.py`, `pre-v03-authority-stage.sh`, `watch-v02-authority.sh`, `verify-lab-artifact-seal.py`, `build_lab_dev22_payload.py`, `V02_TOOLING_MANIFEST.json`, `approval-envelope.template.json`, `AUTHORITY_INBOX_README.txt`, trust-anchor/signature/key-parity/local-identity tools or dev22 tests.

## Required tests

- `TV009-01` profile loader accepts only exact canonical binding bytes/hash and required schema; wrong candidate/binding/source/package/build/test/contract/review identity fails closed.
- `TV009-02` generic intake takes explicit reviewed binding/inbox, requires envelope identity equality plus local-controller containment and complete 86-case suite/role-pin authority; no default may silently select dev22.
- `TV009-03` preflight/watcher use explicit dev23 inbox/evidence roots, are read-only/fail-closed, and stale READY state is removed before evaluation.
- `TV009-04` V2 materializer consumes only a successful V2 intake and emits generation-1 NativeStore candidate bytes without HKLM write; exact candidate profile is carried in the receipt.
- `TV009-05` V2 pre-V03 stage requires stopped LAB, exact seal/profile/current evidence and never starts LAB/native or writes HKLM.
- `TV009-06` seal verifier binds exact dev23 candidate ID/binding/source and rejects writable/missing/hash/size/restore-probe drift.
- `TV009-07` generic LAB payload builder binds exact reviewed dev23 runtime/package/wheel/source/test/contract and immutable app manifest; it never copies a host venv or runs native cases.
- `TV009-08` DEV23 tooling manifest hashes every successor/shared dependency actually executed, exact dev23 binding and active trust-anchor/public-key identity; historical dev22 tooling bytes stay unchanged.
- `TV009-09` shared key/signature/identity primitives remain byte-identical and candidate-independent; no author test reads private signing bytes, signs authority or accesses canonical inbox/HKLM.
- `TV009-10` V03 compiler reproduces exactly 133 stages / 94-15-10-14 modes, acyclic detached base-manifest construction, signed finite destination locator rules and exact reviewed producer dependencies.
- `TV009-11` V03 producer verifier rejects missing/foreign/stale producer lineage, unreviewed mode substitution, mutable base refs, wrong checkpoint/copy receipt and incomplete proof scope.
- `TV009-12` policy updater implements reviewed P0-P8 serialization: exact parent under global guard, validate full next NativeStore, write/readback, idempotent publication event, release before request entry, fail-closed interruption/recovery; no signing.
- `TV009-13` fixture controller preserves 85 native fixture/preparation coverage and cannot execute native actions; it produces only reviewed ARRANGE/OBSERVE preparation records.
- `TV009-14` late-proof materializer supports exactly the nine reviewed roles/scope/timing/source rules and rejects early/wrong/ambiguous proof materialization.
- `TV009-15` all TD006/TD007 negative obligations remain represented; new tooling cannot weaken product `stage_authority.py`/harness checks or create accepted evidence from workspace-only observations.
- `TV009-16` old dev22 11-script regression suite remains green and no historical file is silently redefined as dev23 authority.

## Runtime / deployment boundary

Tests use fixtures, temp dirs and pure/test-double authority objects only. No local private key, canonical dev22/dev23 inbox, Windows HKLM, real LAB distro, prodlike deployment or SITE endpoint is touched. Passing this TEST_CHANGE/TEST_REVIEW authorizes implementation/review of successor tooling only; it does not authorize signing, deployment or native V03.

Prodlike dev23 release/control-bundle deployment and LAB reseed/rebuild remain separate later reconciliation work with fresh evidence.
