# TEST_CHANGE — dev23 prodlike release verify-runtime contract 013

~~~yaml
TEST_CHANGE_ID: TEST_CHANGE-P00-DEV23-PRODLIKE-VERIFY-RUNTIME-013
RUN_ID: RUN-P00-VALIDATION-002
WORK_ITEM: TEST-DESIGN-P00-DEV23-PRODLIKE-VERIFY-RUNTIME-013
BASE_VALIDATION_COMMIT: 35605267fea7cac1fa332a3fd7c90da5dd0726f8
PRODUCT_SOURCE_COMMIT: 2f7da39984a7a582c7cf2a84f743299fc7fe735f
CANDIDATE_ID: acf18da3-4969-451c-8a4b-a7e46ad89c98
CANDIDATE_BINDING_SHA256: ed7823332afa96c3335f3353518ca0330b9e3c687b0022926c776319611c1890
RECONCILIATION_RECEIPT_REVIEW: reviews/CODE-REVIEW-P00-DEV23-PRODLIKE-ATTEMPT4-RECONCILIATION-RECEIPT-002.md
SOURCE_DEBT: DEV23_RELEASE_MISSING_BIN_VERIFY_RUNTIME
ORACLE_CHANGED: false
EXPECTED_BUSINESS_BEHAVIOR_CHANGED: false
NATIVE_EXECUTION_AUTHORIZED: false
AUTHORITY_SIGNING_AUTHORIZED: false
PRODLIKE_DEPLOYMENT_AUTHORIZED: false
LAB_MUTATION_AUTHORIZED: false
STATUS: PENDING_INDEPENDENT_TEST_REVIEW
~~~

## Purpose

Attempt4 proved a release-contract gap rather than a host-only accident: reviewed control bytes require `/home/dragon/ai-film-runtime/current/bin/verify-runtime`, but candidate-generic `build_prodlike_release-v2.py` produced no `bin/verify-runtime`; `test_prodlike_release_v2.py` did not assert the required artifact. Reconciliation2 restored exact dev22 and preserved the broken staged dev23 tree as source-debt evidence.

This change defines the smallest candidate-generic correction. It does not authorize deployment or mutation.

## Authorized implementation scope

MODIFY only:
- `validation/tooling/build_prodlike_release-v2.py`
- `validation/tooling/tests/test_prodlike_release_v2.py`

Everything else remains byte-identical for this correction, including:
- `validation/tooling/build_prodlike_rebuild_set-v2.py`
- `validation/tooling/build_prodlike_control_bundle-v2.py`
- `validation/tooling/verify_prodlike_control_bundle-v2.py`
- `validation/tooling/verify_prodlike_user_systemd-v2.py`
- `validation/tooling/prodlike_control_templates_v2.json`
- `validation/tooling/deployment_transaction_common.py`
- `validation/tooling/deploy_prodlike_candidate-v2.py`
- `validation/tooling/rebuild_lab_candidate-v2.py`
- all historical dev22 tooling/tests/evidence and all accepted product source/contracts.

The preserved staged dev23 evidence is not an implementation target and must not be repaired/deleted in place.

## Required release contract

The candidate-generic release builder must generate a regular, non-symlink executable `bin/verify-runtime` with mode `0750`. Its semantics must match the V2 release layout, not the historical dev22 venv layout:

- resolve the release root from its own installed path;
- validate `runtime-manifest.json` kind/schema and candidate/non-native boundaries;
- validate `app-manifest.sha256` hash, exact app member set, app file hashes and immutable app file/directory modes;
- validate the copied wheel file against `runtime-manifest.json` `wheel_sha256`; no host venv is required or permitted;
- execute version, workspace-only preflight and native-inventory listing using a clean bounded environment equivalent to the V2 release builder (`PYTHONPATH=<release>/app/src`, system Python, release-local HOME/TMPDIR); inherited Python/virtualenv secrets are not trusted;
- require expected implementation version, `host_ready=false`, exactly 86 native cases `NOT_RUN`, zero parent native cases, and `qualification_issued=false`;
- remain non-native and perform no deployment, signing, HKLM, LAB, SITE or qualification action.

The final runtime manifest must bind `verify_runtime_sha256` to the generated verifier. The builder must run the verifier successfully after the final manifest exists, before returning PASS. The build receipt must expose verifier identity/status sufficiently for tests to prove this relation.

## Required tests

- `TV013-01` successful release contains exactly one regular non-symlink `bin/verify-runtime`, mode `0750`, executable and not writable.
- `TV013-02` runtime manifest contains `verify_runtime_sha256` equal to the final verifier bytes; build receipt binds the same identity/status.
- `TV013-03` generated verifier succeeds against a valid synthetic V2 release using the V2 clean-env/system-Python model and does not require a release-local or host venv.
- `TV013-04` verifier rejects missing/drifted runtime manifest, app-manifest hash, app member set, app bytes, writable app file/directory, wheel hash drift, wrong version, `host_ready=true`, native inventory count/status/parent-case drift, or `qualification_issued=true`.
- `TV013-05` verifier rejects self-integrity drift when its bytes no longer match `runtime-manifest.json.verify_runtime_sha256`.
- `TV013-06` candidate-generic verifier source/output contains no dev21/dev22 candidate ID, build/test/package hash, fixed release version/path or historical authority evidence identity.
- `TV013-07` composition test proves reviewed control consumers `scripts/activate-release`, `scripts/verify-current` and `systemd/aifilm-p00-current-verify.service` all require the same `<release>/bin/verify-runtime` path that a V2 release now guarantees.
- `TV013-08` absence, symlink substitution, wrong mode or non-executable verifier fails release verification before any deployment transaction can be authorized.
- `TV013-09` `build_prodlike_rebuild_set-v2.py` remains byte-identical and its regression stays green; rebuilding from reviewed package/wheel plus corrected builder deterministically regenerates the verifier rather than storing mutable host/runtime bytes in the rebuild set.
- `TV013-10` TV010 release/control/LAB tests, TV011/TV012 transaction tests, TV009 generic-tooling tests and 11 historical dev22 scripts remain green.
- `TV013-11` preserved broken dev23 staging evidence remains byte-identical during author/tests; tests operate only on temporary synthetic release roots.
- `TV013-12` no author/test path switches prodlike `current`, changes user-systemd, creates deployment authorization, mutates LAB, signs authority, writes HKLM, executes native routes, enters SITE, issues qualification or marks HOST_READY.

## Oracle and design discipline

`ORACLE_CHANGED=false`: this correction supplies an artifact already required by reviewed activation/control behavior. It does not change Phase00 business/native expectations. If implementation needs any file beyond the two-file MODIFY allowlist, or requires a release-local venv/new deployment behavior/new native evidence, return to TEST_DESIGN/TEST_REVIEW instead of widening scope.

Historical dev22 `verify-runtime` is semantic reference evidence only; candidate-generic implementation must not copy dev22 candidate identity or assume the old venv layout.

## Exit gate

Independent TEST_REVIEW must confirm the two-file MODIFY-only scope, TV013-01..12 coverage, explicit control-path composition, V2 clean-env/no-venv semantics, predecessor regression retention, preserved broken-dev23 evidence, `ORACLE_CHANGED=false`, and no deployment/native/signing/LAB authority. Only PASS authorizes implementation.
