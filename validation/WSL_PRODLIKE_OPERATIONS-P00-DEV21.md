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
HEALTH_SCRIPT_SHA256: ebbb37d707836ac6112fbb5d731ac4cdd9ad76f417506c30c8cfaed425b49254
BACKUP_SCRIPT_SHA256: 4c0225848d441dbc924633f37bfdd2da172e91fc5c2a4a8f642d061e010e3e1e
BACKUP_VERIFY_SCRIPT_SHA256: 9aef87cc5af76de165145461e42d7534c8d8a61b95d6200e20d2b50f99151881
RECOVERY_VERIFY_SCRIPT_SHA256: 8297533df3c2c9d6bb838aea48b643031fac0d100c64f2be932439bbbb4d2ffe
HOST_MIRROR_SCRIPT_SHA256: dd6436cd20a5041e0b0b88f31a0d62c2b94c1ce8d0525ee91bd2b0c5ce54aa57
HOST_MIRROR_VERIFY_SCRIPT_SHA256: b473ba2d7937f4a2ab4442b1da3ac572fd4def66d9b1bf3c44ea75bba2909dca
INTEGRITY_SERVICE_SHA256: c54a9ca3d2fe38d7f7f36b057e6e3f1b8d4aa1ae1fcbb8661273dac82235bd4f
AUTHORITY_WATCH_SERVICE_SHA256: 911b262eee734028b278a4acc4251c24b263b997e326b19e5df7570ec896619c
HEALTH_SERVICE_SHA256: 31e73156d59dfe8ad051fbaef3745e1d879e07931bd7dd9634e2e04d9a461356
BACKUP_SERVICE_SHA256: 3b676b732d073c9bdee366cdc842120dbaad43acb185fc2a000358713b7cf252
RECOVERY_SERVICE_SHA256: b0edc5b3516c1222760a2f3939aed6ca37e29f126e4e76a4e0322b2a89ecbc0e
HOST_MIRROR_SERVICE_SHA256: cc7f2ccabc21843b00331f8ce2223085e933fe59fd3ba38d045b99989b5128f1
HEALTH_TIMER_SHA256: d99307b488f902f9a7879bcad00e689150497ebb609a7263e1aecccc65e53a12
BACKUP_TIMER_SHA256: 9aad58f9c2eb94e8aeeefba036a256349d682d13790b1d7f3b09c36ff6ad667d
RECOVERY_TIMER_SHA256: 8609834b5903565266155d9547f9a9268d7f9537e446aa84812b6e0aba43f56d
HOST_MIRROR_TIMER_SHA256: 024fc001ccb5749791c55b11fab94430c5d907f4437036b50ce7aab973923186
BOUNDED_EXECUTION_DROPINS:
  2MIN_SHA256: 8eb4f434128696bbed55d83fbaac4bc995446af73f4dac7bf522babe71ab7a85
  5MIN_SHA256: b29cfb8eb000cdee0704b5f92a66df30106f9fd09677311468346363fdca61f5
  10MIN_SHA256: f6ddc0822cc97e489773b9bbbdefb3ab47d6eff9770def066ff79602f9ff57ed
  EFFECTIVE_TIMEOUTS: "integrity=5m authority-watch=2m health=5m backup=10m recovery=10m host-mirror=5m"
HEALTH_SYSTEMD_SECURITY: "4.1 OK"
BACKUP_SYSTEMD_SECURITY: "4.1 OK"
RECOVERY_SYSTEMD_SECURITY: "4.1 OK"
HOST_MIRROR_SYSTEMD_SECURITY: "4.1 OK"
HEALTH_TIMER: "enabled active / 10min"
BACKUP_TIMER: "enabled active / 24h"
RECOVERY_TIMER: "enabled active / boot+6h"
HOST_MIRROR_TIMER: "enabled active / 2h"
INTEGRITY_TIMER: "enabled active / 15min"
V02_AUTHORITY_TIMER: "enabled active / 5min"
SYSTEMD_USER_LINGER: true
HEALTH_STATUS: PASS
HEALTH_SAMPLE_SHA256: b9f5e59f27739d9f621472761ebfa07f5bfa90463eba27b075d039b4ab784228
HEALTH_AUTHORITY_STATUS: BLOCKED
HEALTH_AUTHORITY_REASON: APPROVAL_ENVELOPE_MISSING
HEALTH_CHECKS_BACKUP_FRESHNESS: true
HEALTH_CHECKS_HOST_MIRROR_FRESHNESS: true
HEALTH_CHECKS_PERIODIC_JOB_RESULT: true
HEALTH_CHECKS_SERVICE_TIMEOUTS: true
BACKUP_MAX_AGE_HOURS: 30
HOST_MIRROR_MAX_AGE_HOURS: 30
OPERATIONS_SCRIPTS_NOT_GROUP_OR_OTHER_WRITABLE: true
NATIVE_INVENTORY_MODE: "0600"
HEALTH_DIR_MODE: "0700"
BACKUP_DIR_MODE: "0700"
CONTROL_BACKUP_RETENTION: 14
BACKUP_SAMPLE: control-state-20260916T172440Z.tar.gz
BACKUP_SAMPLE_SHA256: a992d525d752c270605b14ba65949cf3b035cda0e0e6754bc462cca01521ac0c
BACKUP_SAMPLE_FILES: 35
CONTROL_BACKUP_VERIFY: PASS
CONTROL_BACKUP_RESTORE_PROBE: PASS
CONTROL_BACKUP_SECRET_SCAN: PASS
CONTROL_BACKUP_INCLUDES_NATIVE_AUTHORITY: false
CONTROL_BACKUP_INCLUDES_PROTECTED_IDENTITY: false
RECOVERY_VERIFY: PASS
HOST_MIRROR_RECORD: validation/WSL_PRODLIKE_HOST_MIRROR-P00-DEV21.md
HOST_MIRROR_FILESYSTEM: NTFS
HOST_MIRROR_RETENTION: 14
HOST_MIRROR_VERIFY: PASS
HOST_MIRROR_RESTORE_PROBE: PASS
HOST_MIRROR_SECRET_SCAN: PASS
HOST_MIRROR_ACL: "SYSTEM + operator only / inheritance disabled"
PERIODIC_JOB_RESULTS: "integrity=success authority-watch=success backup=success recovery=success host_mirror=success"
NATIVE_LAB_AUTHORITY: false
NATIVE_EXECUTION_STARTED: false
HOST_READY: false
```

## What changed

Production-like operations were hardened without changing the exact dev21 app tree or native authority. The mutable native inventory evidence is mode `0600`. A machine-readable health collector verifies the stable release, exact runtime integrity, authority-signal consistency, operational-script permissions, disk headroom, all six user-systemd timers, previous supervised job results, freshness/integrity of the newest control-state backup and Windows-host mirror, and the effective bounded-execution timeouts for all six services. Its sampled result is PASS while correctly reporting V02 as `BLOCKED / APPROVAL_ENVELOPE_MISSING` rather than treating the governance block as runtime failure.

Service base units remain byte-identical to their previously recorded identities, including the integrity-service hash embedded in `runtime-manifest.json`. Bounded execution is supplied by six separate systemd drop-ins: authority watch 2 minutes; integrity, health and host mirror 5 minutes; backup and recovery 10 minutes; all use `TimeoutStopSec=30s`. The timeout drop-ins are themselves included in the safe control backup, so deployment identity remains stable while hang containment is recoverable and machine-checked.

A daily control-state backup archives only a fixed safe whitelist: release/runtime manifests, release history, health state, non-sensitive V02 watcher evidence, operational/recovery/mirror scripts, AI-FILM user-systemd units and timeout drop-ins. It deliberately excludes the protected approval inbox, protected authority objects, credentials, raw SID/MachineGuid and native authority. Archives and sidecars are mode `0600`; directories are mode `0700`; retention is the newest 14 archives. The standalone verifier rejects stale backups older than 30 hours, permission drift, sidecar/hash mismatch, unsafe archive paths, member-set drift, per-member hash mismatch and any manifest claiming native authority or protected identity inclusion.

`aifilm-p00-recovery-verify.timer` runs after boot and every six hours. `aifilm-p00-host-mirror.timer` runs every two hours and mirrors only an already-verified safe control backup to an ACL-protected Windows NTFS directory. The current 35-file local/NTFS archive includes the timeout drop-ins and passed hash/member verification, direct NTFS restore probe and protected-domain/secret scan. Health, backup, recovery and mirror services have observed `systemd-analyze security` exposure `4.1 OK`.

The NTFS mirror is a second-filesystem recovery copy for WSL-distro failure; it is not represented as off-host or independent-physical-device disaster recovery. Existing unrelated listeners/processes outside `/home/dragon/ai-film-*` were not modified.

## Runtime/service boundary

Exact dev21 is a gated CLI (`preflight`, `dry-run`, `apply`, `verify`, `support-bundle`, `recovery-notes`), not a reviewed always-on network server. No synthetic application daemon or listener was created. The production-like layer supervises integrity, health, authority state, bounded execution, backup freshness, cross-filesystem mirroring and recoverability only.

This record is operational-readiness evidence only. It does not create `LAB_EXECUTION_AUTHORITY_VERIFIED`, does not start `AI-FILM-P00-LAB`, does not write the HKLM trust anchor, does not execute any of the 86 native acceptance cases, and does not advance `RUN-P00-VALIDATION-001` past V02.