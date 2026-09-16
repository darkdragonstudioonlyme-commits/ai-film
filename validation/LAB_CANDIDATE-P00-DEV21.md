# Phase00 disposable LAB candidate — exact dev21

```yaml
CANDIDATE_RECORD: LAB-CANDIDATE-P00-DEV21-001
STATUS: READY_FOR_EXTERNAL_REGISTRATION
APPROVED: false
EXTERNAL_AUTHORITY_ATTESTED: false
CANDIDATE_ID: 336b12af-cada-4968-8083-8a5b41e479a2
TECHNICAL_FACTS_SHA256: bca858e356faa2430a04ca2c8a069d02f3f4468927b130ef5a860fa844ecec79
PENDING_AUTHORITY_BUNDLE_RECORD: validation/LAB_PENDING_AUTHORITY_BUNDLE-P00-DEV21.md
PENDING_AUTHORITY_BUNDLE_INDEX_SHA256: fa38540df54df9ebb87929c43e9fe8fbcd09e290e93d8c5d53d7af991df8f615
PROTECTED_REGISTRATION_CANDIDATE_SHA256: 28ec95c3ecdd8ea7615843601c4657e25b503248fa2c93582cadb86c45488916
DISTRO_NAME: AI-FILM-P00-LAB
WSL_VERSION: 2
OS: Ubuntu 24.04.5 LTS
DEFAULT_USER: aifilmlab
PASSWORD_LOCKED: true
SYSTEMD: running
WINDOWS_AUTOMOUNT_ENABLED: false
WINDOWS_PATH_APPENDED: false
NO_REAL_CREDENTIALS: true
NO_PRODUCTION_MAPPINGS: true
CONTROLLER_CHANNEL_OBSERVED: WINDOWS_WSL_MANAGEMENT_OUTSIDE_GUEST
MACHINE_IDENTITY_SHA256: 0705fb633dc0155a9f501e007e6ede7bcb85c17491f7ebcbe183391051bfecf6
OPERATOR_SID_SHA256: 8d4b658f3bc550b3b867adfc19c85b42a754899fec6fe19f323db56b3aed5026
RAW_WINDOWS_IDENTITY_PUBLISHED: false
WINDOWS_PRODUCT: Windows 10 Pro
WINDOWS_DISPLAY_VERSION: 23H2
WINDOWS_BUILD: 22631.3296
```

## Exact dev21 binding

```yaml
SOURCE_COMMIT: 934659f535d81d9a4a07389531acc2b9c304fa6d
SOURCE_DIGEST: a284645e9eb60661f27eba1ea436d7ff7bbe60d6cd3e312850f1b108d32b1c62
TEST_DIGEST: c645f3d9f88fcb716f78fcff9cd9b4144b320dc4f0c8c7082346a5cfbe6d9383
CONTRACT_DIGEST: f259656c48ed24c15bd48da2bb040950ed94d8edcf1473cf6456b96578c933ee
APP_TAR_SHA256: f0276084ad99906ddeee75b5923704fa0833f17909b7e46dd4c62badd8ee3d06
APP_TAR_BYTES: 6359040
APP_FILE_COUNT: 283
APP_MANIFEST_SHA256: 2282f89da136ca54838379bdae8d9edc4b8e9c6a66770c732d8b3555eb4276f5
APP_BYTE_VERIFY_IN_LAB: PASS
LAB_RUNTIME_VERSION: 0.1.0.dev21
LAB_DOCUMENT_PREFLIGHT: PASS_HOST_READY_FALSE
PRE_V03_INVENTORY_SHA256: 7ef70d5cb5134b3328dee96747a7a7d4b26c5b8e7f2dcaffa39aa96e0556851a
PRE_V03_CASES: 86_NOT_RUN
NATIVE_PARENT_CASES_EXECUTED: 0
QUALIFICATION_ISSUED: false
HOST_READY: false
```

## Disposable recovery boundary

```yaml
BASELINE_SNAPSHOT_SHA256: 0b91d4947754be40bdb4fd3d07c8eb452dde1b6bc160829923c8e0ef005dfffd
BASELINE_SNAPSHOT_BYTES: 491407360
PRISTINE_DEV21_SNAPSHOT_SHA256: 552d6cf0ec7158ebebc5385f7dfeb7b0b3216f3536d2915877bc9425ad02127d
PRISTINE_DEV21_SNAPSHOT_BYTES: 499660800
PRISTINE_EMBEDDED_APP_MANIFEST_VERIFY: PASS
PRISTINE_EMBEDDED_PRE_V03_INVENTORY_VERIFY: PASS
RESTORE_PROBE_DISTRO: AI-FILM-P00-LAB-RP-552d6cf0
RESTORE_PROBE_APP_BYTE_VERIFY: PASS
RESTORE_PROBE_VERSION: 0.1.0.dev21
RESTORE_PROBE_INVENTORY: 86_NOT_RUN
RESTORE_PROBE_DISPOSITION: UNREGISTERED_AFTER_PASS
```

## Pending protected authority bundle

The Windows-side protected store now contains byte-verified copies of the non-consumable registration candidate (`28ec95c3...`), technical facts (`bca858e3...`) and exact 86-case authority draft (`746a2939...`). A non-consumable pending index binds those documents to dev21 and the recovery snapshots; its SHA-256 is `fa38540df54df9ebb87929c43e9fe8fbcd09e290e93d8c5d53d7af991df8f615`.

The protected registration candidate may contain raw operator identity required for later authority binding, but raw SID/machine identity is not published here. The pending index explicitly has `approved=false`, `native_consumable=false` and no external approval/attestation/suite refs.

The LAB was installed fresh from the WSL Ubuntu 24.04 source rather than cloned from the development distro. Its Windows-drive automount is disabled, its dedicated user has a locked password, and dev21 was controller-streamed without mounting development/production storage into the guest. Snapshot restore was independently exercised by importing the pristine snapshot into a temporary distro, verifying exact app bytes and the 86-case `NOT_RUN` inventory, then unregistering only that probe.

This record is **technical preparation, not authority**. It does not set a trusted `registration.execution_class=LAB`, does not create or pin an approved `lab_acceptance_suite`, and does not close V02. External registration/owner-controller attestation and exact approved fixture/plan/suite authority remain required before any native LAB stage.