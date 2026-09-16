# Phase00 dev21 — Windows host control-backup mirror

```yaml
MIRROR_RECORD_ID: WSL-PRODLIKE-HOST-MIRROR-P00-DEV21-001
STATUS: PASS
SOURCE_COMMIT: 934659f535d81d9a4a07389531acc2b9c304fa6d
SOURCE_BACKUP_ROOT: /home/dragon/ai-film-runtime/backups
HOST_MIRROR_ROOT: C:\Users\Admin\AppData\Local\AI-FILM\runtime-backups\dev21
HOST_FILESYSTEM: NTFS
MIRROR_SCRIPT_SHA256: dd6436cd20a5041e0b0b88f31a0d62c2b94c1ce8d0525ee91bd2b0c5ce54aa57
MIRROR_VERIFY_SCRIPT_SHA256: b473ba2d7937f4a2ab4442b1da3ac572fd4def66d9b1bf3c44ea75bba2909dca
MIRROR_TIMER: "enabled active / 2h"
MIRROR_SERVICE_RESULT: success
MIRROR_SYSTEMD_SECURITY: "4.1 OK"
RETENTION: 14
MIRROR_MAX_AGE_HOURS: 30
SAMPLE_ARCHIVE: control-state-20260916T223556Z.tar.gz
SAMPLE_ARCHIVE_SHA256: 0f368a952974dcfee4d53ccc6be402899dfe00ef901b7f9b73342b9b6482379a
SAMPLE_FILE_COUNT: 58
MIRROR_VERIFY: PASS
FULL_DR_TOOLING_RECOVERABLE: true
FAILCLOSED_CAMPAIGN_TOOLING_RECOVERABLE: true
BOOT_ORDERING_DROPINS_RECOVERABLE: true
RECOVERY_EVIDENCE_RECOVERABLE: true
WINDOWS_ACL_INHERITANCE: disabled
WINDOWS_ACL_PRINCIPALS: "SYSTEM + operator only"
NATIVE_AUTHORITY_INCLUDED: false
PROTECTED_IDENTITY_INCLUDED: false
NATIVE_EXECUTION_STARTED: false
```

The mirror copies only a locally verified control backup, rehashes the NTFS bytes and commits the mirror index only after verification. The current mirror matches the local 58-file backup SHA `0f368a95...`.

The expanded recovery set includes the full-DR rehearsal tool/evidence, fail-closed campaign tool/evidence, the two new service/timer pairs, bounded-execution drop-ins and explicit health/recovery ordering drop-ins. A disposable rehearsal using the portable recovery chain restored these controls and verified ten timer definitions before reconstructing exact dev21.

The Windows mirror remains same-host second-filesystem recovery. It excludes the protected authority inbox/objects and is not represented as off-host disaster recovery or native execution authority.
