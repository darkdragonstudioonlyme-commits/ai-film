# Phase00 dev21 — Production-Like Readiness Program

```yaml
PROGRAM_ID: PRODLIKE-READINESS-P00-DEV21-002
SOURCE_COMMIT: 934659f535d81d9a4a07389531acc2b9c304fa6d
STATUS: P1_P6_COMPLETE_P7_RECONCILIATION_PENDING
ACTIVE_RUN: RUN-P00-VALIDATION-001
NATIVE_STEP: V02_LAB_EXECUTION_AUTHORITY
NATIVE_STEP_STATE: BLOCKED_EXTERNAL_AUTHORITY

P1_BASELINE_DRIFT_INVENTORY: PASS
P2_FAILCLOSED_FAULT_CAMPAIGN: PASS_8_OF_8
P3_FULL_DR_RECOVERY_REHEARSAL: PASS
P4_BOOT_SERVICE_RESILIENCE: PASS
P5_EXTERNAL_AUTHORITY_PREFLIGHT: PASS
P6_RUNBOOK_INCIDENT_MATRIX: PASS
P7_CANONICAL_RECONCILIATION: PENDING

SUPERVISED_TIMERS: 10
SUPERVISED_JOB_RESULTS_REQUIRED: 9
CONTROL_BACKUP_FILES: 58
CONTROL_BACKUP: control-state-20260916T223556Z.tar.gz
CONTROL_BACKUP_SHA256: 0f368a952974dcfee4d53ccc6be402899dfe00ef901b7f9b73342b9b6482379a
HOST_MIRROR_VERIFY: PASS
TRANSFER_EXPORT_SHA256: f993040f082fe49650a9a6819290717694e04980f24c2ef7a5b90cf0a4509c05
TRANSFER_EXPORT_VERIFY: PASS
TRANSFER_EXPORT_CONTROL_FILES: 58
REBUILD_SET_COLD_PROBE: PASS
FULL_DR_REHEARSAL: PASS
FULL_DR_CONTROL_FILES: 58
FULL_DR_TIMER_DEFINITIONS: 10
FULL_DR_APP_FILES: 283
FULL_DR_VERSION: 0.1.0.dev21
FULL_DR_INVENTORY: "86 NOT_RUN"
FAILCLOSED_CAMPAIGN: "8/8 PASS"
OFFHOST_METADATA_ANCHOR: STATIC_EXACT_CANDIDATE_IDENTITY_PRIVATE_GOOGLE_DRIVE
OFFHOST_BINARY_PAYLOAD_UPLOADED: false
OFF_HOST_DR_CLAIMED: false
NATIVE_EXECUTION_STARTED: false
```

## Program scope

This program replaces incremental one-off hardening with a longer operational campaign. It remains entirely outside native LAB/SITE authority. No phase can satisfy V02 `DONE_WHEN`, start the disposable LAB, write the HKLM trust anchor, execute a native case, issue qualification, or claim HOST_READY.

### P1 — baseline and drift inventory

Canonical V38, validation lane, live runtime, systemd supervision, DR artifacts and V02 authority evidence were reconciled before mutation. The native gate remained `APPROVAL_ENVELOPE_MISSING`, LAB stopped, READY absent and trust anchor absent.

### P2 — fail-closed negative campaign

`/home/dragon/ai-film-runtime/bin/run-failclosed-campaign.py` loads the actual live verifier modules against disposable copies. Eight negative cases passed: backup sidecar mismatch, backup stale, export sidecar mismatch, export stale, inner-control corruption, rebuild-index mismatch, rebuild-artifact corruption and unsafe native-authority flag. Every corrupted copy was rejected and all live artifacts reverified PASS afterward.

### P3 — full DR recovery rehearsal

`run-dr-recovery-rehearsal.py` restores the control plane from the portable export into a disposable root, verifies every manifest member, checks required operational tooling and timer definitions, compiles restored Python control scripts, re-verifies 283 app files, creates a fresh `venv --without-pip`, restores the `.pth` runtime shape and reproduces `0.1.0.dev21`, `86 NOT_RUN`, zero native execution and `host_ready=false`.

### P4 — boot/service resilience

Health and recovery now explicitly `Wants+After` runtime integrity verification rather than relying only on timer offsets. Daily full-DR rehearsal and weekly fail-closed campaign run as hardened user-systemd jobs, each bounded to ten minutes and observed at `4.1 OK` systemd security exposure. Runtime health requires ten timers, successful supervised job results, fresh DR evidence and fresh negative-campaign evidence.

During migration the new rehearsal correctly rejected the old 44-file export because new required control artifacts were absent. The transition was completed in the required order `backup -> mirror -> export -> rehearsal`, producing the current 58-file recovery set. The rejection was treated as expected fail-closed schema migration behavior, not bypassed.

### P5 — V02 authority preflight

`/home/dragon/ai-film-dev/validation-ops/v02-authority-preflight.py` invokes the exact existing V02 validator on a staging directory, snapshots staging metadata before/after, and emits only normalized MISSING/INVALID/READY_FOR_INTAKE state. Current inbox returned MISSING; a disposable malformed envelope returned INVALID/ENVELOPE_SCHEMA; both left staging unchanged and created no READY flag.

### P6 — operations/runbook durability

Operational response is defined in `validation/PRODLIKE_OPERATIONS_RUNBOOK-P00-DEV21.md`. The private Google Drive manifest was changed from a rotating-export hash anchor to a stable exact-candidate/rebuild identity anchor, preventing daily backup rotation from creating a stale off-host checksum claim. Binary payload remains on-host and is not represented as off-host DR.

### P7 — canonical reconciliation

P7 is intentionally deferred until the validation records below are reconciled and the exact canonical design can be reviewed/audited as one state transition. This is a real state change (10 timers, 58-file control state, supervised negative testing/full DR rehearsal and read-only V02 preflight), so the next canonical transition is justified rather than a version-only bump.
