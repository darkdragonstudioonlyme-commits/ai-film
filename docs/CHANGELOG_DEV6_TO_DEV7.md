# Changelog — dev6 → dev7

## Scope

Coherent implementation increment: exact native executable/dependency byte trust for Windows child processes plus effective-profile hardening.

## Source changes

- Added `src/aifilm_p00/native/executable_trust.py`.
- Added strict executable hashing/pinning to `native/filesystem.py`.
- Added production executable-trust enforcement and witness fields to `native/process.py`.
- Required `executable_policy_ref` in `native/bindings.py`.
- Reload executable policy on native authority refresh; explicitly require observed effective profile == plan profile in `native/session_driver.py`.
- Updated package version to `0.1.0.dev7`.
- Added `tests/test_dev7_executable_trust.py`.

## Evidence

- 673 workspace tests PASS.
- 90 static checks PASS.
- Native Windows/WSL/LAB/SITE not run.

## Non-claims

No design change, code-review verdict, qualification, native validation, or HOST_READY claim.
