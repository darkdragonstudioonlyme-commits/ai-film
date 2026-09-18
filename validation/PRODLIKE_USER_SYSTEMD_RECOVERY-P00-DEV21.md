# Phase00 dev21 — user-systemd control-plane recovery

```yaml
RECOVERY_ID: PRODLIKE-USER-SYSTEMD-RECOVERY-P00-DEV21-001
BASE_VALIDATION_HEAD: 5edb3f65ddd369321c6a5a4286a8fa5027494a18
INCIDENT_CLASS: USER_SYSTEMD_DEPLOYMENT_ABSENT
STATUS: RECOVERED_VERIFIED_USER_SCOPE
SOURCE_BACKUP: control-state-20260918T041624Z.tar.gz
SOURCE_BACKUP_SHA256: ab2ddc7fab3693a7b0c101cc2dd8f7435b9a369b9d1b441f61611fec535e3210
SOURCE_BACKUP_FILE_COUNT: 91
SOURCE_SYSTEMD_FILE_COUNT: 46
SOURCE_TIMER_COUNT: 11
POSTRESTORE_HEALTH_SHA256: b2fa7347c966c8b85e781ae88931f87c331426f27492f9bb39cdc290b50d5cf5
POSTRESTORE_BACKUP_SHA256: 1d7e7ef0e37791c789940e2f3715c789fbb741271db75893ebc238fd69fdbfa9
POSTRESTORE_BACKUP_FILE_COUNT: 93
POSTRESTORE_EXPORT_SHA256: cec3339223a1d3965ba14bfcb22749560b2f3f68d565522631566d7ca5891a5c
VERIFIER: validation/tooling/verify_prodlike_user_systemd.py
PRODUCT_SOURCE_CHANGED: false
NATIVE_EXECUTION_ADVANCED: false
```

## Finding

A live operational audit found all documented AI-FILM timers absent from both user and system systemd views, while exact dev21 runtime bytes, V02 tooling, backup archives and offhost export remained intact. The latest verified control backup contained the complete supervision layer: eleven service/timer pairs plus drop-ins, with 46 `systemd/` files manifest-bound.

The absence was a deployment-state loss, not a reviewed runtime-content change. It exposed a recoverability gap: documentation described the timer controls, but the Git validation lane did not contain a machine verifier that could bind a live user-systemd deployment back to the portable control backup.

## Recovery evidence

1. Source control backup `ab2ddc7f...` verified PASS, 91 files, `native_authority_included=false`, `protected_identity_included=false`.
2. All 91 archive members, including 46 systemd files, matched the embedded manifest; all 16 live control scripts matched backup hashes.
3. A first copy to system scope was detected as incorrect before timers were started. Root execution of exact `verify-runtime` returned `APP_WRITABLE_DRIFT`, proving the units belong to the unprivileged runtime identity. System-scope files/symlinks were fully rolled back.
4. `loginctl` confirmed `dragon` user linger enabled. Exact 46 files were restored to `/home/dragon/.config/systemd/user`, byte-for-byte verified, and `systemd-analyze --user verify` passed.
5. Eleven user timers became enabled/active. Ten non-health periodic oneshots returned `Result=success / ExecMainStatus=0`; runtime-health then returned success.
6. Fresh runtime-health `b2fa7347...` reports every check true, `authority_status=BLOCKED`, reason `APPROVAL_ENVELOPE_MISSING`, READY absent and `native_execution_started=false`.
7. Recovery refreshed a verified 93-file control backup (`1d7e7ef0...`) and verified offhost export (`cec33392...`).
8. V02 preflight after recovery remains MISSING / `APPROVAL_ENVELOPE_MISSING`; no native policy or native case was created.

Local forensic receipt is retained under `/home/dragon/ai-film-dev/run-evidence/validation/systemd-restore/20260918T043027Z/`. It includes source archive hash, pre/post deployment hashes, unit verifier output, timer states and postrestore health evidence.

## Durable correction

`validation/tooling/verify_prodlike_user_systemd.py` now verifies portable backup manifest integrity against deployed user-systemd bytes and can additionally require every timer to be enabled and active. Its synthetic regression covers valid deployment, missing unit, content drift, missing drop-in and archive-member drift.

The operations runbook now states the scope invariant explicitly: these are **user-systemd** units and must not be installed as system/root services. This recovery changes no accepted candidate identity and grants no V02/V03/native authority.
