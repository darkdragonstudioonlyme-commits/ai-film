# Phase00 dev21 — production-like WSL operations hardening

```yaml
OPS_RECORD_ID: WSL-PRODLIKE-OPS-P00-DEV21-001
STATUS: READY_NON_NATIVE_PRODLIKE_OPERATIONS
SOURCE_COMMIT: 934659f535d81d9a4a07389531acc2b9c304fa6d
RUNTIME_ROOT: /home/dragon/ai-film-runtime/dev21
STABLE_CURRENT: /home/dragon/ai-film-runtime/current
RUNTIME_MANIFEST_SHA256: 8227e8350208314db087612889d2b481393c67ec3a5eb0bfa84a869c1d0829a2
APP_MANIFEST_SHA256: 07fcf4a31c6ffabc3628ba12584d249680cea1344e26fb1d2cbe2983e30270fa
RUNTIME_VERIFY: "PRODLIKE_RUNTIME_VERIFY_PASS 283 86 NOT_RUN"
HEALTH_SCRIPT_SHA256: dfd11d418b820a3083f7016d1a0ab3355f3bd9b650e3c4ffc2de67ba042b34d5
BACKUP_SCRIPT_SHA256: ce3fb2fbac2e6514ceeae930efd483fcc3a95017d87b638331bff2f29620f327
HEALTH_SERVICE_SHA256: 31e73156d59dfe8ad051fbaef3745e1d879e07931bd7dd9634e2e04d9a461356
HEALTH_TIMER_SHA256: d99307b488f902f9a7879bcad00e689150497ebb609a7263e1aecccc65e53a12
BACKUP_SERVICE_SHA256: 3b676b732d073c9bdee366cdc842120dbaad43acb185fc2a000358713b7cf252
BACKUP_TIMER_SHA256: 9aad58f9c2eb94e8aeeefba036a256349d682d13790b1d7f3b09c36ff6ad667d
HEALTH_SYSTEMD_SECURITY: "4.1 OK"
BACKUP_SYSTEMD_SECURITY: "4.1 OK"
HEALTH_TIMER: "enabled active / 10min"
BACKUP_TIMER: "enabled active / 24h"
INTEGRITY_TIMER: "enabled active / 15min"
V02_AUTHORITY_TIMER: "enabled active / 5min"
SYSTEMD_USER_LINGER: true
HEALTH_LATEST_STATUS: PASS
HEALTH_LATEST_SHA256: 02352d1e10b5ed62a88b3f0a72c8889c5cb3bb223309b3d3fb8fe499c07f93ed
HEALTH_AUTHORITY_STATUS: BLOCKED
HEALTH_AUTHORITY_REASON: APPROVAL_ENVELOPE_MISSING
OPERATIONS_SCRIPTS_NOT_GROUP_OR_OTHER_WRITABLE: true
NATIVE_INVENTORY_MODE: "0600"
HEALTH_DIR_MODE: "0700"
BACKUP_DIR_MODE: "0700"
CONTROL_BACKUP_RETENTION: 14
LATEST_CONTROL_BACKUP: control-state-20260916T145912Z.tar.gz
LATEST_CONTROL_BACKUP_SHA256: 4c1f1c5c818b3615dcdd787718a0e5bf5a65082992a052a23b20a26214b91823
LATEST_CONTROL_BACKUP_FILES: 21
CONTROL_BACKUP_RESTORE_PROBE: PASS
CONTROL_BACKUP_INCLUDES_NATIVE_AUTHORITY: false
CONTROL_BACKUP_INCLUDES_PROTECTED_IDENTITY: false
NATIVE_LAB_AUTHORITY: false
NATIVE_EXECUTION_STARTED: false
HOST_READY: false
```

## What changed

Production-like operations were hardened without changing the exact dev21 app tree or native authority. The mutable native inventory evidence was tightened from `0644` to `0600`. A machine-readable health collector now verifies the stable release, exact runtime integrity, authority-signal consistency, operational-script permissions, disk headroom and all four user-systemd timers. Its latest result is PASS while correctly reporting V02 as `BLOCKED / APPROVAL_ENVELOPE_MISSING` rather than treating the governance block as runtime failure.

A daily control-state backup now archives only a fixed safe whitelist: release/runtime manifests, release history, health state, non-sensitive V02 watcher evidence, the operational scripts and the eight AI-FILM user-systemd units. It deliberately excludes the protected approval inbox, protected authority objects, credentials, raw SID/MachineGuid and native authority. Archives and sidecars are mode `0600`; directories are mode `0700`; retention is the newest 14 archives.

The current backup was extracted into an isolated temporary restore probe, every restored file was rehashed against the embedded manifest, unsafe archive paths were rejected, forbidden protected-content indicators were checked, and the probe passed before being deleted. This proves the backup is restorable rather than merely hashable.

## Runtime/service boundary

Exact dev21 is a gated CLI (`preflight`, `dry-run`, `apply`, `verify`, `support-bundle`, `recovery-notes`), not a reviewed always-on network server. No synthetic application daemon or listener was created. The production-like layer therefore supervises integrity, health, authority state and recoverability only. Existing unrelated listeners/processes outside `/home/dragon/ai-film-*` were not modified.

This record is operational-readiness evidence only. It does not create `LAB_EXECUTION_AUTHORITY_VERIFIED`, does not start `AI-FILM-P00-LAB`, does not write the HKLM trust anchor, does not execute any of the 86 native acceptance cases, and does not advance `RUN-P00-VALIDATION-001` past V02.