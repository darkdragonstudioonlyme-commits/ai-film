# Phase00 dev21 — production-like WSL runtime

```yaml
RUNTIME_SETUP_ID: WSL-PRODLIKE-P00-DEV21-001
STATUS: READY_NON_NATIVE
SOURCE_COMMIT: 934659f535d81d9a4a07389531acc2b9c304fa6d
SOURCE_DIGEST: a284645e9eb60661f27eba1ea436d7ff7bbe60d6cd3e312850f1b108d32b1c62
TEST_DIGEST: c645f3d9f88fcb716f78fcff9cd9b4144b320dc4f0c8c7082346a5cfbe6d9383
CONTRACT_DIGEST: f259656c48ed24c15bd48da2bb040950ed94d8edcf1473cf6456b96578c933ee
V21_PACKAGE_SHA256: f6ee158a318614f8bbef28be7af82549e0a268425da28147a2fa7b14c7b3d3e3
WSL_DISTRO: Ubuntu-24.04
PYTHON: 3.12.3
VALIDATION_VENV: /home/dragon/ai-film-dev/venvs/validation-dev21
VALIDATION_VENV_PIP: 24.0
PRODLIKE_ROOT: /home/dragon/ai-film-runtime/dev21
STABLE_CURRENT: /home/dragon/ai-film-runtime/current
APP_ROOT: /home/dragon/ai-film-runtime/dev21/app
APP_FILE_COUNT: 283
APP_BYTE_VERIFY: PASS
APP_MANIFEST_SHA256: 07fcf4a31c6ffabc3628ba12584d249680cea1344e26fb1d2cbe2983e30270fa
APP_READ_ONLY: true
RUNTIME_VENV: /home/dragon/ai-film-runtime/dev21/venv
RUNTIME_DEPENDENCIES: []
PIP_CHECK: PASS
BUILD_WHEEL: aifilm_p00_contracts-0.1.0.dev21-py3-none-any.whl
BUILD_WHEEL_SHA256: 9b565b24a896879bd7bd812c43efcc741d8bc2eb08c0b23318b1e66c64b9e7e8
SETUPTOOLS_68_1_2_WHEEL_SHA256: 3d8083eed2d13afc9426f227b24fd1659489ec107c0e86cec2ffdde5c92e790b
WHEEL_0_42_0_SHA256: 177f9c9b0d45c47873b619f5b650346d632cdc35fb5e4d25058e09c9e581433d
RUNTIME_MANIFEST_SHA256: 02e48cbf39da75eee10135fa87bfc622496570a80ff5048231648e225b458dd4
VERIFY_RUNTIME_SHA256: 0b6955ccad668eb2271f84e78ecacb77c838488af4ee847d6b9f8da61e863f1f
ENVIRONMENT_POLICY: ENV_CLEARED_ALLOWLIST_ONLY
RUNTIME_VERIFY: "PRODLIKE_RUNTIME_VERIFY_PASS 283 86 NOT_RUN"
NATIVE_LAB_AUTHORITY: false
NATIVE_EXECUTION_STARTED: false
HOST_READY: false
```

## Deployment shape

The runtime is intentionally not a plain wheel install. The exact dev21 package resolves its normative `contracts/` relative to the package source root; the built wheel contains package modules but no root `contracts/` or `docs/`. Treating that wheel alone as the native runtime would therefore break the reviewed authority layout. The wheel is retained as a reproducible build artifact, while the active WSL runtime uses an immutable exact-Git app tree plus an isolated Python venv and a fixed `.pth` pointing only to that tree.

`/home/dragon/ai-film-runtime/dev21/app` was created by `git archive` of exact source commit `934659f...`, contains exactly 283 tracked files, and every deployed file byte was reverified against its Git blob. The app tree is read-only. Mutable state is separated into `var/lib`, `var/log`, `var/tmp`, and `evidence`; the stable `current` symlink points to dev21.

The launcher `/home/dragon/ai-film-runtime/dev21/bin/aifilm-p00` clears the inherited environment with `env -i` and repopulates only an explicit allowlist (`HOME`, user identity, locale, fixed PATH, Python isolation flags and runtime TMPDIR). No sudo/password secret was read, copied or persisted by this setup, and arbitrary inherited secret environment variables are not forwarded into the runtime process.

## Verification

The production-like runtime independently passed:

- 283/283 deployed app files byte-identical to exact dev21;
- app integrity manifest verification;
- isolated Python 3.12.3 runtime and `pip check` PASS;
- `python -m aifilm_p00 --version` => `0.1.0.dev21`;
- document-only `preflight --workspace-only` => `source_kind=DOCUMENT`, `host_ready=false`;
- document-only `recovery-notes` => `native_execution=false`;
- native inventory metadata => 86 cases, all `NOT_RUN`, zero parent cases executed, no qualification issued;
- validation workspace after recreating the full pip-enabled venv => 760 tests PASS, 101 static PASS, dirty before/after = 0.

This record is preparation evidence only. It does not register the current Windows/WSL host as disposable LAB, does not grant native LAB/SITE execution authority, and does not advance `RUN-P00-VALIDATION-001` beyond `V02_LAB_EXECUTION_AUTHORITY`.