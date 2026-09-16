# Phase00 dev21 — Windows host control-backup mirror

```yaml
MIRROR_RECORD_ID: WSL-PRODLIKE-HOST-MIRROR-P00-DEV21-001
STATUS: PASS
SOURCE_COMMIT: 934659f535d81d9a4a07389531acc2b9c304fa6d
HOST_FILESYSTEM: NTFS
MIRROR_TIMER: "enabled active / 2h"
MIRROR_SERVICE_RESULT: success
MIRROR_SYSTEMD_SECURITY: "4.1 OK"
RETENTION: 14
MIRROR_MAX_AGE_HOURS: 30
SAMPLE_ARCHIVE: control-state-20260916T232534Z.tar.gz
SAMPLE_ARCHIVE_SHA256: daa43ca4d72052881f7ac6aabfd2eae95c9ffcff7ca3f43e8a6d1d1a25ca58de
SAMPLE_FILE_COUNT: 85
MIRROR_VERIFY: PASS
EVIDENCE_LEDGER_RECOVERABLE: true
EVIDENCE_HISTORY_RECOVERABLE: true
RESOURCE_DROPINS_RECOVERABLE: 11
TIMER_DEFINITIONS_RECOVERABLE: 11
FULL_DR_TOOLING_RECOVERABLE: true
FAILCLOSED_CAMPAIGN_TOOLING_RECOVERABLE: true
WINDOWS_ACL_INHERITANCE: disabled
NATIVE_AUTHORITY_INCLUDED: false
PROTECTED_IDENTITY_INCLUDED: false
NATIVE_EXECUTION_STARTED: false
```

The NTFS mirror contains the current locally verified 85-file control backup and matches SHA `daa43ca4...`. The expanded state carries the evidence-ledger producer/verifier, bounded ledger history, all 11 timer definitions, all 11 resource-bound drop-ins, DR/fault tooling and their safe evidence.

The full DR rehearsal restored this mirrored/exported control schema in a disposable root and verified ledger-chain integrity before reconstructing exact dev21. The mirror remains a same-host second-filesystem measure; it is not binary off-host DR and excludes protected authority/identity domains.