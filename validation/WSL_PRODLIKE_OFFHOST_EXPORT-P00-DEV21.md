# Phase00 dev21 — transfer-ready off-host DR export

```yaml
EXPORT_RECORD_ID: WSL-PRODLIKE-OFFHOST-EXPORT-P00-DEV21-001
STATUS: TRANSFER_READY_WITH_OFFHOST_METADATA
SOURCE_COMMIT: 934659f535d81d9a4a07389531acc2b9c304fa6d
EXPORT_PATH: C:\Users\Admin\AppData\Local\AI-FILM\offhost-export\dev21\AI-FILM-P00-DEV21-OFFHOST-DR-EXPORT.zip
EXPORT_SHA256: 11ab63f8a0ef155e9df5004798ef4ce1bd4c550938eddf01fc21e567de7de28b
EXPORT_SIZE_BYTES: 1373626
EXPORT_PAYLOAD_FILES: 7
CONTROL_BACKUP: control-state-20260916T200952Z.tar.gz
CONTROL_BACKUP_SHA256: 29a92f78683ff71ba118023516cd32783bc45cc8232dbebf3ddf90b9b52309e1
CONTROL_BACKUP_FILES: 39
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
OFF_HOST_PAYLOAD_UPLOADED: false
NATIVE_AUTHORITY_INCLUDED: false
PROTECTED_IDENTITY_INCLUDED: false
CREDENTIALS_INCLUDED: false
OFF_HOST_COPY_COMPLETED: false
OFF_HOST_DR_CLAIMED: false
```

The export bundles the current verified 39-file control backup plus the exact reviewed non-secret runtime reconstruction set (V21 implementation package, dev21 wheel, app manifest, runtime manifest and rebuild index) into one portable ZIP. The embedded `OFFHOST-DR-MANIFEST.json` binds every payload by size and SHA-256 and explicitly records that native authority, protected identity and credentials are not included.

A self-contained transfer drill used **only the portable ZIP as its input**. It verified all seven payloads, independently reverified all 39 files in the embedded control backup, extracted the implementation package, verified all 283 source bytes, created a fresh `python3 -m venv --without-pip`, reproduced the live `.pth` runtime shape, and executed version/preflight/inventory from that rebuilt venv. The result was `0.1.0.dev21`, `host_ready=false`, `86 NOT_RUN`, zero parent cases and no qualification.

The export directory has Windows ACL inheritance removed and only SYSTEM plus the current operator have Full Control. This makes the bundle ready for transfer through a future trusted binary transport without repackaging or touching the protected LAB authority domain.

A private Google Drive integrity manifest is now stored under folder `AI-FILM DR`. Readback verified the export filename/SHA, exact candidate identities, current control-backup SHA, rebuild identities, exclusions and the explicit boundary `PAYLOAD_NOT_UPLOADED / OFF_HOST_DR_CLAIMED=false`. The Drive file is not publicly shared. This provides an off-host checksum/integrity anchor only; the binary DR export payload remains on the original host.

The binary bundle is therefore **not currently off-host**. Google Drive binary upload requires a connector `file_uri`, while the available Remote Desktop connector cannot materialize remote WSL/Windows files into that form; Google Drive Desktop is also not installed/mounted. No OAuth credential workaround, base64 repository upload or weaker transport was introduced. Canonical `OFF_HOST_DR_CLAIMED=false` remains correct.

This export/metadata anchor does not grant LAB/SITE/native execution authority and does not advance `RUN-P00-VALIDATION-001` beyond V02.
