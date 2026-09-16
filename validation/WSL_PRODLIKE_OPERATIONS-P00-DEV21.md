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
HEALTH_SCRIPT_SHA256: a24483db2fc586706e663403764d74ea86a7860a6937058f04466b5fb387db7e
BACKUP_SCRIPT_SHA256: 6383b715fff0c2cfc9fa8d30a1c301f7270e37535af7e4ac5b634fcf7ede0403
BACKUP_VERIFY_SCRIPT_SHA256: 9aef87cc5af76de165145461e42d7534c8d8a61b95d6200e20d2b50f99151881
RECOVERY_VERIFY_SCRIPT_SHA256: 8297533df3c2c9d6bb838aea48b643031fac0d100c64f2be932439bbbb4d2ffe
HOST_MIRROR_SCRIPT_SHA256: dd6436cd20a5041e0b0b88f31a0d62c2b94c1ce8d0525ee91bd2b0c5ce54aa57
HOST_MIRROR_VERIFY_SCRIPT_SHA256: b473ba2d7937f4a2ab4442b1da3ac572fd4def66d9b1bf3c44ea75bba2909dca
REBUILD_VERIFY_SCRIPT_SHA256: 8db9a92b236e2b718aabb9fcc177ce797bd09e27e68e8edba0a16351d3b1e473
OFFHOST_EXPORT_BUILD_SCRIPT_SHA256: 41fc42c9c792db204b8759c97787125340a979f9119047aae0864400a966bce1
OFFHOST_EXPORT_VERIFY_SCRIPT_SHA256: beacaee9a1f68228d4466970fa83f3492d2591ea0296502b57ceb0b046202a67
OFFHOST_EXPORT_SERVICE_SHA256: 60df6cea651bcc669f5809e062325d962d5389485e6cae4d9d40e084838c9b51
OFFHOST_EXPORT_TIMER_SHA256: 086d01ab44d122bba0a7bb8e50168548af132fccd8a1955bc124ae8afc95e305
BOUNDED_EXECUTION_DROPINS:
  2MIN_SHA256: 8eb4f434128696bbed55d83fbaac4bc995446af73f4dac7bf522babe71ab7a85
  5MIN_SHA256: b29cfb8eb000cdee0704b5f92a66df30106f9fd09677311468346363fdca61f5
  10MIN_SHA256: f6ddc0822cc97e489773b9bbbdefb3ab47d6eff9770def066ff79602f9ff57ed
  EFFECTIVE_TIMEOUTS: "integrity=5m authority-watch=2m health=5m backup=10m recovery=10m host-mirror=5m rebuild=10m offhost-export=10m"
SYSTEMD_SECURITY: "prodlike services including offhost-export 4.1 OK; authority-watch 4.9 OK"
TIMERS: "integrity=15m authority-watch=5m health=10m backup=24h recovery=boot+6h host-mirror=2h rebuild=boot+12h offhost-export=boot+6h; all enabled/active"
SYSTEMD_USER_LINGER: true
HEALTH_STATUS: PASS
HEALTH_SAMPLE_SHA256: 1c376bd66acb86fd9ce2cb750255fe2cbc5298f46f117006694ac44d1fdcb436
HEALTH_AUTHORITY_STATUS: BLOCKED
HEALTH_AUTHORITY_REASON: APPROVAL_ENVELOPE_MISSING
HEALTH_CHECKS: "runtime integrity + authority signal + local backup freshness + NTFS mirror freshness + rebuild-set integrity + transfer-export freshness/integrity + service timeouts + previous supervised job results"
BACKUP_MAX_AGE_HOURS: 30
HOST_MIRROR_MAX_AGE_HOURS: 30
CONTROL_BACKUP_RETENTION: 14
BACKUP_SAMPLE: control-state-20260916T203634Z.tar.gz
BACKUP_SAMPLE_SHA256: c31250cf400221f7872ed0001fbdf513ca158b8735dc7a4fd4694a11ecc8ed6f
BACKUP_SAMPLE_FILES: 44
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
REBUILD_SET_RECORD: validation/WSL_PRODLIKE_REBUILD_SET-P00-DEV21.md
REBUILD_SET_FILESYSTEM: NTFS
REBUILD_SET_VERIFY: PASS
REBUILD_SET_COLD_PROBE: PASS
REBUILD_SET_ISOLATED_VENV: PASS
REBUILD_SET_LIVE_VENV_USED: false
REBUILD_SET_PYTHONPATH_USED: false
OFFHOST_EXPORT_RECORD: validation/WSL_PRODLIKE_OFFHOST_EXPORT-P00-DEV21.md
OFFHOST_EXPORT_STATUS: TRANSFER_READY_WITH_OFFHOST_METADATA
OFFHOST_EXPORT_DETERMINISTIC: true
OFFHOST_EXPORT_SHA256: 0f603dec5e48d64bccc52271abfd0e83deb93a0655193c4cb7741c850500bbf8
OFFHOST_EXPORT_PAYLOAD_FILES: 7
OFFHOST_EXPORT_CONTROL_FILES: 44
OFFHOST_EXPORT_VERIFY: PASS
OFFHOST_EXPORT_DRILL: PASS
OFFHOST_METADATA_ANCHOR: PRIVATE_GOOGLE_DRIVE
OFFHOST_BINARY_PAYLOAD_UPLOADED: false
OFFHOST_DR_CLAIMED: false
PERIODIC_JOB_RESULTS: "integrity=success authority-watch=success backup=success recovery=success host-mirror=success rebuild=success offhost-export=success"
NATIVE_LAB_AUTHORITY: false
NATIVE_EXECUTION_STARTED: false
HOST_READY: false
```

## What changed

Production-like operations remain fail-closed and non-native. Runtime health now supervises eight user-systemd timers and also requires a fresh verified transfer-ready DR export, the previous export job result and its bounded execution timeout. The export service builds only from already-verified control backup and exact NTFS rebuild artifacts, runs the heavy self-contained fresh-venv drill, and has observed `systemd-analyze security` exposure `4.1 OK`.

The safe control backup now contains 44 whitelisted control files because it includes the transfer-export builder/verifier, service/timer and timeout drop-in. Local backup and NTFS mirror share SHA `c31250cf...`; both pass member/hash checks, recovery verification and protected-domain exclusions. Authority inbox, authority objects, credentials and protected identity remain excluded.

The transfer export is deterministic: identical payload state generates identical ZIP bytes/SHA. Its current SHA is `0f603dec...`; it contains seven payloads, including the 44-file verified control backup and the exact non-secret dev21 reconstruction set. Heavy drill from the export alone reconstructs a fresh isolated venv, verifies 283/283 app bytes, reports version `0.1.0.dev21`, `86 NOT_RUN` and `host_ready=false`.

A private Google Drive document stores the currently anchored checksum/identity metadata but not the binary payload. Therefore `OFFHOST_DR_CLAIMED=false` remains mandatory. Exact dev21 is still a gated CLI, no synthetic network daemon was introduced, and no production-like control creates native authority.

This record does not create `LAB_EXECUTION_AUTHORITY_VERIFIED`, start `AI-FILM-P00-LAB`, write HKLM, execute any native acceptance case, issue qualification or advance `RUN-P00-VALIDATION-001` past V02.