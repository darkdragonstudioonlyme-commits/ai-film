# Phase00 dev21 — Execution SLA, retention and rotating-state semantics

```yaml
PROGRAM_ID: PRODLIKE-SLA-RETENTION-P00-DEV21-003
STATUS: PASS
SOURCE_COMMIT: 934659f535d81d9a4a07389531acc2b9c304fa6d
NATIVE_EXECUTION_STARTED: false
V02_STATUS: BLOCKED_EXTERNAL_AUTHORITY
```

## N1 — timer execution-SLA audit

All eleven user-systemd jobs were measured against their real timer cadence and `AccuracySec`. Each service was within cadence at audit time. Health was then extended to verify last completed execution with `ExecMainExitTimestampMonotonic`, not merely timer enabled/active state.

The SLA rule is cadence plus jitter/grace. A service that has never completed in the current boot is allowed only through its configured `OnBootSec + AccuracySec + startup grace`; after that it is fail-closed. Current health reports all eleven services `FRESH`.

## N2 — freshness enforcement

Runtime health script SHA-256 is `03510f3525682cf9358949ed8fb55fe511c2db1346c922c1dfa806612fa850dd`. It exposes `service_execution_freshness` for all eleven services and requires `service_execution_freshness_ok=true`.

A direct negative test of the production freshness function verified both failure classes: an old monotonic completion is `STALE/ok=false`, and a service with no completion beyond boot grace is `NEVER_COMPLETED_THIS_BOOT/ok=false`.

## N3 — retention overflow campaign

The real backup producer was redirected to a disposable backup root preloaded past retention. After producer execution it retained exactly 14 archives plus their sidecars. No live backup was pruned by this test.

The real evidence-ledger producer/verifier was redirected to a disposable 31-record valid chain. After one additional record, retention converged to exactly 30 records. The pruned-chain anchor matched the predecessor hash of the oldest retained record and the production ledger verifier returned PASS.

## N4 — resource enforcement binding

Unsafe deliberate OOM/fork exhaustion was not performed. Instead a temporary benign user-systemd unit was run with `MemoryMax=32M` and `TasksMax=8`; while active, systemd exposed `MemoryMax=33554432` / `TasksMax=8` and the kernel cgroup files exposed exactly `memory.max=33554432` / `pids.max=8`. The transient probe was stopped and removed from the accepted control plane.

Live AI-FILM services remain bounded at `MemoryMax=256M` and `TasksMax=128`, with accounting enabled.

## N5 — producer-first recovery refresh

The changed health control was incorporated through the required producer sequence: control backup -> NTFS mirror -> deterministic transfer export -> full DR rehearsal -> fail-closed campaign -> evidence ledger -> health.

Observed current rotating sample:

```yaml
LATEST_BACKUP_SAMPLE: control-state-20260917T090226Z.tar.gz
LATEST_BACKUP_SAMPLE_FILES: 87
LATEST_BACKUP_SAMPLE_SHA256: c213efff4aeff5585bf14efea172889dffe3b33af815dabaf30f3b5e14c887d2
LATEST_EXPORT_SAMPLE_SHA256: 023eb0d5275eeb1b27974c908664f17b46a4bbe11a12376d4e085602a7135d11
FULL_DR_SAMPLE_CONTROL_FILES: 87
FULL_DR_TIMER_DEFINITIONS: 11
FULL_DR_RESOURCE_DROPINS: 11
EVIDENCE_LEDGER_RECORDS_AT_SAMPLE: 7
EVIDENCE_LEDGER_RETENTION: 30
FAILCLOSED_CAMPAIGN: 8/8_PASS
HEALTH_STATUS: PASS
```

The 85→87 count change is legitimate because the backup contains bounded ledger history. Therefore backup file count, backup SHA and transfer-export SHA are **rotating observed samples**, not stable candidate identities. Stable invariants are verifier success, retention/freshness bounds, timer/resource schema, chain integrity, exact reviewed dev21 identities and fail-closed producer-before-consumer migration.

## N6 — canonical rule

Future canonical state must distinguish stable identity from rotating recovery samples. It may record the latest sample for traceability, but must not treat the current backup/export SHA or history-dependent file count as an immutable release identity.

This program changes no product source, native configuration or test oracle. It creates no LAB approval, READY flag, trust anchor, native result, qualification, SITE evidence or HOST_READY claim.