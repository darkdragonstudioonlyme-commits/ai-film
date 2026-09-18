# HEALTH_REVIEW-WF-P00-V02-EXACT-SOURCE-CI-006

```yaml
HEALTH_REVIEW_ID: HEALTH-WF-P00-V02-EXACT-SOURCE-CI-006
RUN_ID: RUN-P00-VALIDATION-001
STEP_ID: V02_LAB_EXECUTION_AUTHORITY
BASE_VALIDATION_COMMIT: 0e9fea427d9ec0385326c9fc1dc1c4d8ec9b27c3
CANDIDATE_BRANCH: lane/validation-p00-v02-exact-source-ci
STATUS: CANDIDATE_REVIEW_REQUIRED
PRODUCT_SOURCE_CHANGED: false
NATIVE_EXECUTION_ADVANCED: false
V03_AUTHORIZED: false
```

## Finding — V02-CI-SOURCE-ADDRESSABILITY-005

The current validation workflow still ends with `Exact-source regression remains review-gated` and states that GitHub source is `ARTIFACT_ONLY`. That was intentionally correct during the prior post-deployment hardening cycle. Canonical source visibility later changed: exact dev21 commit `934659f535d81d9a4a07389531acc2b9c304fa6d` is now remotely browseable as a full Git tree at `source/p00-dev21-exact`, with exact commit identity remaining authoritative over the branch name.

Leaving the old skip in place therefore creates under-enforced CI: the exact-source-dependent hardened-validator regression is available to the server but is not being executed there.

## Correction

The candidate workflow checks out exact source by immutable commit SHA into a second worktree, verifies the checkout identity, binds its `src` directory to the validator's reviewed absolute source path on the ephemeral runner, and runs `test_v02_hardened_validator.py` unchanged. Runtime validator bytes and import semantics are not patched to make CI pass.

Local pre-review execution against exact source already passes all six hardened-validator negative cases. The exact source package declares zero dependencies; validation tooling continues installing only `cryptography` for Ed25519 verification.

## Boundary

This is server enforcement only. The real authority inbox remains external; external key provenance, signed envelope and protected object graph remain absent. LAB must remain stopped, all 86 cases remain NOT_RUN, and V03 remains unauthorized.

## Learning disposition

This finding is follow-through on the already canonical source-visibility/source-addressability learning. It does not create a new learning lifecycle record: when exact source becomes remotely addressable, CI should retire a source-unavailability exception rather than preserve the old skip indefinitely.
