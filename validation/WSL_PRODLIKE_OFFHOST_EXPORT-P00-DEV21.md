# Phase00 dev21 — transfer-ready DR export

```yaml
EXPORT_RECORD_ID: WSL-PRODLIKE-OFFHOST-EXPORT-P00-DEV21-001
STATUS: TRANSFER_READY_WITH_STATIC_OFFHOST_IDENTITY_METADATA
SOURCE_COMMIT: 934659f535d81d9a4a07389531acc2b9c304fa6d
EXPORT_PATH: C:\Users\Admin\AppData\Local\AI-FILM\offhost-export\dev21\AI-FILM-P00-DEV21-OFFHOST-DR-EXPORT.zip
LATEST_SAMPLE_SHA256: 023eb0d5275eeb1b27974c908664f17b46a4bbe11a12376d4e085602a7135d11
EXPORT_PAYLOAD_FILES: 7
EXPORT_DETERMINISTIC_FOR_IDENTICAL_PAYLOAD: true
EXPORT_TIMER: "enabled active / boot+6h"
EXPORT_SERVICE_RESULT: success
EXPORT_SYSTEMD_SECURITY: "4.1 OK"
EXPORT_MAX_AGE_HOURS: 30
LATEST_CONTROL_BACKUP_SAMPLE: control-state-20260917T090226Z.tar.gz
LATEST_CONTROL_BACKUP_SAMPLE_SHA256: c213efff4aeff5585bf14efea172889dffe3b33af815dabaf30f3b5e14c887d2
LATEST_CONTROL_BACKUP_SAMPLE_FILES: 87
PACKAGE_SHA256: f6ee158a318614f8bbef28be7af82549e0a268425da28147a2fa7b14c7b3d3e3
WHEEL_SHA256: 9b565b24a896879bd7bd812c43efcc741d8bc2eb08c0b23318b1e66c64b9e7e8
APP_MANIFEST_SHA256: 07fcf4a31c6ffabc3628ba12584d249680cea1344e26fb1d2cbe2983e30270fa
RUNTIME_MANIFEST_SHA256: 8227e8350208314db087612889d2b481393c67ec3a5eb0bfa84a869c1d0829a2
REBUILD_INDEX_SHA256: 40cc6df68e8ca536acf183e8cbf63ce157845e4f33d2659c92efcb41fbc3ed54
SELF_CONTAINED_DRILL: PASS
FULL_DR_REHEARSAL: PASS
FULL_DR_TIMER_DEFINITIONS: 11
FULL_DR_RESOURCE_DROPINS: 11
FULL_DR_LEDGER_CHAIN: PASS
OFF_HOST_METADATA_MANIFEST: STATIC_EXACT_CANDIDATE_IDENTITY_PRIVATE_GOOGLE_DRIVE
OFF_HOST_ROTATING_EXPORT_HASH_PINNED: false
OFF_HOST_PAYLOAD_UPLOADED: false
OFF_HOST_DR_CLAIMED: false
```

The export remains deterministic for an identical input payload, but the input recovery payload legitimately changes as bounded ledger history advances. Therefore the current export SHA and embedded backup count are rotating samples, not release identities.

The latest sample `023eb0d5...` embeds the verified 87-file backup sample `c213efff...`; heavy export drill and full DR both PASS. Full DR still restores 11 timer definitions, 11 resource-bound drop-ins and verified ledger-chain state before reconstructing exact dev21 in a fresh venv.

Google Drive continues to pin only stable exact-candidate/rebuild identities. Rotating backup/export samples remain host-side freshness verified; binary payload is still on-host and `OFF_HOST_DR_CLAIMED=false`.