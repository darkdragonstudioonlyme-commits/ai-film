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
MIRROR_TIMEOUT_DROPIN_SHA256: b29cfb8eb000cdee0704b5f92a66df30106f9fd09677311468346363fdca61f5
MIRROR_EFFECTIVE_TIMEOUT: 5min
MIRROR_TIMER: "enabled active / 2h"
MIRROR_SERVICE_RESULT: success
MIRROR_SYSTEMD_SECURITY: "4.1 OK"
RETENTION: 14
MIRROR_MAX_AGE_HOURS: 30
SAMPLE_ARCHIVE: control-state-20260916T183817Z.tar.gz
SAMPLE_ARCHIVE_SHA256: 4c8ff1de63df7f58ae42b59766e8936b87dc9581c201b772d7fdd95453707905
SAMPLE_FILE_COUNT: 39
MIRROR_VERIFY: PASS
MIRROR_RESTORE_PROBE: PASS
MIRROR_SECRET_SCAN: PASS
WINDOWS_ACL_INHERITANCE: disabled
WINDOWS_ACL_PRINCIPALS: "NT AUTHORITY\\SYSTEM + DESKTOP-LCISMET\\Admin only"
NATIVE_AUTHORITY_INCLUDED: false
PROTECTED_IDENTITY_INCLUDED: false
NATIVE_EXECUTION_STARTED: false
```

The mirror copies only a control backup that has already passed the local verifier. Copy uses a temporary destination followed by atomic replace, then the NTFS bytes are rehashed before `mirror-index.json` is committed. The mirror index binds archive name, SHA-256, copy timestamp, retention and explicit `native_authority_included=false` / `protected_identity_included=false` assertions.

The Windows directory has ACL inheritance removed and only SYSTEM plus the current operator retain Full Control. No approval inbox, protected authority object, raw SID/MachineGuid, credential or qualification evidence is mirrored.

A restore probe executed directly from the NTFS copy rehashed all 39 control files against the embedded manifest, rejected unsafe paths and passed secret/protected-domain scanning. The 39-file control archive includes operational scripts, seven supervised timer/service definitions and bounded-execution drop-ins, including the rebuild-set verifier control files; the exact runtime reconstruction artifacts themselves are kept separately in `validation/WSL_PRODLIKE_REBUILD_SET-P00-DEV21.md`.

This mirror is a same-host, second-filesystem recovery measure for WSL-distro failure. It is not claimed as off-host disaster recovery and does not create LAB authority, write HKLM, start the disposable LAB or execute native acceptance cases.