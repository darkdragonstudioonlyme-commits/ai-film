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
PYTHON_MODE: ISOLATED_VENV_FULL
VENV: /home/dragon/ai-film-dev/venvs/validation-dev21
VENV_STATUS: READY
VENV_PIP: 24.0
PIP_CHECK: PASS
RUNTIME_DEPENDENCIES: []
PRODLIKE_RUNTIME_RECORD: validation/WSL_PRODLIKE_RUNTIME-P00-DEV21.md
WORKSPACE_TESTS: "760 PASS / 0 failure / 0 error / 0 skip"
STATIC_CHECKS: "101 PASS / 0 failed"
NATIVE_INVENTORY_METADATA: "86 cases / all NOT_RUN / zero parent cases executed"
DIRTY_BEFORE_SAFE_CHECKS: 0
DIRTY_AFTER_SAFE_CHECKS: 0
NATIVE_EXECUTION_STARTED: false
LAB_AUTHORITY_GRANTED: false
```

## Installed/prepared layout

- exact detached dev21 Git worktree: `/home/dragon/ai-film-dev/validation`;
- isolated full Python environment: `/home/dragon/ai-film-dev/venvs/validation-dev21`;
- separate evidence root: `/home/dragon/ai-film-dev/run-evidence/validation`;
- preserved setup evidence: `/home/dragon/ai-film-dev/run-evidence/validation/wsl-setup-dev21`;
- package staging root: `/home/dragon/ai-film-dev/validation-staging/package-v21`;
- environment helper: `/home/dragon/ai-film-dev/validation-env.sh`;
- safe verification helper: `/home/dragon/ai-film-dev/validation-safe-checks.sh`;
- package/Git-byte verifier: `/home/dragon/ai-film-dev/validation-staging/verify_dev21.py`;
- production-like immutable runtime: `/home/dragon/ai-film-runtime/dev21`, documented separately in `WSL_PRODLIKE_RUNTIME-P00-DEV21.md`.

The initial setup used `python3 -m venv --without-pip` because `python3.12-venv`/ensurepip was absent. After the operator installed the required Ubuntu venv package, the validation venv was recreated normally and now includes pip 24.0. No project runtime dependency was added because dev21 declares `dependencies=[]`.

## Verification

After the full venv recreation, `validation-safe-checks.sh` again verified exact Git/package identity, all manifest member hashes/bytes, reproduced 760 workspace tests and 101 static checks, and executed only metadata mode `run_native_acceptance_tests.py --list`. Generated tracked evidence is copied to the external validation evidence root and restored from exact dev21 before exit; the validation worktree remained clean (`DIRTY_BEFORE=0`, `DIRTY_AFTER=0`).

The inventory remains 86 cases at `NOT_RUN`, `parent_cases_executed=0`, `qualification_issued=false`, `host_ready=false`.

This setup does not classify the current development host as LAB and does not grant or consume native LAB/SITE execution authority. `RUN-P00-VALIDATION-001 / V02_LAB_EXECUTION_AUTHORITY` remains the current blocked validation step.