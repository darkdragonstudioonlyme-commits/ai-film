# Phase00 dev21 — production-like WSL operations hardening

```yaml
OPS_RECORD_ID: WSL-PRODLIKE-OPS-P00-DEV21-001
STATUS: READY_NON_NATIVE_PRODLIKE_OPERATIONS
SOURCE_COMMIT: 934659f535d81d9a4a07389531acc2b9c304fa6d
RUNTIME_VERIFY: "PRODLIKE_RUNTIME_VERIFY_PASS 283 86 NOT_RUN"
OPERATIONAL_MATURITY_RECORD: validation/PRODLIKE_OPERATIONAL_MATURITY-P00-DEV21.md
HEALTH_SCRIPT_SHA256: d44432fdbcee063eabefbd813da942f18170e604c412377cb1c0cb008d3801c4
BACKUP_SCRIPT_SHA256: 01c6c5416c11553fc42455f4753c558657b931d36a3e33b541cadfd02973d9a1
DR_REHEARSAL_SCRIPT_SHA256: 84a190a3df68867572e250a9f28070be76c34d4e4e9d661f7e04f4436541865a
FAILCLOSED_CAMPAIGN_SCRIPT_SHA256: 937fb4ad422eb072591081f2188cc55b0f12f4defe5d2ab1fb720263c4e63e55
EVIDENCE_LEDGER_SCRIPT_SHA256: ad308636ce51cbe1ace8b9790b8225ed6c4c09d61956e3d29bb49f3fc00d1d05
EVIDENCE_LEDGER_VERIFY_SHA256: fb6198d92188f147c9b5a7212a996b89a57e101c36014346295fdd1a3085c257
SUPERVISED_TIMERS: 11
SUPERVISED_PREVIOUS_JOB_RESULTS: 10
RESOURCE_BOUND_SERVICES: 11
MEMORY_MAX_PER_SERVICE: 256M
TASKS_MAX_PER_SERVICE: 128
RESOURCE_ACCOUNTING: "memory/cpu/tasks enabled"
SYSTEMD_USER_LINGER: true
USER_MANAGER_DAEMON_REEXEC_REHEARSAL: PASS
ALL_TIMERS_PERSISTENT_ENABLED_ACTIVE_AFTER_REEXEC: true
HEALTH_STATUS: PASS
HEALTH_AUTHORITY_STATUS: BLOCKED
HEALTH_AUTHORITY_REASON: APPROVAL_ENVELOPE_MISSING
CONTROL_BACKUP_RETENTION: 14
CONTROL_BACKUP_MAX_AGE_HOURS: 30
CONTROL_BACKUP_SAMPLE: control-state-20260916T232534Z.tar.gz
CONTROL_BACKUP_SHA256: daa43ca4d72052881f7ac6aabfd2eae95c9ffcff7ca3f43e8a6d1d1a25ca58de
CONTROL_BACKUP_FILES: 85
CONTROL_BACKUP_VERIFY: PASS
HOST_MIRROR_VERIFY: PASS
HOST_MIRROR_FILES: 85
REBUILD_SET_VERIFY: PASS
REBUILD_SET_COLD_PROBE: PASS
TRANSFER_EXPORT_SHA256: b4cf49cd4e177c7ea6777e5ead4da3bf5d1669088bfbd136ce180a322faa31c5
TRANSFER_EXPORT_CONTROL_FILES: 85
TRANSFER_EXPORT_VERIFY: PASS
TRANSFER_EXPORT_DRILL: PASS
FULL_DR_REHEARSAL: PASS
FULL_DR_CONTROL_FILES: 85
FULL_DR_TIMER_DEFINITIONS: 11
FULL_DR_RESOURCE_DROPINS: 11
FAILCLOSED_CAMPAIGN: "8/8 PASS"
EVIDENCE_LEDGER: PASS
EVIDENCE_LEDGER_RETENTION: 30
EVIDENCE_LEDGER_HASH_CHAIN: PASS
INCIDENT_DRILL: PASS
INCIDENT_HEALTH_FAIL_CAPTURED: true
INCIDENT_RECOVERY_HEALTH_PASS: true
OFFHOST_METADATA_ANCHOR: STATIC_EXACT_CANDIDATE_IDENTITY_PRIVATE_GOOGLE_DRIVE
OFFHOST_BINARY_PAYLOAD_UPLOADED: false
OFFHOST_DR_CLAIMED: false
NATIVE_LAB_AUTHORITY: false
NATIVE_EXECUTION_STARTED: false
HOST_READY: false
```

## Current operating model

Production-like operations now combine positive verification, negative verification, bounded resource containment, restart resilience and historical incident evidence. Health checks 11 enabled/active persistent timers, 10 supervised previous-job results, 11 effective resource limits, runtime integrity, backup/mirror/rebuild/export freshness, DR/fault evidence and evidence-ledger chain integrity.

Peak RSS was measured before applying limits; the highest observed job was about 44 MiB. Every AI-FILM oneshot now has accounting plus `MemoryMax=256M` and `TasksMax=128`, providing a large operating margin while bounding runaway processes.

A daily evidence ledger stores safe hash-chained operational snapshots with retention 30. A controlled incident drill forced the supervised fail-closed campaign service to fail; health correctly changed to FAIL and the ledger captured the incident. Removing the temporary fault, rerunning the real service and health restored PASS, and the next ledger record chained through the failure record.

Recovery schema migration followed producer-first ordering. The stricter DR consumer rejected the older recovery export before migration. After backup -> mirror -> export regeneration, current recovery state contains 85 files, 11 timer definitions, 11 resource drop-ins and bounded ledger history; full DR verifies the restored ledger chain before reconstructing exact dev21.

None of these controls creates LAB authority, READY/trust state, native execution, qualification, SITE evidence or HOST_READY.