# Phase00 dev21 — production-like WSL operations hardening

```yaml
OPS_RECORD_ID: WSL-PRODLIKE-OPS-P00-DEV21-001
STATUS: READY_NON_NATIVE_PRODLIKE_OPERATIONS
SOURCE_COMMIT: 934659f535d81d9a4a07389531acc2b9c304fa6d
RUNTIME_ROOT: /home/dragon/ai-film-runtime/dev21
RUNTIME_MANIFEST_SHA256: 8227e8350208314db087612889d2b481393c67ec3a5eb0bfa84a869c1d0829a2
APP_MANIFEST_SHA256: 07fcf4a31c6ffabc3628ba12584d249680cea1344e26fb1d2cbe2983e30270fa
RUNTIME_VERIFY: "PRODLIKE_RUNTIME_VERIFY_PASS 283 86 NOT_RUN"

HEALTH_SCRIPT_SHA256: cf694078218919a679b94021e2db11fdb499ff97b3a1b563434bffdc27ac9ada
BACKUP_SCRIPT_SHA256: b9cf4b968cb913b40be4e9bb8fee96d90b08d6f4ee153d812d3ddfdea409b33b
DR_REHEARSAL_SCRIPT_SHA256: 853726f437c25763f0d15d0058994bce8c4d4eefc91df4db52b7b2be1f2a3de7
FAILCLOSED_CAMPAIGN_SCRIPT_SHA256: 937fb4ad422eb072591081f2188cc55b0f12f4defe5d2ab1fb720263c4e63e55
REBUILD_VERIFY_SCRIPT_SHA256: 8db9a92b236e2b718aabb9fcc177ce797bd09e27e68e8edba0a16351d3b1e473
OFFHOST_EXPORT_BUILD_SCRIPT_SHA256: 41fc42c9c792db204b8759c97787125340a979f9119047aae0864400a966bce1
OFFHOST_EXPORT_VERIFY_SCRIPT_SHA256: beacaee9a1f68228d4466970fa83f3492d2591ea0296502b57ceb0b046202a67

SUPERVISED_TIMERS: 10
TIMER_CADENCE: "integrity=15m authority-watch=5m health=10m backup=24h recovery=boot+6h host-mirror=2h rebuild=boot+12h offhost-export=boot+6h full-dr=24h failclosed-campaign=7d"
SYSTEMD_USER_LINGER: true
BOOT_ORDERING: "health/recovery Wants+After runtime-integrity verification"
BOUNDED_EXECUTION: true
DR_REHEARSAL_TIMEOUT: 10min
FAILCLOSED_CAMPAIGN_TIMEOUT: 10min
DR_REHEARSAL_SYSTEMD_SECURITY: "4.1 OK"
FAILCLOSED_CAMPAIGN_SYSTEMD_SECURITY: "4.1 OK"
HEALTH_STATUS: PASS
HEALTH_SAMPLE_SHA256: a9629c573ddf5986c2e1bc77f1501c93acf57fc1e5fc02935fa3e71c7af73fc5
HEALTH_AUTHORITY_STATUS: BLOCKED
HEALTH_AUTHORITY_REASON: APPROVAL_ENVELOPE_MISSING

CONTROL_BACKUP_RETENTION: 14
CONTROL_BACKUP_MAX_AGE_HOURS: 30
CONTROL_BACKUP_SAMPLE: control-state-20260916T223556Z.tar.gz
CONTROL_BACKUP_SHA256: 0f368a952974dcfee4d53ccc6be402899dfe00ef901b7f9b73342b9b6482379a
CONTROL_BACKUP_FILES: 58
CONTROL_BACKUP_VERIFY: PASS
CONTROL_BACKUP_INCLUDES_NATIVE_AUTHORITY: false
CONTROL_BACKUP_INCLUDES_PROTECTED_IDENTITY: false
HOST_MIRROR_VERIFY: PASS
HOST_MIRROR_FILES: 58
RECOVERY_VERIFY: PASS

REBUILD_SET_VERIFY: PASS
REBUILD_SET_COLD_PROBE: PASS
REBUILD_SET_ISOLATED_VENV: PASS
TRANSFER_EXPORT_STATUS: TRANSFER_READY_WITH_OFFHOST_METADATA
TRANSFER_EXPORT_SHA256: f993040f082fe49650a9a6819290717694e04980f24c2ef7a5b90cf0a4509c05
TRANSFER_EXPORT_CONTROL_FILES: 58
TRANSFER_EXPORT_VERIFY: PASS
TRANSFER_EXPORT_DRILL: PASS

FULL_DR_REHEARSAL: PASS
FULL_DR_EVIDENCE_SHA256: 2fa4b29a39e4b3c75d0aec46c97707e66bd181497cd4cc41797de6e68891fa04
FULL_DR_CONTROL_FILES: 58
FULL_DR_TIMER_DEFINITIONS: 10
FULL_DR_APP_FILES: 283
FULL_DR_REBUILT_VERSION: 0.1.0.dev21
FULL_DR_REBUILT_INVENTORY: "86 NOT_RUN"
FAILCLOSED_CAMPAIGN: "8/8 PASS"
FAILCLOSED_EVIDENCE_SHA256: 28119b53c9db0f07f5398cd51e11dbace63d5c2b212311d46a908f113ba2be93

OFFHOST_METADATA_ANCHOR: STATIC_EXACT_CANDIDATE_IDENTITY_PRIVATE_GOOGLE_DRIVE
OFFHOST_ROTATING_EXPORT_HASH_PINNED: false
OFFHOST_BINARY_PAYLOAD_UPLOADED: false
OFFHOST_DR_CLAIMED: false
NATIVE_LAB_AUTHORITY: false
NATIVE_EXECUTION_STARTED: false
HOST_READY: false
```

## Current operating model

The non-native control plane now includes supervised positive and negative verification. Runtime health checks immutable runtime integrity, authority-signal consistency, backup/mirror/rebuild/export freshness, service timeouts/results, ten timers, daily full-DR rehearsal freshness and weekly fail-closed campaign freshness.

The safe control backup expanded to 58 whitelisted files to carry the new recovery/fault tooling, evidence, systemd units and ordering/timeout drop-ins. Local and NTFS copies match SHA `0f368a95...` and exclude protected authority/identity domains.

Full DR rehearsal restores the control plane into a disposable root and reconstructs dev21 from the portable export with a fresh venv. The weekly negative campaign runs eight deliberate corruption/staleness/unsafe-flag cases against disposable copies using the actual verifier modules; all eight are rejected and live artifacts are reverified afterward.

During the control-schema migration, the stricter rehearsal correctly rejected the prior 44-file export. The approved transition sequence is `backup -> mirror -> export -> rehearsal`; after refresh the rehearsal passed with 58 files and ten timer definitions. Checker/recovery requirements were not weakened to preserve green status.

The private Drive manifest is now a static exact-candidate/rebuild identity anchor rather than a rotating export checksum. Dynamic backup/export hashes remain host-side freshness-verified; binary off-host DR is still not claimed.

This record does not create LAB execution authority, start the disposable LAB, write HKLM, execute native acceptance cases, issue qualification or advance V02.
