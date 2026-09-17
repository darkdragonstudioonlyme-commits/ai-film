# Phase00 dev21 — production-like WSL operations hardening

```yaml
OPS_RECORD_ID: WSL-PRODLIKE-OPS-P00-DEV21-001
STATUS: READY_NON_NATIVE_PRODLIKE_OPERATIONS
SOURCE_COMMIT: 934659f535d81d9a4a07389531acc2b9c304fa6d
RUNTIME_VERIFY: "PRODLIKE_RUNTIME_VERIFY_PASS 283 86 NOT_RUN"
OPERATIONAL_MATURITY_RECORD: validation/PRODLIKE_OPERATIONAL_MATURITY-P00-DEV21.md
EXECUTION_SLA_RETENTION_RECORD: validation/PRODLIKE_EXECUTION_SLA_RETENTION-P00-DEV21.md
HEALTH_SCRIPT_SHA256: 03510f3525682cf9358949ed8fb55fe511c2db1346c922c1dfa806612fa850dd
SUPERVISED_TIMERS: 11
SUPERVISED_PREVIOUS_JOB_RESULTS: 10
SERVICE_EXECUTION_FRESHNESS_MONITORED: 11
SERVICE_EXECUTION_FRESHNESS_STATUS: PASS
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
BACKUP_RETENTION: 14
BACKUP_RETENTION_OVERFLOW_TEST: PASS
EVIDENCE_LEDGER_RETENTION: 30
EVIDENCE_LEDGER_RETENTION_OVERFLOW_TEST: PASS
EVIDENCE_LEDGER_PRUNED_CHAIN_ANCHOR: PASS
EVIDENCE_LEDGER_HASH_CHAIN: PASS
RESOURCE_CGROUP_BINDING_PROBE: PASS
FAILCLOSED_CAMPAIGN: "8/8 PASS"
NATIVE_LAB_AUTHORITY: false
NATIVE_EXECUTION_STARTED: false
HOST_READY: false
```

## Stable operating invariants

Health now checks execution freshness as well as timer state and previous results. The freshness source is `ExecMainExitTimestampMonotonic`; a timer may be enabled/active and still fail health if its service completion is stale. A service with no completion in the current boot is permitted only during bounded startup grace. Production-function negative tests returned `STALE/ok=false` and `NEVER_COMPLETED_THIS_BOOT/ok=false` for the expected cases.

Retention is tested, not merely configured. The real control-backup producer retained exactly 14 archives in a disposable overflow root. The real operational-ledger producer/verifier retained exactly 30 records after overflow and preserved chain continuity through `anchor_before_oldest_sha256`.

Resource containment is verified at the kernel binding layer without destructive exhaustion. A benign transient unit configured with `MemoryMax=32M` and `TasksMax=8` exposed the same values through both systemd and cgroup `memory.max`/`pids.max`. Live AI-FILM services remain at the wider reviewed `256M/128` bounds.

## Rotating recovery sample

The current producer-first refresh passed backup -> NTFS mirror -> deterministic export -> full DR -> negative campaign -> evidence ledger -> health. At that observation point:

```yaml
LATEST_BACKUP_SAMPLE: control-state-20260917T090226Z.tar.gz
LATEST_BACKUP_SAMPLE_FILES: 87
LATEST_BACKUP_SAMPLE_SHA256: c213efff4aeff5585bf14efea172889dffe3b33af815dabaf30f3b5e14c887d2
LATEST_EXPORT_SAMPLE_SHA256: 023eb0d5275eeb1b27974c908664f17b46a4bbe11a12376d4e085602a7135d11
FULL_DR_SAMPLE_CONTROL_FILES: 87
FULL_DR_TIMER_DEFINITIONS: 11
FULL_DR_RESOURCE_DROPINS: 11
EVIDENCE_LEDGER_RECORDS_AT_SAMPLE: 7
```

These recovery bytes are intentionally rotating because bounded ledger history is embedded in the backup. The current file count and backup/export SHA are therefore traceability samples, not immutable candidate identities. Stable truth is exact dev21 identity plus verifier success, freshness/retention limits, 11 timer/resource definitions, ledger-chain validity and producer-before-consumer recovery migration.

No operation here creates LAB authority, READY/trust state, native execution, qualification, SITE evidence or HOST_READY.