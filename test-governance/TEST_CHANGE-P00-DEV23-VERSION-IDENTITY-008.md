# TEST_CHANGE — dev23 package/version identity 008

TEST_CHANGE_ID: TEST_CHANGE-P00-DEV23-VERSION-IDENTITY-008
RUN_ID: RUN-P00-VALIDATION-002
TARGET_BASE_SOURCE_COMMIT: 86bb64938a136e3f8d6cfd0266685a01cb832b77
PREDECESSOR_TEST_CHANGE: TEST_CHANGE-P00-V03-AUTHORITY-CONSTRUCTIBILITY-007
PREDECESSOR_TEST_REVIEW: test-governance/TEST_REVIEW-P00-V03-AUTHORITY-CONSTRUCTIBILITY-007.md
TARGET_VERSION: 0.1.0.dev23
ORACLE_CHANGED: false
EXPECTED_BUSINESS_BEHAVIOR_CHANGED: false
NATIVE_EXECUTION_AUTHORIZED: false
STATUS: PENDING_NON_AUTHOR_TEST_REVIEW

## Gap closed

The canonical dev23 routing requires a dev23 source/package candidate, while the accepted dev22 source still declares `0.1.0.dev22` in both `pyproject.toml` and `src/aifilm_p00/__init__.py`. TEST_CHANGE 006/007 intentionally constrained functional product changes but did not authorize those two release-identity edits. Leaving them unchanged would make a dev23 implementation self-identify and package as dev22; silently editing them would violate the reviewed exact-scope rule.

## Narrow source-scope extension

In addition to the already reviewed functional source/test allowlist, dev23 may MODIFY only these two metadata files:

- `pyproject.toml`: set `[project].version` to `0.1.0.dev23`; description may identify the reviewed stage-derived-authority candidate; `[tool.aifilm-p00].code-review-status` may describe pending dev23 code review. No dependency, backend-availability or unrelated metadata change.
- `src/aifilm_p00/__init__.py`: set only `__version__ = '0.1.0.dev23'`. `CONTRACT_DIGEST` and `NATIVE_BACKEND_AVAILABLE` remain byte-for-byte values from dev22.

All functional source/test permissions from TEST_CHANGE 006/007 remain unchanged: ADD `src/aifilm_p00/native/stage_authority.py`; MODIFY `src/aifilm_p00/native/harness_controller.py`; ADD `tests/test_dev23_stage_authority.py`; MODIFY `tests/test_dev15_harness.py`. No other product/test path is authorized.

## Required tests

- `TV008-01`: installed/imported `aifilm_p00.__version__`, `pyproject.toml [project].version`, and expected candidate version are exactly `0.1.0.dev23`.
- `TV008-02`: `CONTRACT_DIGEST` remains `f259656c48ed24c15bd48da2bb040950ed94d8edcf1473cf6456b96578c933ee`; `NATIVE_BACKEND_AVAILABLE` remains false.
- `TV008-03`: diff allowlist rejects any metadata/source/test file outside the combined reviewed 006/007/008 set.
- `TV008-04`: package/wheel smoke identifies `0.1.0.dev23`; this is packaging evidence only, never native validation.

These assertions may be placed in the already authorized `tests/test_dev23_stage_authority.py` and packaging verification. No new public behavior or business oracle is introduced.

## Gate

Independent TEST_REVIEW must confirm the extension is necessary for truthful candidate identity, limited to the two fields/files above, and `ORACLE_CHANGED=false`. Only PASS permits dev23 authoring to modify those metadata files. This change grants no signing, HKLM, LAB/native, qualification, SITE or HOST_READY authority.
