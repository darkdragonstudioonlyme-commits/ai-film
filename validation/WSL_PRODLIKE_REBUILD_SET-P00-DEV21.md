# Phase00 dev21 — Windows NTFS runtime rebuild set

```yaml
REBUILD_RECORD_ID: WSL-PRODLIKE-REBUILD-P00-DEV21-001
STATUS: PASS
SOURCE_COMMIT: 934659f535d81d9a4a07389531acc2b9c304fa6d
SOURCE_DIGEST: a284645e9eb60661f27eba1ea436d7ff7bbe60d6cd3e312850f1b108d32b1c62
TEST_DIGEST: c645f3d9f88fcb716f78fcff9cd9b4144b320dc4f0c8c7082346a5cfbe6d9383
CONTRACT_DIGEST: f259656c48ed24c15bd48da2bb040950ed94d8edcf1473cf6456b96578c933ee
HOST_REBUILD_ROOT: C:\Users\Admin\AppData\Local\AI-FILM\runtime-rebuild\dev21
HOST_FILESYSTEM: NTFS
PACKAGE_SHA256: f6ee158a318614f8bbef28be7af82549e0a268425da28147a2fa7b14c7b3d3e3
PACKAGE_SIZE_BYTES: 1184312
WHEEL_SHA256: 9b565b24a896879bd7bd812c43efcc741d8bc2eb08c0b23318b1e66c64b9e7e8
APP_MANIFEST_SHA256: 07fcf4a31c6ffabc3628ba12584d249680cea1344e26fb1d2cbe2983e30270fa
RUNTIME_MANIFEST_SHA256: 8227e8350208314db087612889d2b481393c67ec3a5eb0bfa84a869c1d0829a2
REBUILD_INDEX_SHA256: 40cc6df68e8ca536acf183e8cbf63ce157845e4f33d2659c92efcb41fbc3ed54
REBUILD_VERIFY_SCRIPT_SHA256: 8db9a92b236e2b718aabb9fcc177ce797bd09e27e68e8edba0a16351d3b1e473
REBUILD_SERVICE_SHA256: bd7c3a7b8ece1d136a29e0fe5dea0a6210cead7c8f5152f99c6ec8f497796fca
REBUILD_TIMER_SHA256: df74a3e7cbbaa2f290bdf1983c5ac81ac45d7ad8a2ace2a168833c78dfcb90b3
REBUILD_TIMEOUT_DROPIN_SHA256: f6ddc0822cc97e489773b9bbbdefb3ab47d6eff9770def066ff79602f9ff57ed
REBUILD_EFFECTIVE_TIMEOUT: 10min
REBUILD_TIMER: "enabled active / boot+12h"
REBUILD_SERVICE_RESULT: success
REBUILD_SYSTEMD_SECURITY: "4.1 OK"
REBUILD_LIGHT_VERIFY: PASS
REBUILD_COLD_PROBE: PASS
REBUILD_ISOLATED_VENV: PASS
REBUILD_VENV_MODE: "python3 -m venv --without-pip + app/src .pth"
LIVE_RUNTIME_VENV_USED: false
PYTHONPATH_USED_BY_COLD_PROBE: false
REBUILT_VERSION: 0.1.0.dev21
REBUILT_APP_BYTE_VERIFY: "283/283 PASS"
REBUILT_NATIVE_INVENTORY: "86 NOT_RUN / 0 parent cases / qualification false"
REBUILT_HOST_READY: false
WINDOWS_ACL_INHERITANCE: disabled
WINDOWS_ACL_PRINCIPALS: "NT AUTHORITY\\SYSTEM + DESKTOP-LCISMET\\Admin only"
NATIVE_AUTHORITY_INCLUDED: false
PROTECTED_IDENTITY_INCLUDED: false
NATIVE_EXECUTION_STARTED: false
```

The rebuild set exists because the exact dev21 source is not fully mirrored as a remotely browsable Git tree. A control-state backup alone would not be sufficient to reconstruct the exact runtime after loss of the WSL distro. The Windows-side rebuild directory therefore carries only reviewed, non-secret reconstruction artifacts: `IMPL-P00-001_IMPLEMENTATION_PACKAGE_V21.zip`, the dev21 wheel artifact, the 283-entry app manifest, the runtime manifest and a hash-bound rebuild index.

The cold probe uses the **NTFS copy as its source**. It verifies every indexed file hash/size, rejects unsafe ZIP paths, extracts the V21 package into an isolated temporary directory and re-verifies all 283 source files against `app-manifest.sha256`. It then creates a brand-new Python venv with `--without-pip`, writes the same `app/src` `.pth` shape used by the live runtime, and executes version, document-only preflight and native-inventory listing through that disposable venv. It does not use the live dev21 venv and does not rely on `PYTHONPATH`.

The reconstructed runtime reports version `0.1.0.dev21`, `host_ready=false`, and the full 86-case inventory still `NOT_RUN` with zero parent cases and no qualification. `aifilm-p00-rebuild-verify.timer` performs the cold probe after boot and every twelve hours. The service is hardened (`4.1 OK` observed exposure), has a ten-minute start timeout and no network socket families or capabilities. The runtime health collector also performs a lightweight rebuild-set verification on each health cycle and requires the latest cold-probe service result to be `success`.

The current 39-file safe control backup and its NTFS mirror contain this exact rebuild verifier SHA and passed a direct mirror probe proving the venv-independent verifier is recoverable. The rebuild directory has Windows ACL inheritance removed and only SYSTEM plus the current operator retain Full Control. It contains no approval envelope, protected authority object, raw SID/MachineGuid, credential, qualification or native execution evidence.

This is same-host, second-filesystem rebuild readiness; it is **not** claimed as off-host disaster recovery or LAB/SITE authority. This record does not advance `RUN-P00-VALIDATION-001` beyond V02 and does not alter any of the 86 native acceptance statuses.
