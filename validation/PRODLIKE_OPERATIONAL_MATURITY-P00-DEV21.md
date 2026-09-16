# Phase00 dev21 — production-like operational maturity program

```yaml
PROGRAM_ID: PRODLIKE-OPMAT-P00-DEV21-003
SOURCE_COMMIT: 934659f535d81d9a4a07389531acc2b9c304fa6d
STATUS: PASS_NON_NATIVE
M1_CAPACITY_RETENTION_AUDIT: PASS
M2_HASH_CHAINED_EVIDENCE_HISTORY: PASS
M3_RESOURCE_CONTAINMENT: PASS
M4_USER_MANAGER_REEXEC_REHEARSAL: PASS
M5_INCIDENT_DETECTION_RECOVERY_DRILL: PASS
M6_RECOVERY_SCHEMA_RECONCILIATION: PASS
SUPERVISED_TIMERS: 11
SUPERVISED_PREVIOUS_JOB_RESULTS: 10
RESOURCE_BOUND_SERVICES: 11
MEMORY_MAX_PER_SERVICE: 256M
TASKS_MAX_PER_SERVICE: 128
EVIDENCE_LEDGER_RETENTION: 30
CONTROL_BACKUP_FILES: 85
CONTROL_BACKUP_SHA256: daa43ca4d72052881f7ac6aabfd2eae95c9ffcff7ca3f43e8a6d1d1a25ca58de
TRANSFER_EXPORT_SHA256: b4cf49cd4e177c7ea6777e5ead4da3bf5d1669088bfbd136ce180a322faa31c5
FULL_DR_REHEARSAL: PASS
FULL_DR_CONTROL_FILES: 85
FULL_DR_TIMER_DEFINITIONS: 11
FULL_DR_RESOURCE_DROPINS: 11
FAILCLOSED_CAMPAIGN: 8/8_PASS
NATIVE_EXECUTION_STARTED: false
OFF_HOST_DR_CLAIMED: false
```

## M1 — capacity and retention audit

WSL has roughly 912 GiB free and the Windows volume roughly 1.6 TiB free. AI-FILM recovery state remains small. The real gap was historical evidence: health, DR and negative-campaign evidence exposed only latest snapshots. Peak RSS was measured before setting bounds: rebuild/export/full-DR were roughly 20–22 MiB, fault campaign about 24 MiB and health about 44 MiB.

## M2/M3 — evidence continuity and resource containment

A daily safe operational evidence ledger now hash-chains snapshots of health, DR, fault-campaign and authority status. The ledger retains 30 records with a prune anchor and excludes protected authority objects/credentials. A separate verifier checks sidecars, chain continuity, last-record state and freshness.

All AI-FILM user services have accounting plus `MemoryMax=256M` and `TasksMax=128`, leaving more than five times the observed peak while bounding runaway processes. Runtime health verifies those effective limits.

## M4/M5 — manager resilience and incident behavior

A controlled `systemctl --user daemon-reexec` preserved all 11 timers as enabled/active/Persistent and preserved dependency/resource drop-ins. Health remained PASS.

An incident drill temporarily injected `ExecStartPre=/bin/false` into the supervised weekly fault-campaign service. The service failed, health changed to FAIL, and a ledger record captured that failure. After removing the temporary drop-in and rerunning the real job, health returned to PASS and the next ledger record chained through the incident record. No runtime/backup/export/native artifact was corrupted.

## M6 — producer-before-consumer recovery migration

The control schema expansion intentionally made the new DR consumer reject the old export with `control-required-file`. The accepted migration order was producer-first: control backup -> NTFS mirror -> deterministic export -> full DR rehearsal -> negative campaign -> health/ledger. The new recovery payload contains 85 control files, 11 timer definitions, all 11 resource drop-ins and bounded ledger history. Full DR verifies the restored ledger chain before reconstructing exact dev21.

This program strengthens non-native operations only. It does not approve V02, create READY/trust state, start `AI-FILM-P00-LAB`, execute native procedures, issue qualification or claim HOST_READY/off-host binary DR.