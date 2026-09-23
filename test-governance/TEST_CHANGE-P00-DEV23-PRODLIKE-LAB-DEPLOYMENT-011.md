# TEST_CHANGE — dev23 prodlike deployment and LAB rebuild/reseed transactions 011

~~~yaml
TEST_CHANGE_ID: TEST_CHANGE-P00-DEV23-PRODLIKE-LAB-DEPLOYMENT-011
RUN_ID: RUN-P00-VALIDATION-002
WORK_ITEM: TEST-DESIGN-P00-DEV23-PRODLIKE-LAB-DEPLOYMENT-011
BASE_VALIDATION_COMMIT: d1e436a5c526de95b81eeae1007808c8fd1a9dd9
PRODUCT_SOURCE_COMMIT: 2f7da39984a7a582c7cf2a84f743299fc7fe735f
CANDIDATE_ID: acf18da3-4969-451c-8a4b-a7e46ad89c98
CANDIDATE_BINDING_SHA256: ed7823332afa96c3335f3353518ca0330b9e3c687b0022926c776319611c1890
PACKAGE_SHA256: d60433b2b559c975dd93378db7c3c8481ba80896deb539d8227b28b169a83dbf
WHEEL_SHA256: 55853acf55374db3e8da6159ae6fe26dcad2d0a6b7f022aef79b2009c40253df
PREDECESSOR_TEST_CHANGE: TEST_CHANGE-P00-DEV23-PRODLIKE-LAB-RECONCILIATION-010
PREDECESSOR_TEST_REVIEW: test-governance/TEST_REVIEW-P00-DEV23-PRODLIKE-LAB-RECONCILIATION-010.md
TOOLING_CODE_REVIEW: reviews/CODE-REVIEW-P00-DEV23-PRODLIKE-LAB-RECONCILIATION-010.md
CURRENT_PRODLIKE_VERSION: 0.1.0.dev22
TARGET_PRODLIKE_VERSION: 0.1.0.dev23
CURRENT_LAB_STATE: STOPPED_DEV22_SEALED_PENDING_AUTHORITY
DEV22_PRODLIKE_RECEIPT_SHA256: dcd7bb011005032cc8564bfda386f6c3c4987ae3336b6a00f3e3a698fb41428a
DEV22_LAB_REBUILD_RECEIPT_SHA256: df3652621d71d13efebcab50fcb8743b4c203b08c0e28f27a5360f00a6321f97
ORACLE_CHANGED: false
EXPECTED_BUSINESS_BEHAVIOR_CHANGED: false
NATIVE_EXECUTION_AUTHORIZED: false
AUTHORITY_SIGNING_AUTHORIZED: false
HKLM_MUTATION_AUTHORIZED: false
SITE_AUTHORIZED: false
STATUS: PENDING_NON_AUTHOR_TEST_REVIEW
~~~

## Purpose

TEST_CHANGE 010 and its CODE_REVIEW authorize candidate-generic build/verify/plan tooling only; they deliberately do not authorize deployment or LAB mutation. This successor defines the exact mutation/recovery/evidence contract required before dev23 can replace dev22 as the non-native prodlike runtime and LAB technical substrate.

The two transactions are independent and must be separately receipted. Prodlike deployment success does not imply LAB rebuild success. LAB rebuild failure must not roll back a successfully verified prodlike deployment unless a separately reviewed recovery condition explicitly requires that action.

## Authorized implementation scope after TEST_REVIEW PASS

ADD only:
- `validation/tooling/deploy_prodlike_candidate-v2.py`
- `validation/tooling/rebuild_lab_candidate-v2.py`
- `validation/tooling/deployment_transaction_common.py`
- `validation/tooling/tests/test_prodlike_deployment_transaction_v2.py`
- `validation/tooling/tests/test_lab_rebuild_transaction_v2.py`.

Existing TEST_CHANGE-009/010 generic tooling, dev23 binding, historical dev22 tooling/tests/evidence and product source remain byte-identical. Any need to modify them reopens test/design review.

## Common execution hardcuts

Both executors default to plan/dry-run and require an exact transaction authorization capsule for mutation. The capsule binds canonical main state, owning validation head, reviewed executor commit/tree, candidate ID/binding, transaction ID, exact input hashes, permitted mutation roots/commands and one execution attempt. It contains no secret bytes and grants neither signing nor native authority.

Mutation mode must reject: dirty/unreviewed executor bytes, wrong candidate, stale dev22-as-dev23 artifacts, changed input hash, unexpected target root, non-user systemd scope, unknown WSL distro, LAB not in required stopped boundary, missing rollback artifact, previous uncertain attempt, or any request for private key/HKLM/native/SITE/qualification/HOST_READY operations.

Every external command is argument-array allowlisted; shell interpolation, arbitrary command passthrough, sudo/root escalation, network package install and nested worker invocation are forbidden. Tests use injected fake command runners; they do not mutate the real prodlike runtime or LAB.

## Prodlike transaction requirements

- `TV011-01` preflight requires current link/runtime exactly dev22, current dev22 deployment receipt/manifest identities, exact reviewed dev23 release/rebuild/control bundle and exact candidate binding. A mixed candidate fails before mutation.
- `TV011-02` transaction captures durable pre-switch rollback evidence before the first mutation: current symlink target, deployed scripts/units/config bytes+modes, enabled/active user-timer set, dev22 runtime/rebuild identities and control-backup hash.
- `TV011-03` dev23 release is staged side-by-side under candidate/version-specific immutable path and verified there before changing `current`; existing dev22 runtime/rebuild bytes are never overwritten.
- `TV011-04` reviewed 64-file control bundle is statically verified before deployment. Deployment may touch only configured user script/config roots and user-systemd unit tree; extra/missing members, wrong mode or path escape block.
- `TV011-05` exactly the reviewed 11 user timers/services are quiesced before replacing their unit/script/config bytes. No system-level unit, root service, unrelated user unit or LAB process may be touched.
- `TV011-06` stable current-link switch is atomic and occurs only after side-by-side runtime + source control bundle verification. Rollback identity remains durable until the full transaction commits.
- `TV011-07` post-switch verification requires exact deployed-byte/mode equality, runtime manifest dev23 identity, generic current verifier PASS, exact 11 reviewed user timers enabled/active and live user-scope service verification. Runtime-health is evaluated last and cannot self-certify readiness.
- `TV011-08` any failure after the first mutation triggers deterministic rollback of current link, deployed control bytes and user-timer enable/active state to the captured dev22 snapshot; rollback is independently reverified. Ambiguous/failed rollback returns `RECONCILE_REQUIRED`, never PASS.
- `TV011-09` prodlike receipt records before/after identities, rollback evidence, every mutation boundary, live verifier results and `native_execution_started=false`; it cannot claim LAB/native/V02 qualification.

## LAB rebuild/reseed transaction requirements

- `TV011-10` preflight requires primary `AI-FILM-P00-LAB` stopped, exact dev22 LAB deployment receipt/seal/facts, exact reviewed dev23 payload + rebuild plan, and exact prodlike dev23 deployment receipt PASS. No primary LAB mutation occurs until fresh rollback export completes and hashes.
- `TV011-11` a fresh stopped pre-rebuild export of the primary LAB is captured before mutation. The primary registration may not be unregistered or overwritten without that rollback export and exact registration/path snapshot.
- `TV011-12` dev23 LAB runtime is installed/reseeded only from reviewed candidate payload, using the existing isolated LAB identity. Guest dependency/runtime construction is offline/candidate-bound; no host venv or network dependency install is allowed.
- `TV011-13` metadata verification inside the rebuilt LAB may read version/source/runtime/inventory only. It must show `0.1.0.dev23`, exact source/package/wheel/app identities, 86-case inventory `NOT_RUN`, zero parent cases, no qualification/HOST_READY, and must not execute native routes/tests.
- `TV011-14` after metadata verification the LAB is stopped; a fresh pristine dev23 export is captured and imported under a temporary probe registration/path. Probe verification repeats exact app/mode/venv/isolation/inventory checks, then the probe is stopped and unregistered.
- `TV011-15` canonical technical facts and artifact seal may be replaced only after restore-probe PASS. Previous dev22 facts/seal are copied to immutable historical identities before replacement. New seal is exact dev23 candidate/binding/source and remains non-authority.
- `TV011-16` any failure after primary mutation must leave a stopped, known registration state with rollback export preserved. Temporary probe leftovers, unknown registration, restore failure or partial seal/facts update returns `RECONCILE_REQUIRED`; it cannot silently continue to authority construction.
- `TV011-17` LAB receipt binds pre-rebuild export, pristine raw/sealed export, restore-probe receipt/unregistered state, technical facts, artifact seal, runtime/app/inventory, rollback source and `authority_envelope_created=false`, `native_execution_started=false`, `v03_started=false`.

## Cross-transaction and historical coverage

- `TV011-18` successful prodlike deployment with LAB still dev22/stopped is a valid intermediate state and must be represented honestly; it is not full dev23 V02 readiness.
- `TV011-19` all historical dev22 deployment tooling, receipts, reviews/audits, runtime rollback bytes and LAB rollback exports remain immutable and remain rollback/history evidence only.
- `TV011-20` tests inject failure at every mutation boundary for both transactions and prove fail-closed non-replay behavior; unknown/ambiguous external command completion is reconciled from durable before/after evidence before any retry.
- `TV011-21` no path in either executor reads private signing key bytes, signs authority, writes HKLM, creates authority envelope/READY, runs native tests/routes, enters SITE, issues qualification or marks HOST_READY.

## Execution evidence semantics

Implementation/unit/fault-injection tests do not prove deployment. After executor CODE_REVIEW PASS, each real transaction requires a separate immutable execution authorization, before/after receipt, independent verification, review and audit. Prodlike deployment and LAB rebuild/reseed are separate real transactions even when executed in the same parent run.

No real mutation is authorized by TEST_CHANGE/TEST_REVIEW 011 alone.

## Exit gate

Independent TEST_REVIEW must confirm the exact five-file ADD-only implementation boundary, TV011-01..21 coverage, immutable historical scopes, explicit rollback/reconcile semantics, independent prodlike/LAB receipts and the no-native/no-signing/no-HKLM boundary. Only PASS authorizes implementation of the transaction executors and tests. Real execution remains separately blocked.
