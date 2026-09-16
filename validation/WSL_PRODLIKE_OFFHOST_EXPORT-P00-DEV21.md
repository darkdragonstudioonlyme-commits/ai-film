# Phase00 dev21 — transfer-ready DR export

```yaml
EXPORT_RECORD_ID: WSL-PRODLIKE-OFFHOST-EXPORT-P00-DEV21-001
STATUS: TRANSFER_READY_WITH_STATIC_OFFHOST_IDENTITY_METADATA
SOURCE_COMMIT: 934659f535d81d9a4a07389531acc2b9c304fa6d
EXPORT_PATH: C:\Users\Admin\AppData\Local\AI-FILM\offhost-export\dev21\AI-FILM-P00-DEV21-OFFHOST-DR-EXPORT.zip
EXPORT_SHA256: f993040f082fe49650a9a6819290717694e04980f24c2ef7a5b90cf0a4509c05
EXPORT_PAYLOAD_FILES: 7
EXPORT_DETERMINISTIC: true
EXPORT_BUILD_SCRIPT_SHA256: 41fc42c9c792db204b8759c97787125340a979f9119047aae0864400a966bce1
EXPORT_VERIFY_SCRIPT_SHA256: beacaee9a1f68228d4466970fa83f3492d2591ea0296502b57ceb0b046202a67
EXPORT_TIMER: "enabled active / boot+6h"
EXPORT_SERVICE_RESULT: success
EXPORT_SYSTEMD_SECURITY: "4.1 OK"
EXPORT_MAX_AGE_HOURS: 30
CONTROL_BACKUP: control-state-20260916T223556Z.tar.gz
CONTROL_BACKUP_SHA256: 0f368a952974dcfee4d53ccc6be402899dfe00ef901b7f9b73342b9b6482379a
CONTROL_BACKUP_FILES: 58
PACKAGE_SHA256: f6ee158a318614f8bbef28be7af82549e0a268425da28147a2fa7b14c7b3d3e3
WHEEL_SHA256: 9b565b24a896879bd7bd812c43efcc741d8bc2eb08c0b23318b1e66c64b9e7e8
APP_MANIFEST_SHA256: 07fcf4a31c6ffabc3628ba12584d249680cea1344e26fb1d2cbe2983e30270fa
RUNTIME_MANIFEST_SHA256: 8227e8350208314db087612889d2b481393c67ec3a5eb0bfa84a869c1d0829a2
REBUILD_INDEX_SHA256: 40cc6df68e8ca536acf183e8cbf63ce157845e4f33d2659c92efcb41fbc3ed54
SELF_CONTAINED_DRILL: PASS
DRILL_CONTROL_FILES: 58
DRILL_APP_FILES: 283
DRILL_REBUILT_VERSION: 0.1.0.dev21
DRILL_REBUILT_INVENTORY: "86 NOT_RUN / 0 parent cases / qualification false"
DRILL_HOST_READY: false
OFF_HOST_METADATA_MANIFEST: STATIC_EXACT_CANDIDATE_IDENTITY_PRIVATE_GOOGLE_DRIVE
OFF_HOST_ROTATING_EXPORT_HASH_PINNED: false
OFF_HOST_PAYLOAD_UPLOADED: false
NATIVE_AUTHORITY_INCLUDED: false
PROTECTED_IDENTITY_INCLUDED: false
CREDENTIALS_INCLUDED: false
OFF_HOST_COPY_COMPLETED: false
OFF_HOST_DR_CLAIMED: false
```

The transfer-ready export remains deterministic for identical payload state and is rebuilt only from the latest verified control backup plus the exact non-secret rebuild set. Heavy drill verifies the embedded 58-file control state, 283 app files and a fresh reconstructed venv reporting `0.1.0.dev21`, `86 NOT_RUN` and `host_ready=false`.

The private Google Drive document no longer pins the rotating export/control-backup SHA. Daily control backup rotation legitimately changes those hashes, which made the previous dynamic checksum anchor stale. The Drive document now stores only stable exact-candidate/rebuild identities: source commit, package, wheel, app manifest, runtime manifest and rebuild index. This makes the off-host metadata durable without pretending the binary payload has been uploaded.

Dynamic export/control hashes remain verified and freshness-gated on the original host. The binary ZIP itself is still on-host; `OFF_HOST_DR_CLAIMED=false` remains mandatory. No authority, credential or protected identity material is included.
