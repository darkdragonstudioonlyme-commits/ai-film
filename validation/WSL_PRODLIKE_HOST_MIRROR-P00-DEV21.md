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
MIRROR_SERVICE_SHA256: cc7f2ccabc21843b00331f8ce2223085e933fe59fd3ba38d045b99989b5128f1
MIRROR_TIMER_SHA256: 024fc001ccb5749791c55b11fab94430c5d907f4437036b50ce7aab973923186
MIRROR_TIMER: "enabled active / 2h"
MIRROR_SERVICE_RESULT: success
MIRROR_SYSTEMD_SECURITY: "4.1 OK"
RETENTION: 14
MIRROR_MAX_AGE_HOURS: 30
SAMPLE_ARCHIVE: control-state-20260916T171511Z.tar.gz
SAMPLE_ARCHIVE_SHA256: bf369a12ba9da16eb77f5e27f540fc6a44968c325c87ffd8da464e1c76e293bf
SAMPLE_FILE_COUNT: 29
MIRROR_VERIFY: PASS
MIRROR_RESTORE_PROBE: PASS
MIRROR_SECRET_SCAN: PASS
WINDOWS_ACL_INHERITANCE: disabled
WINDOWS_ACL_PRINCIPALS: "NT AUTHORITY\\SYSTEM + DESKTOP-LCISMET\\Admin only"
NATIVE_AUTHORITY_INCLUDED: false
PROTECTED_IDENTITY_INCLUDED: false
NATIVE_EXECUTION_STARTED: false
```

The mirror copies only a control backup that has already passed the local backup verifier. Copy is performed through a temporary file followed by atomic replace on the Windows-side destination, and the destination bytes are rehashed before the mirror index is committed. The host-side index binds archive name, SHA-256, copy timestamp, retention and explicit `native_authority_included=false` / `protected_identity_included=false` assertions.

The Windows directory has inheritance removed and only SYSTEM plus the current operator retain Full Control. No approval inbox, protected authority object, raw SID/MachineGuid, credential, password/token assignment or private-key marker is mirrored.

A restore probe was executed directly from the NTFS mirror rather than the local WSL backup. All 29 embedded control files were rehashed against the archive manifest, unsafe paths were rejected, required recovery files were present and the secret/protected-domain scan passed. This provides a second-filesystem recovery copy for WSL-distro failure; it is **not claimed as off-host or independent-physical-device disaster recovery**.

The mirror is operational-readiness evidence only. It does not create LAB authority, write HKLM, start the disposable LAB, execute native acceptance cases or advance V02.