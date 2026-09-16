# AI-FILM-SERVER — State Checkpoint V40

Exact dev21 product/native state is unchanged: source `934659f535d81d9a4a07389531acc2b9c304fa6d` remains code-review PASS; `RUN-P00-VALIDATION-001` remains BLOCKED at `V02_LAB_EXECUTION_AUTHORITY`; all 86 native procedures remain `NOT_RUN`; qualification/SITE/HOST_READY remain absent.

V40 reconciles actual operational-maturity evidence recorded at validation head `c615af57b7216e2fbb0b3c71a9431e442a4def59`.

```yaml
SUPERVISED_TIMERS: 11
SUPERVISED_PREVIOUS_JOB_RESULTS: 10
RESOURCE_BOUND_SERVICES: 11
MEMORY_MAX_PER_SERVICE: 256M
TASKS_MAX_PER_SERVICE: 128
EVIDENCE_LEDGER_RETENTION: 30
EVIDENCE_LEDGER_HASH_CHAIN: PASS
USER_MANAGER_REEXEC_REHEARSAL: PASS
INCIDENT_DETECTION_RECOVERY_DRILL: PASS
CONTROL_BACKUP_FILES: 85
CONTROL_BACKUP_SHA256: daa43ca4d72052881f7ac6aabfd2eae95c9ffcff7ca3f43e8a6d1d1a25ca58de
NTFS_HOST_MIRROR_VERIFY: PASS
TRANSFER_EXPORT_SHA256: b4cf49cd4e177c7ea6777e5ead4da3bf5d1669088bfbd136ce180a322faa31c5
FULL_DR_REHEARSAL: PASS
FULL_DR_CONTROL_FILES: 85
FULL_DR_TIMER_DEFINITIONS: 11
FULL_DR_RESOURCE_DROPINS: 11
FAILCLOSED_CAMPAIGN: 8/8_PASS
OFFHOST_BINARY_PAYLOAD_UPLOADED: false
NATIVE_EXECUTION_STARTED: false
```

The evidence ledger captured an intentionally injected supervised-service failure while health was FAIL and then captured the recovered PASS state in the next hash-chained record. The controlled user-manager `daemon-reexec` preserved 11 persistent enabled/active timers and resource/dependency drop-ins.

The recovery schema expansion used producer-before-consumer migration. The stricter new DR rehearsal rejected the old recovery payload, then passed only after new backup -> mirror -> export regeneration. This is evidence relevant to learning 006 but **not** effectiveness closure because its state-version gate remains V41.

V40 also finalizes learning 006 from V39 transition-only `PASS_ON_FINAL_REVIEW / ACTIVE_ON_PROMOTION` to durable `PASS / ACTIVE`. Its `PENDING_MEASUREMENT` status and V41 gate remain unchanged.

R8 review and A8 audit must bind one exact final V40 design SHA. Promotion may add only their immutable verdict records and must be followed by post-promotion CI.