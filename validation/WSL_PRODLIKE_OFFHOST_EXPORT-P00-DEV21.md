# Phase00 dev21 — transfer-ready DR export

```yaml
EXPORT_RECORD_ID: WSL-PRODLIKE-OFFHOST-EXPORT-P00-DEV21-001
STATUS: TRANSFER_READY_WITH_STATIC_OFFHOST_IDENTITY_METADATA
SOURCE_COMMIT: 934659f535d81d9a4a07389531acc2b9c304fa6d
EXPORT_PATH: C:\Users\Admin\AppData\Local\AI-FILM\offhost-export\dev21\AI-FILM-P00-DEV21-OFFHOST-DR-EXPORT.zip
EXPORT_SHA256: b4cf49cd4e177c7ea6777e5ead4da3bf5d1669088bfbd136ce180a322faa31c5
EXPORT_PAYLOAD_FILES: 7
EXPORT_DETERMINISTIC: true
EXPORT_TIMER: "enabled active / boot+6h"
EXPORT_SERVICE_RESULT: success
EXPORT_SYSTEMD_SECURITY: "4.1 OK"
EXPORT_MAX_AGE_HOURS: 30
CONTROL_BACKUP: control-state-20260916T232534Z.tar.gz
CONTROL_BACKUP_SHA256: daa43ca4d72052881f7ac6aabfd2eae95c9ffcff7ca3f43e8a6d1d1a25ca58de
CONTROL_BACKUP_FILES: 85
PACKAGE_SHA256: f6ee158a318614f8bbef28be7af82549e0a268425da28147a2fa7b14c7b3d3e3
WHEEL_SHA256: 9b565b24a896879bd7bd812c43efcc741d8bc2eb08c0b23318b1e66c64b9e7e8
APP_MANIFEST_SHA256: 07fcf4a31c6ffabc3628ba12584d249680cea1344e26fb1d2cbe2983e30270fa
RUNTIME_MANIFEST_SHA256: 8227e8350208314db087612889d2b481393c67ec3a5eb0bfa84a869c1d0829a2
REBUILD_INDEX_SHA256: 40cc6df68e8ca536acf183e8cbf63ce157845e4f33d2659c92efcb41fbc3ed54
SELF_CONTAINED_DRILL: PASS
DRILL_CONTROL_FILES: 85
DRILL_APP_FILES: 283
DRILL_REBUILT_VERSION: 0.1.0.dev21
DRILL_REBUILT_INVENTORY: "86 NOT_RUN / 0 parent cases / qualification false"
FULL_DR_REHEARSAL: PASS
FULL_DR_TIMER_DEFINITIONS: 11
FULL_DR_RESOURCE_DROPINS: 11
FULL_DR_LEDGER_CHAIN: PASS
OFF_HOST_METADATA_MANIFEST: STATIC_EXACT_CANDIDATE_IDENTITY_PRIVATE_GOOGLE_DRIVE
OFF_HOST_ROTATING_EXPORT_HASH_PINNED: false
OFF_HOST_PAYLOAD_UPLOADED: false
NATIVE_AUTHORITY_INCLUDED: false
PROTECTED_IDENTITY_INCLUDED: false
CREDENTIALS_INCLUDED: false
OFF_HOST_COPY_COMPLETED: false
OFF_HOST_DR_CLAIMED: false
```

The deterministic transfer export now embeds the verified 85-file operational-maturity control state. Heavy drill still reconstructs exact dev21 in a fresh isolated venv, while full DR additionally restores 11 timer definitions, 11 resource-bound drop-ins and the bounded hash-chained evidence history.

The stricter new DR consumer intentionally rejected the previous export before producer migration. Only after a new backup and NTFS mirror were produced was this export rebuilt and accepted. This preserves fail-closed recovery schema versioning.

Private Google Drive continues to pin only stable exact-candidate/rebuild identities. Rotating export/control hashes remain host-side freshness-verified; the binary payload has not left the host, so `OFF_HOST_DR_CLAIMED=false` remains mandatory.