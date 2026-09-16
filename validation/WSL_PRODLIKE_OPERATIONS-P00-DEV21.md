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
HEALTH_SCRIPT_SHA256: d62495ee7d85bfcdadf460a216e360d75211c52f65a3836539db05bbcd343cf5
BACKUP_SCRIPT_SHA256: 7b27e192632f2594d4d2d0f4fc77c74afab0658071944c7ea7cf5de7db2749d1
BACKUP_VERIFY_SCRIPT_SHA256: 9aef87cc5af76de165145461e42d7534c8d8a61b95d6200e20d2b50f99151881
RECOVERY_VERIFY_SCRIPT_SHA256: 8297533df3c2c9d6bb838aea48b643031fac0d100c64f2be932439bbbb4d2ffe
HOST_MIRROR_SCRIPT_SHA256: dd6436cd20a5041e0b0b88f31a0d62c2b94c1ce8d0525ee91bd2b0c5ce54aa57
HOST_MIRROR_VERIFY_SCRIPT_SHA256: b473ba2d7937f4a2ab4442b1da3ac572fd4def66d9b1bf3c44ea75bba2909dca
REBUILD_VERIFY_SCRIPT_SHA256: 8db9a92b236e2b718aabb9fcc177ce797bd09e27e68e8edba0a16351d3b1e473
INTEGRITY_SERVICE_SHA256: c54a9ca3d2fe38d7f7f36b057e6e3f1b8d4aa1ae1fcbb8661273dac82235bd4f
AUTHORITY_WATCH_SERVICE_SHA256: 911b262eee734028b278a4acc4251c24b263b997e326b19e5df7570ec896619c
HEALTH_SERVICE_SHA256: 31e73156d59dfe8ad051fbaef3745e1d879e07931bd7dd9634e2e04d9a461356
BACKUP_SERVICE_SHA256: 3b676b732d073c9bdee366cdc842120dbaad43acb185fc2a000358713b7cf252
RECOVERY_SERVICE_SHA256: b0edc5b3516c1222760a2f3939aed6ca37e29f126e4e76a4e0322b2a89ecbc0e
HOST_MIRROR_SERVICE_SHA256: cc7f2ccabc21843b00331f8ce2223085e933fe59fd3ba38d045b99989b5128f1
REBUILD_SERVICE_SHA256: bd7c3a7b8ece1d136a29e0fe5dea0a6210cead7c8f5152f99c6ec8f497796fca
HEALTH_TIMER_SHA256: d99307b488f902f9a7879bcad00e689150497ebb609a7263e1aecccc65e53a12
BACKUP_TIMER_SHA256: 9aad58f9c2eb94e8aeeefba036a256349d682d13790b1d7f3b09c36ff6ad667d
RECOVERY_TIMER_SHA256: 8609834b5903565266155d9547f9a9268d7f9537e446aa84812b6e0aba43f56d
HOST_MIRROR_TIMER_SHA256: 024fc001ccb5749791c55b11fab94430c5d907f4437036b50ce7aab973923186
REBUILD_TIMER_SHA256: df74a3e7cbbaa2f290bdf1983c5ac81ac45d7ad8a2ace2a168833c78dfcb90b3
BOUNDED_EXECUTION_DROPINS:
  2MIN_SHA256: 8eb4f434128696bbed55d83fbaac4bc995446af73f4dac7bf522babe71ab7a85
  5MIN_SHA256: b29cfb8eb000cdee0704b5f92a66df30106f9fd09677311468346363fdca61f5
  10MIN_SHA256: f6ddc0822cc97e489773b9bbbdefb3ab47d6eff9770def066ff79602f9ff57ed
  EFFECTIVE_TIMEOUTS: "integrity=5m authority-watch=2m health=5m backup=10m recovery=10m host-mirror=5m rebuild=10m"
SYSTEMD_SECURITY: "integrity/health/backup/recovery/host-mirror/rebuild 4.1 OK; authority-watch 4.9 OK"
TIMERS: "integrity=15m authority-watch=5m health=10m backup=24h recovery=boot+6h host-mirror=2h rebuild=boot+12h; all enabled/active"
SYSTEMD_USER_LINGER: true
HEALTH_STATUS: PASS
HEALTH_SAMPLE_SHA256: e1b6151fa3c5ef291f815afd91ad01ca987024fabb3e817ca3aa74e8f2cdf944
HEALTH_AUTHORITY_STATUS: BLOCKED
HEALTH_AUTHORITY_REASON: APPROVAL_ENVELOPE_MISSING
HEALTH_CHECKS: "runtime integrity + authority signal + local backup freshness + NTFS mirror freshness + rebuild-set integrity + service timeouts + previous supervised job results"
BACKUP_MAX_AGE_HOURS: 30
HOST_MIRROR_MAX_AGE_HOURS: 30
CONTROL_BACKUP_RETENTION: 14
BACKUP_SAMPLE: control-state-20260916T200952Z.tar.gz
BACKUP_SAMPLE_SHA256: 29a92f78683ff71ba118023516cd32783bc45cc8232dbebf3ddf90b9b52309e1
BACKUP_SAMPLE_FILES: 39
CONTROL_BACKUP_VERIFY: PASS
CONTROL_BACKUP_RESTORE_PROBE: PASS
CONTROL_BACKUP_SECRET_SCAN: PASS
CONTROL_BACKUP_INCLUDES_NATIVE_AUTHORITY: false
CONTROL_BACKUP_INCLUDES_PROTECTED_IDENTITY: false
RECOVERY_VERIFY: PASS
HOST_MIRROR_RECORD: validation/WSL_PRODLIKE_HOST_MIRROR-P00-DEV21.md
HOST_MIRROR_FILESYSTEM: NTFS
HOST_MIRROR_VERIFY: PASS
HOST_MIRROR_RESTORE_PROBE: PASS
HOST_MIRROR_SECRET_SCAN: PASS
HOST_MIRROR_ACL: "SYSTEM + operator only / inheritance disabled"
REBUILD_SET_RECORD: validation/WSL_PRODLIKE_REBUILD_SET-P00-DEV21.md
REBUILD_SET_FILESYSTEM: NTFS
REBUILD_SET_INDEX_SHA256: 40cc6df68e8ca536acf183e8cbf63ce157845e4f33d2659c92efcb41fbc3ed54
REBUILD_SET_VERIFY: PASS
REBUILD_SET_COLD_PROBE: PASS
REBUILD_SET_ISOLATED_VENV: PASS
REBUILD_SET_LIVE_VENV_USED: false
REBUILD_SET_PYTHONPATH_USED: false
REBUILD_SET_PACKAGE_SHA256: f6ee158a318614f8bbef28be7af82549e0a268425da28147a2fa7b14c7b3d3e3
REBUILD_SET_RECONSTRUCTED_VERSION: 0.1.0.dev21
REBUILD_SET_RECONSTRUCTED_INVENTORY: "86 NOT_RUN"
VENV_REBUILD_VERIFIER_RECOVERABLE_FROM_NTFS_CONTROL_MIRROR: true
PERIODIC_JOB_RESULTS: "integrity=success authority-watch=success backup=success recovery=success host-mirror=success rebuild=success"
NATIVE_LAB_AUTHORITY: false
NATIVE_EXECUTION_STARTED: false
HOST_READY: false
```

## What changed

Production-like operations are hardened without changing the exact dev21 app tree or native authority. The health collector verifies the stable release, exact runtime integrity, authority-signal consistency, operational-script permissions, disk headroom, all seven user-systemd timers, previous supervised job results, effective service timeouts, freshness/integrity of local and Windows control backups, and integrity of the Windows runtime rebuild set. V02 being `BLOCKED / APPROVAL_ENVELOPE_MISSING` is treated as a governance state rather than a runtime failure.

Daily control-state backups contain only a fixed safe whitelist of runtime/control metadata, operational scripts, systemd units and timeout drop-ins. They exclude the protected approval inbox, authority objects, credentials, raw SID/MachineGuid and native authority. The current 39-file local/NTFS backup pair has SHA `29a92f78...`, passed hash/member verification and recovery checks, and contains the exact strengthened rebuild verifier SHA `8db9a92b...`.

The NTFS rebuild set closes the WSL-distro-loss reconstruction gap. The cold probe now goes beyond source execution: it creates a brand-new venv with `python3 -m venv --without-pip`, writes the same `app/src` `.pth` shape as the live runtime, and runs version/preflight/inventory through the new venv without using the live dev21 venv or `PYTHONPATH`. It still reconstructs `0.1.0.dev21`, `host_ready=false`, and `86 NOT_RUN` with zero parent cases and no qualification.

Exact dev21 remains a gated CLI rather than a reviewed always-on network server, so no synthetic application daemon/listener was created. Existing unrelated listeners/processes outside `/home/dragon/ai-film-*` were not modified. The NTFS control mirror and rebuild set remain same-host second-filesystem recovery measures, **not** off-host or independent-physical-device disaster recovery.

This record is operational-readiness evidence only. It does not create `LAB_EXECUTION_AUTHORITY_VERIFIED`, start `AI-FILM-P00-LAB`, write the HKLM trust anchor, execute any native acceptance case, issue qualification or advance `RUN-P00-VALIDATION-001` past V02.
