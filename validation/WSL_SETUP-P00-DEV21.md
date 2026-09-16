# Phase00 dev21 — WSL validation preparation

```yaml
SETUP_ID: WSL-SETUP-P00-DEV21-001
STATUS: COMPLETE
WSL_DISTRO: Ubuntu-24.04
WSL_USER: dragon
VALIDATION_WORKTREE: /home/dragon/ai-film-dev/validation
VALIDATION_HEAD: 934659f535d81d9a4a07389531acc2b9c304fa6d
WORKTREE_DIRTY_FILES: 0
PACKAGE: /home/dragon/ai-film-dev/artifacts/IMPL-P00-001_IMPLEMENTATION_PACKAGE_V21.zip
PACKAGE_SHA256: f6ee158a318614f8bbef28be7af82549e0a268425da28147a2fa7b14c7b3d3e3
PACKAGE_MANIFEST_ENTRIES: 283
PACKAGE_GIT_BYTE_VERIFY: PASS
PYTHON: 3.12.3
PYTHON_MODE: SYSTEM_PYTHON
VENV_STATUS: NOT_CREATED_PYTHON3_12_VENV_PACKAGE_MISSING
SUDO_NONINTERACTIVE: false
WORKSPACE_TESTS: "760 PASS / 0 failure / 0 error / 0 skip"
STATIC_CHECKS: "101 PASS / 0 failed"
NATIVE_INVENTORY_METADATA: "86 cases / all NOT_RUN / zero parent cases executed"
NATIVE_EXECUTION_STARTED: false
LAB_AUTHORITY_GRANTED: false
```

## Installed/prepared layout

- exact detached dev21 Git worktree: `/home/dragon/ai-film-dev/validation`;
- separate evidence root: `/home/dragon/ai-film-dev/run-evidence/validation`;
- package staging root: `/home/dragon/ai-film-dev/validation-staging/package-v21`;
- environment helper: `/home/dragon/ai-film-dev/validation-env.sh`;
- safe verification helper: `/home/dragon/ai-film-dev/validation-safe-checks.sh`;
- package/Git-byte verifier: `/home/dragon/ai-film-dev/validation-staging/verify_dev21.py`.

The attempted virtual environment was not retained because Ubuntu lacks `python3.12-venv` and passwordless sudo is unavailable. Dev21 declares no third-party runtime dependencies, so setup uses system Python 3.12.3 and exact `PYTHONPATH` without changing system packages.

## Verification

`validation-safe-checks.sh` independently verified exact Git/package identity, all manifest member hashes/bytes, reproduced 760 workspace tests and 101 static checks, and executed only metadata mode `run_native_acceptance_tests.py --list`. The inventory remained 86 cases at `NOT_RUN`, `parent_cases_executed=0`, `qualification_issued=false`, `host_ready=false`.

This setup does not classify the current development host as LAB and does not grant or consume native LAB/SITE execution authority. `RUN-P00-VALIDATION-001 / V02_LAB_EXECUTION_AUTHORITY` remains the current blocked validation step.