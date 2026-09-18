# Phase00 dev22 — production-like runtime/control migration design

MIGRATION_ID: PRODLIKE-DEV22-MIGRATION-P00-001
RUN_ID: RUN-P00-VALIDATION-002
STEP_ID: V02_LOCAL_OPERATOR_LAB_AUTHORITY
BASE_VALIDATION_HEAD: c5f2d43aaa0d2e0ae796ea7981f578bcb2b0a148
STATUS: DESIGN_CANDIDATE_PENDING_REVIEW
TARGET_RELEASE: dev22
TARGET_SOURCE_COMMIT: 86bb64938a136e3f8d6cfd0266685a01cb832b77
TARGET_PACKAGE_SHA256: c2ea52087039f4c7b98c53a7cc0eaf1a4a0f931645f86491bf2eb8ef12956aae
TARGET_WHEEL_SHA256: e5a7ae51c73e5e9bea1e9d62c2220d2f39133a2bd74f73ccf97c38d75019147f
CONTROL_BUNDLE: validation/prodlike-dev22
CONTROL_BUNDLE_MANIFEST_SHA256: 62918ef3fddb1b752c9a7679a3f47f29e54b8b992efdf593c123d77c0ab7b800
RELEASE_CONTROL_SHA256: 2988b93eef37e9b18a14979902f6686f7fb2fb4bb9d1f0b34392ab01ac9c9803
STAGING_RUNTIME_MANIFEST_SHA256: ef19d1bbb573bb8b75a7f49d01231436151ec74f614ba2f97cf5f0cff7ae009a
STAGING_APP_MANIFEST_SHA256: 8f31bb6359387257f00388e12f05e2cb6014867ebb90295d1684d3b6fab00471
STAGING_REBUILD_INDEX_SHA256: 24338195fe4bb7adda35b4d4484728a0c30f235c4b88b11a9c2fc4171de1ddef
STAGING_EVIDENCE: /home/dragon/ai-film-dev/run-evidence/validation/prodlike-dev22-design-final/20260918T082115Z
REVIEW_RECORD: reviews/VALIDATION-PRODLIKE-DEV22-MIGRATION-REVIEW-001_PASS.md
AUDIT_RECORD: reviews/VALIDATION-PRODLIKE-DEV22-MIGRATION-AUDIT-001_PASS.md
NATIVE_EXECUTION_STARTED: false

## Finding

The current non-native production-like runtime remains exact dev21 and healthy, but its control plane is version-bound: `runtime-health.py`, backup/mirror/rebuild/export/DR paths, the runtime verify service/timer, and several unit descriptions hardcode dev21. More importantly, current health/status still read the historical dev21 authority evidence root `/run-evidence/validation/v02-authority` while the canonical dev22 watcher writes `/run-evidence/validation/v02-authority-dev22`. Therefore dev21 health remains useful historical infrastructure evidence but cannot be promoted to dev22 candidate readiness by switching only the `current` symlink.

## Canonical control source

V58 migration introduces a non-rotating, Git-reviewed control source under `validation/prodlike-dev22/`:

- `release-control.json` binds exact dev22 product/package/wheel identities, runtime/rebuild/backup/export paths, dev22 authority-evidence root and same-WSL local-authority model;
- 17 operational scripts, including new `control_common.py`, consume the fixed release-control file rather than environment overrides;
- 46 exact target **user-systemd** unit/drop-in files use generic `aifilm-p00-current-verify.{service,timer}` and stable `current` paths; old `aifilm-p00-dev21-verify.*` is forbidden in the target;
- `CONTROL_BUNDLE_MANIFEST.json` content-addresses all 64 deployable files and declares target deployment modes;
- `verify_prodlike_dev22_control_bundle.py` independently checks source/deployed bytes, modes, exact release identity, absence of stale dev21 authority tokens, old verify-unit absence and—when live—the unprivileged user-systemd scope plus all 11 enabled/active timers. It does not rely on runtime-health to prove the scheduler that runs runtime-health.

This removes the previous design debt where authoritative supervision bytes existed only inside rotating control backups. Fresh operational backups remain required recovery evidence, but they are consumers/copies of a stable reviewed source rather than the only deployable source.

## Exact release build

`build_prodlike_dev22_release.py` validates the reviewed V22 package/wheel hashes, extracts only the package manifest's 284 exact Git source members, verifies all member hashes and all 58 wheel Python modules, creates an isolated venv + `.pth`, writes a relative-path launcher and verifier, collects the 86-case metadata-only native inventory, makes the app tree read-only and emits a deterministic runtime manifest.

Exact-artifact staging produced:

- runtime manifest `ef19d1bb...`;
- app manifest `8f31bb63...`;
- 284/284 app files;
- 58/58 wheel modules;
- `PRODLIKE_RUNTIME_VERIFY_PASS 284 86 NOT_RUN release=dev22`;
- deterministic 4-file rebuild set index `24338195...`;
- `native_execution_started=false`.

The synthetic builder regression separately proves package-hash fail-closed behavior and generated runtime/rebuild verification without depending on the exact V22 artifacts being present in CI.

## Migration transaction

Deployment must preserve the current dev21 runtime as rollback source and must not start the LAB. Required order:

1. Verify current dev21 runtime/health/V02 blocked state and create a final fresh dev21 control backup.
2. Build `/home/dragon/ai-film-runtime/dev22` side-by-side from exact reviewed package/wheel and require its generated `verify-runtime` PASS before any switch. Build the dev22 NTFS rebuild set and verify identities.
3. Privately snapshot current root control scripts/config, user-systemd unit tree and `current` symlink for rollback.
4. Quiesce all AI-FILM user timers/services. Deploy exact reviewed control scripts, `release-control.json`, `control-bundle-manifest.json` and exact target user-systemd files; remove/disable only superseded `aifilm-p00-dev21-verify.*`; run `systemd-analyze --user verify` before timer activation. Never install these units under `/etc/systemd/system`.
5. Atomically activate exact dev22 using stable `activate-release dev22`; verify `current` and exact release identity.
6. Enable/start exactly 11 target user timers. Before health is trusted, independently run the control-bundle verifier with deployed-byte/mode/user-scope/live-timer checks.
7. Execute producer-before-consumer refresh: current verify → control backup → host mirror → rebuild verify → offhost export/verify → recovery verify → full DR rehearsal → fail-closed campaign → evidence ledger → V02 watcher → runtime-health last.
8. Verify a fresh control backup independently binds the manifest-backed user-systemd deployment and live timer states using `verify_prodlike_user_systemd.py`. This is required for the supervision-deployability learning metric and is not replaced by the health timer.
9. Require final runtime-health PASS and status `READY_NON_NATIVE_PRODLIKE_OPERATIONS`, `BLOCKED_LOCAL_OPERATOR_AUTHORITY`, `APPROVAL_ENVELOPE_MISSING`, `native_execution_started=false`. V02 remains BLOCKED; LAB remains stopped.

On any failure before final health PASS, stop target timers, restore prior root control/config/user-systemd bytes and `current -> dev21` from the private snapshot, reload/re-enable the prior user timers and verify dev21 health. Failed migration evidence is retained; no partial deployment is labelled ready.

## Learning boundary

This future live supervision migration occurs after activation of `LEARNING-PRODLIKE-SUPERVISION-DEPLOYABILITY-014` and may qualify as its effectiveness event only if the real deployment independently detects/prevents wrong-scope/missing/byte-drift supervision before READY, binds manifest-backed source/backup to the unprivileged deployed units and live timers without relying on runtime-health itself, and preserves V02/native boundaries. A measurement receipt is created only after the real event and independent review; this design/staging work does not count.
