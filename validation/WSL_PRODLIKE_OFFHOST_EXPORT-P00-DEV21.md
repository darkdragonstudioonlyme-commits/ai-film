# Phase00 dev21 — transfer-ready off-host DR export

```yaml
EXPORT_RECORD_ID: WSL-PRODLIKE-OFFHOST-EXPORT-P00-DEV21-001
STATUS: TRANSFER_READY_WITH_OFFHOST_METADATA
SOURCE_COMMIT: 934659f535d81d9a4a07389531acc2b9c304fa6d
EXPORT_PATH: C:\Users\Admin\AppData\Local\AI-FILM\offhost-export\dev21\AI-FILM-P00-DEV21-OFFHOST-DR-EXPORT.zip
EXPORT_SHA256: 0f603dec5e48d64bccc52271abfd0e83deb93a0655193c4cb7741c850500bbf8
EXPORT_SIZE_BYTES: 1376937
EXPORT_PAYLOAD_FILES: 7
EXPORT_DETERMINISTIC: true
EXPORT_BUILD_SCRIPT_SHA256: 41fc42c9c792db204b8759c97787125340a979f9119047aae0864400a966bce1
EXPORT_VERIFY_SCRIPT_SHA256: beacaee9a1f68228d4466970fa83f3492d2591ea0296502b57ceb0b046202a67
EXPORT_SERVICE_SHA256: 60df6cea651bcc669f5809e062325d962d5389485e6cae4d9d40e084838c9b51
EXPORT_TIMER_SHA256: 086d01ab44d122bba0a7bb8e50168548af132fccd8a1955bc124ae8afc95e305
EXPORT_TIMEOUT_DROPIN_SHA256: f6ddc0822cc97e489773b9bbbdefb3ab47d6eff9770def066ff79602f9ff57ed
EXPORT_TIMER: "enabled active / boot+6h"
EXPORT_SERVICE_RESULT: success
EXPORT_SYSTEMD_SECURITY: "4.1 OK"
EXPORT_MAX_AGE_HOURS: 30
CONTROL_BACKUP: control-state-20260916T203634Z.tar.gz
CONTROL_BACKUP_SHA256: c31250cf400221f7872ed0001fbdf513ca158b8735dc7a4fd4694a11ecc8ed6f
CONTROL_BACKUP_FILES: 44
PACKAGE_SHA256: f6ee158a318614f8bbef28be7af82549e0a268425da28147a2fa7b14c7b3d3e3
WHEEL_SHA256: 9b565b24a896879bd7bd812c43efcc741d8bc2eb08c0b23318b1e66c64b9e7e8
APP_MANIFEST_SHA256: 07fcf4a31c6ffabc3628ba12584d249680cea1344e26fb1d2cbe2983e30270fa
RUNTIME_MANIFEST_SHA256: 8227e8350208314db087612889d2b481393c67ec3a5eb0bfa84a869c1d0829a2
REBUILD_INDEX_SHA256: 40cc6df68e8ca536acf183e8cbf63ce157845e4f33d2659c92efcb41fbc3ed54
SELF_CONTAINED_DRILL: PASS
DRILL_APP_FILES: 283
DRILL_REBUILT_VERSION: 0.1.0.dev21
DRILL_REBUILT_INVENTORY: "86 NOT_RUN / 0 parent cases / qualification false"
DRILL_HOST_READY: false
DRILL_ISOLATED_VENV: PASS
WINDOWS_ACL_INHERITANCE: disabled
WINDOWS_ACL_PRINCIPALS: "NT AUTHORITY\\SYSTEM + DESKTOP-LCISMET\\Admin only"
OFF_HOST_METADATA_MANIFEST: STORED_PRIVATE_GOOGLE_DRIVE
OFF_HOST_METADATA_FOLDER: "AI-FILM DR"
OFF_HOST_METADATA_SHARED: false
OFF_HOST_METADATA_ANCHORED_EXPORT_SHA256: 0f603dec5e48d64bccc52271abfd0e83deb93a0655193c4cb7741c850500bbf8
OFF_HOST_PAYLOAD_UPLOADED: false
NATIVE_AUTHORITY_INCLUDED: false
PROTECTED_IDENTITY_INCLUDED: false
CREDENTIALS_INCLUDED: false
OFF_HOST_COPY_COMPLETED: false
OFF_HOST_DR_CLAIMED: false
```

The export is now a supervised repeatable pipeline rather than a one-off package. Every six hours the hardened service builds from the latest already-verified control backup and exact NTFS rebuild set, performs atomic replacement, writes a SHA sidecar and executes the heavy self-contained drill. Runtime health independently checks export freshness/integrity and previous service success.

The format is deterministic: all ZIP entry metadata is normalized to the source control-backup epoch and all members are written in stable order. Two consecutive builds from identical payload state produced identical bytes/SHA. Export identity therefore changes only when its underlying recovery payload changes, not merely because the timer ran again.

Current export SHA is `0f603dec...`. It contains seven payloads including the verified 44-file control backup and exact reviewed non-secret runtime reconstruction set. Heavy drill uses the portable ZIP alone, independently verifies inner control members, 283/283 source bytes, builds a fresh `python3 -m venv --without-pip`, reproduces the `.pth` runtime shape and reports `0.1.0.dev21`, `host_ready=false`, `86 NOT_RUN`, zero parent cases and no qualification.

The export directory has Windows ACL inheritance removed and only SYSTEM plus the current operator have Full Control. A private Google Drive document stores the currently anchored deterministic export checksum and recovery identities. The Drive file is not publicly shared. It remains an off-host integrity metadata anchor only: the binary ZIP itself has not left the original host.

Therefore `OFF_HOST_DR_CLAIMED=false` remains correct. No OAuth/base64 credential workaround was introduced. This export/metadata anchor does not grant LAB/SITE/native execution authority and does not advance `RUN-P00-VALIDATION-001` beyond V02.