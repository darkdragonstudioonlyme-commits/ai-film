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
HEALTH_SCRIPT_SHA256: 7c4a41aa66923deaf8cc82044641dde807c6810ec59d55414660a2b47af81dfb
BACKUP_SCRIPT_SHA256: e949c10373494a2d40ca086299b8177d9168ff4eabd0a3c601abc07c6f997227
BACKUP_VERIFY_SCRIPT_SHA256: 9aef87cc5af76de165145461e42d7534c8d8a61b95d6200e20d2b50f99151881
RECOVERY_VERIFY_SCRIPT_SHA256: 8297533df3c2c9d6bb838aea48b643031fac0d100c64f2be932439bbbb4d2ffe
HEALTH_SERVICE_SHA256: 31e73156d59dfe8ad051fbaef3745e1d879e07931bd7dd9634e2e04d9a461356
HEALTH_TIMER_SHA256: d99307b488f902f9a7879bcad00e689150497ebb609a7263e1aecccc65e53a12
BACKUP_SERVICE_SHA256: 3b676b732d073c9bdee366cdc842120dbaad43acb185fc2a000358713b7cf252
BACKUP_TIMER_SHA256: 9aad58f9c2eb94e8aeeefba036a256349d682d13790b1d7f3b09c36ff6ad667d
RECOVERY_SERVICE_SHA256: b0edc5b3516c1222760a2f3939aed6ca37e29f126e4e76a4e0322b2a89ecbc0e
RECOVERY_TIMER_SHA256: 8609834b5903565266155d9547f9a9268d7f9537e446aa84812b6e0aba43f56d
HEALTH_SYSTEMD_SECURITY: "4.1 OK"
BACKUP_SYSTEMD_SECURITY: "4.1 OK"
RECOVERY_SYSTEMD_SECURITY: "4.1 OK"
HEALTH_TIMER: "enabled active / 10min"
BACKUP_TIMER: "enabled active / 24h"
RECOVERY_TIMER: "enabled active / boot+6h"
INTEGRITY_TIMER: "enabled active / 15min"
V02_AUTHORITY_TIMER: "enabled active / 5min"
SYSTEMD_USER_LINGER: true
HEALTH_STATUS: PASS
HEALTH_SAMPLE_SHA256: 688f07acc10df18dbe9ee002060179dc63b53e7d70d39d414719b551f1fec9c5
HEALTH_AUTHORITY_STATUS: BLOCKED
HEALTH_AUTHORITY_REASON: APPROVAL_ENVELOPE_MISSING
HEALTH_CHECKS_BACKUP_FRESHNESS: true
HEALTH_CHECKS_PERIODIC_JOB_RESULT: true
BACKUP_MAX_AGE_HOURS: 30
OPERATIONS_SCRIPTS_NOT_GROUP_OR_OTHER_WRITABLE: true
NATIVE_INVENTORY_MODE: "0600"
HEALTH_DIR_MODE: "0700"
BACKUP_DIR_MODE: "0700"
CONTROL_BACKUP_RETENTION: 14
BACKUP_SAMPLE: control-state-20260916T163032Z.tar.gz
BACKUP_SAMPLE_SHA256: 624ac8eb570a19fce2ec33e0e66955b757c982a02b5102dc0d160f71281f3589
BACKUP_SAMPLE_FILES: 25
CONTROL_BACKUP_VERIFY: PASS
CONTROL_BACKUP_RESTORE_PROBE: PASS
CONTROL_BACKUP_SECRET_SCAN: PASS
CONTROL_BACKUP_INCLUDES_NATIVE_AUTHORITY: false
CONTROL_BACKUP_INCLUDES_PROTECTED_IDENTITY: false
RECOVERY_VERIFY: PASS
PERIODIC_JOB_RESULTS: "backup=success recovery=success"
NATIVE_LAB_AUTHORITY: false
NATIVE_EXECUTION_STARTED: false
HOST_READY: false
```

## What changed

Production-like operations were hardened without changing the exact dev21 app tree or native authority. The mutable native inventory evidence was tightened from `0644` to `0600`. A machine-readable health collector verifies the stable release, exact runtime integrity, authority-signal consistency, operational-script permissions, disk headroom, all five user-systemd timers, the previous backup/recovery service results, and freshness/integrity of the newest control-state backup. Its sampled result is PASS while correctly reporting V02 as `BLOCKED / APPROVAL_ENVELOPE_MISSING` rather than treating the governance block as runtime failure.

A daily control-state backup archives only a fixed safe whitelist: release/runtime manifests, release history, health state, non-sensitive V02 watcher evidence, operational/recovery scripts and AI-FILM user-systemd units. It deliberately excludes the protected approval inbox, protected authority objects, credentials, raw SID/MachineGuid and native authority. Archives and sidecars are mode `0600`; directories are mode `0700`; retention is the newest 14 archives. The standalone verifier rejects stale backups older than 30 hours, permission drift, sidecar/hash mismatch, unsafe archive paths, member-set drift, per-member hash mismatch, and any manifest claiming native authority or protected identity inclusion.

`aifilm-p00-recovery-verify.timer` runs after boot and every six hours. Its hardened service independently verifies the active release and newest backup and has observed `systemd-analyze security` exposure `4.1 OK`. The sampled backup was extracted into an isolated temporary restore probe, every restored file was rehashed against the embedded manifest, unsafe archive paths were rejected, and the probe passed before deletion. A separate content scan found no raw SID pattern, MachineGuid label, private-key marker, password assignment or token assignment.

## Runtime/service boundary

Exact dev21 is a gated CLI (`preflight`, `dry-run`, `apply`, `verify`, `support-bundle`, `recovery-notes`), not a reviewed always-on network server. No synthetic application daemon or listener was created. The production-like layer supervises integrity, health, authority state, backup freshness and recoverability only. Existing unrelated listeners/processes outside `/home/dragon/ai-film-*` were not modified.

This record is operational-readiness evidence only. It does not create `LAB_EXECUTION_AUTHORITY_VERIFIED`, does not start `AI-FILM-P00-LAB`, does not write the HKLM trust anchor, does not execute any of the 86 native acceptance cases, and does not advance `RUN-P00-VALIDATION-001` past V02.