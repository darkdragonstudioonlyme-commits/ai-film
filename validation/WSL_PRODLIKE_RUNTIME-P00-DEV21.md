# Phase00 dev21 — production-like WSL runtime

```yaml
RUNTIME_SETUP_ID: WSL-PRODLIKE-P00-DEV21-001
STATUS: READY_NON_NATIVE_LIVE_MONITORED
OPERATIONS_STATUS: READY_NON_NATIVE_PRODLIKE_OPERATIONS
OPERATIONS_RECORD: validation/WSL_PRODLIKE_OPERATIONS-P00-DEV21.md
SOURCE_COMMIT: 934659f535d81d9a4a07389531acc2b9c304fa6d
SOURCE_DIGEST: a284645e9eb60661f27eba1ea436d7ff7bbe60d6cd3e312850f1b108d32b1c62
TEST_DIGEST: c645f3d9f88fcb716f78fcff9cd9b4144b320dc4f0c8c7082346a5cfbe6d9383
CONTRACT_DIGEST: f259656c48ed24c15bd48da2bb040950ed94d8edcf1473cf6456b96578c933ee
V21_PACKAGE_SHA256: f6ee158a318614f8bbef28be7af82549e0a268425da28147a2fa7b14c7b3d3e3
WSL_DISTRO: Ubuntu-24.04
PYTHON: 3.12.3
VALIDATION_VENV: /home/dragon/ai-film-dev/venvs/validation-dev21
VALIDATION_VENV_PIP: 24.0
PRODLIKE_ROOT: /home/dragon/ai-film-runtime/dev21
STABLE_CURRENT: /home/dragon/ai-film-runtime/current
APP_ROOT: /home/dragon/ai-film-runtime/dev21/app
APP_FILE_COUNT: 283
APP_BYTE_VERIFY: PASS
APP_MANIFEST_SHA256: 07fcf4a31c6ffabc3628ba12584d249680cea1344e26fb1d2cbe2983e30270fa
APP_READ_ONLY: true
RUNTIME_VENV: /home/dragon/ai-film-runtime/dev21/venv
RUNTIME_DEPENDENCIES: []
PIP_CHECK: PASS
BUILD_WHEEL: aifilm_p00_contracts-0.1.0.dev21-py3-none-any.whl
BUILD_WHEEL_SHA256: 9b565b24a896879bd7bd812c43efcc741d8bc2eb08c0b23318b1e66c64b9e7e8
RUNTIME_MANIFEST_SHA256: 8227e8350208314db087612889d2b481393c67ec3a5eb0bfa84a869c1d0829a2
VERIFY_RUNTIME_SHA256: a2b7163452682cc4522c4afc3a07d4dbcf95241051ec69780e6eb4c3b9714425
VERIFY_CURRENT_SHA256: 93e6d32a0b6c7a8a980ed3c80a654e6256fa9f000cc0746a3dbb9b030819032f
ACTIVATE_RELEASE_SHA256: b175d934787eec0fe919de96b2ebcdd1f5abe9c5249b9b62d8e88bd53a7531cf
SYSTEMD_VERIFY_SERVICE_SHA256: c54a9ca3d2fe38d7f7f36b057e6e3f1b8d4aa1ae1fcbb8661273dac82235bd4f
SYSTEMD_VERIFY_TIMER_SHA256: 2e3568c72d1be9c3b82d487bc5c3128daec02c3ed3e0cf62b07c82126f00bebc
SYSTEMD_TIMER_ENABLED: true
SYSTEMD_TIMER_ACTIVE: true
SYSTEMD_USER_LINGER: true
USER_SYSTEMD_RECOVERY_STATUS: RECOVERED_VERIFIED_USER_SCOPE
USER_SYSTEMD_RECOVERY_RECORD: validation/PRODLIKE_USER_SYSTEMD_RECOVERY-P00-DEV21.md
USER_SYSTEMD_VERIFIER: validation/tooling/verify_prodlike_user_systemd.py
USER_SYSTEMD_UNIT_FILE_COUNT: 46
USER_SYSTEMD_TIMER_COUNT: 11
POSTRESTORE_HEALTH_SHA256: b2fa7347c966c8b85e781ae88931f87c331426f27492f9bb39cdc290b50d5cf5
MONITOR_INTERVAL: 15min
SYSTEMD_SECURITY_EXPOSURE: "4.1 OK"
ENVIRONMENT_POLICY: ENV_CLEARED_ALLOWLIST_ONLY
RUNTIME_VERIFY: "PRODLIKE_RUNTIME_VERIFY_PASS 283 86 NOT_RUN"
ATOMIC_RUNTIME_ACTIVATION: PASS
HEALTH_SCRIPT_SHA256: dfd11d418b820a3083f7016d1a0ab3355f3bd9b650e3c4ffc2de67ba042b34d5
HEALTH_TIMER: "enabled active 10min"
HEALTH_SYSTEMD_SECURITY: "4.1 OK"
HEALTH_LATEST_STATUS: PASS
BACKUP_SCRIPT_SHA256: ce3fb2fbac2e6514ceeae930efd483fcc3a95017d87b638331bff2f29620f327
BACKUP_TIMER: "enabled active 24h"
BACKUP_SYSTEMD_SECURITY: "4.1 OK"
CONTROL_BACKUP_RETENTION: 14
CONTROL_BACKUP_RESTORE_PROBE: PASS
NATIVE_INVENTORY_MODE: "0600"
NATIVE_SITE_AUTHORITY_CHANGED_BY_ACTIVATION: false
NATIVE_LAB_AUTHORITY: false
NATIVE_EXECUTION_STARTED: false
HOST_READY: false
```

## Deployment shape

The runtime is intentionally not a plain wheel install. The exact dev21 package resolves its normative `contracts/` relative to the package source root; the built wheel contains package modules but no root `contracts/` or `docs/`. The active WSL runtime therefore uses an immutable exact-Git app tree plus an isolated Python venv. The wheel remains a reproducible build artifact, not the native authority root.

`/home/dragon/ai-film-runtime/dev21/app` was created from exact source commit `934659f...`, contains exactly 283 tracked files, and every deployed file byte was reverified against its Git blob. The app tree is read-only. Mutable state is separated into `var/lib`, `var/log`, `var/tmp`, and `evidence`; `current` points to dev21.

Both the runtime launcher and release-control helpers re-exec with an empty inherited environment and an explicit allowlist. This prevents arbitrary shell environment secrets from being forwarded into the runtime. No stored privilege secret is required by runtime activation, integrity verification, monitoring, health collection, backup, or the current validation workflow preparation.

## Live-readiness and production-like operations controls

A live recovery check on 2026-09-18 found the user-systemd unit deployment absent even though runtime bytes, backup/export artifacts and V02 fail-closed tooling remained intact. Recovery used the verified control backup `control-state-20260918T041624Z.tar.gz` (`ab2ddc7f...`, 91 files). An initial system-scope copy was detected as wrong scope before any timer activation because root execution violated the runtime writability invariant (`APP_WRITABLE_DRIFT`); it was fully rolled back. Exact 46 unit/drop-in files were then restored to `~/.config/systemd/user`, verified byte-for-byte, loaded through the lingering `dragon` user manager, and all eleven timers plus periodic services returned healthy state. Fresh postrestore control backup/export/health evidence is recorded in `validation/PRODLIKE_USER_SYSTEMD_RECOVERY-P00-DEV21.md`.

`aifilm-p00-dev21-verify.service` is a hardened user-systemd oneshot verifier and `aifilm-p00-dev21-verify.timer` runs it every 15 minutes. The timer is enabled and active; user linger is enabled so the user manager is not tied to the interactive session. The service has no Internet socket families, no capabilities, `NoNewPrivileges`, read-only home/system protection with only runtime tmp writable, private devices/tmp, W^X protection, and an observed `systemd-analyze security` exposure score of `4.1 OK`.

`aifilm-p00-runtime-health.timer` runs every 10 minutes. Its collector fails closed on release/symlink drift, runtime-integrity failure, inconsistent V02 READY/BLOCKED signaling, operational-script write-permission drift, inactive AI-FILM timers, native-authority/native-execution drift, low disk headroom, or evidence permission regression. Current health is PASS while the validation authority field correctly remains `BLOCKED / APPROVAL_ENVELOPE_MISSING`.

`aifilm-p00-control-backup.timer` runs every 24 hours with 14-archive retention. The backup uses a fixed safe whitelist covering runtime/release manifests, release history, health, non-sensitive authority-watcher evidence, operational scripts and AI-FILM user-systemd units. It explicitly excludes the approval inbox, protected authority objects, raw host/operator identity and credentials. Archive/sidecar modes are `0600`; health/backup directories are `0700`. The latest archive was extracted into a temporary restore probe and every restored file rehashed against its embedded manifest before the probe was deleted; the restore probe PASSed.

`/home/dragon/ai-film-runtime/bin/activate-release` verifies the candidate release before an atomic `current` symlink switch and writes a mode-600 release history. Re-activation of dev21 passed and explicitly preserved native/SITE authority state. `/home/dragon/ai-film-runtime/bin/verify-current` verifies the stable active release through the same environment-cleared boundary. Operational targets are owner-controlled and are not group/other writable; the stable launcher path is a symlink to the mode-0750 release launcher.

## Verification

The monitored runtime independently passes 283/283 app-byte verification, app-manifest verification, isolated Python 3.12.3 and `pip check`, document-only workspace preflight, recovery notes, and the 86-case metadata inventory with all cases still `NOT_RUN`, zero parent cases executed, no qualification issued, and `host_ready=false`. Validation workspace remains exact dev21 and clean; the latest safe suite remains 760 tests PASS and 101 static PASS.

This record is deployment/operational-readiness evidence only. It does not register the current Windows/WSL host as disposable LAB, does not grant native LAB/SITE execution authority, and does not advance `RUN-P00-VALIDATION-001` beyond `V02_LAB_EXECUTION_AUTHORITY`.