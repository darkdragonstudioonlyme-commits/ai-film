# Phase00 dev21 — production-like operator status surface

```yaml
STATUS_RECORD_ID: WSL-PRODLIKE-OPERATOR-STATUS-P00-DEV21-001
STATUS: PASS
SOURCE_COMMIT: 934659f535d81d9a4a07389531acc2b9c304fa6d
STATUS_COMMAND: /home/dragon/ai-film-runtime/bin/aifilm-prodlike-status.py
STATUS_SCRIPT_SHA256: a2ed2027136fb6a593a910d05d06154d8b6513ba05cc081d12ac204ff14a44e7
STATUS_SCRIPT_MODE: "0700"
HUMAN_RESULT: READY_NON_NATIVE_PRODLIKE_OPERATIONS
NATIVE_GATE_RESULT: BLOCKED_EXTERNAL_AUTHORITY
AUTHORITY_STATUS: BLOCKED
AUTHORITY_REASON: APPROVAL_ENVELOPE_MISSING
NATIVE_EXECUTION_STARTED: false
JSON_MODE: "--json"
JSON_RUNTIME_MANIFEST_FIELD: runtime_manifest_sha256
JSON_HEALTH_SNAPSHOT_FIELD: health_snapshot_sha256
JSON_HEALTH_TIMESTAMP_FIELD: health_timestamp_utc
CONTROL_BACKUP_CHANGED_BY_STATUS_TOOL: false
NATIVE_AUTHORITY_CHANGED: false
```

The status command is an operator convenience layer over existing verified evidence. It reads the current runtime health and V02 watcher evidence and executes the existing local-backup, NTFS-host-mirror, rebuild-set and recovery verifiers. A healthy non-native runtime with a legitimate V02 governance block is reported as `production_like=READY_NON_NATIVE_PRODLIKE_OPERATIONS` together with `native_gate=BLOCKED_EXTERNAL_AUTHORITY`; the command never converts operational health into native authority.

The observed status passes all seven checks: health, authority evidence presence, `native_execution_started=false`, local control-backup verification, host-mirror verification, rebuild-set verification and recovery verification. JSON mode returns the same classification plus verifier summaries. The schema now distinguishes `runtime_manifest_sha256` from the independently computed `health_snapshot_sha256`, and also returns the health snapshot timestamp, avoiding the previous ambiguous `runtime_health_sha256` label.

This command remains deliberately outside the canonical 39-file V36 control backup, so the operator convenience update does not make `CONTROL_BACKUP_FILES` stale. It is not a daemon, opens no port, does not start the disposable LAB, does not write HKLM, and does not advance `RUN-P00-VALIDATION-001` past V02.
