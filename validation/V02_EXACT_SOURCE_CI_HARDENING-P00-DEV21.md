# Phase00 dev21 — V02 exact-source CI hardening

```yaml
DESIGN_ID: V02-EXACT-SOURCE-CI-P00-DEV21-001
RUN_ID: RUN-P00-VALIDATION-001
STEP_ID: V02_LAB_EXECUTION_AUTHORITY
BASE_VALIDATION_COMMIT: 0e9fea427d9ec0385326c9fc1dc1c4d8ec9b27c3
CANDIDATE_BRANCH: lane/validation-p00-v02-exact-source-ci
EXACT_SOURCE_COMMIT: 934659f535d81d9a4a07389531acc2b9c304fa6d
EXACT_SOURCE_REMOTE_REF: source/p00-dev21-exact
STATUS: CANDIDATE_REVIEW_REQUIRED
PRODUCT_SOURCE_CHANGED: false
NATIVE_EXECUTION_ADVANCED: false
V03_AUTHORIZED: false
```

## Purpose

Retire the validation CI assumption that exact dev21 source is unavailable remotely. That assumption was correct when post-deployment fail-closed hardening was reviewed, but the later formal source-visibility handoff published the exact accepted source commit as a full remote Git tree at `source/p00-dev21-exact`.

This revision makes the exact-source-dependent hardened-validator regression server-enforced without changing validator semantics, source bytes, V02 predicates or native execution state.

## Exact-source binding

The workflow must not treat the mutable branch name as source authority. It performs a second checkout by exact commit SHA `934659f535d81d9a4a07389531acc2b9c304fa6d`, verifies `HEAD` equals that identity, then binds only the checkout's `src` directory to the validator's reviewed runtime path on the ephemeral GitHub runner.

The runtime validator is not patched. `test_v02_hardened_validator.py` executes the same `v02-authority-intake.py` bytes that are shipped in validation tooling while importing exact dev21 source from the path the production validator already expects.

## Server regression contract

`Validation V02 Tooling` must now pass all of the following on candidate, review, audit and canonical validation-lane commits:

- Python compile and shell syntax;
- external Ed25519 authenticity regression;
- preflight byte-integrity regression;
- watcher fail-closed regression;
- pre-V03 stale/partial-policy fail-closed regression;
- tooling-manifest integrity;
- exact source checkout identity assertion;
- exact-source hardened-validator regression, 6 cases.

Only `cryptography` is installed as a tooling dependency; exact dev21 `pyproject.toml` declares no runtime package dependencies.

## Historical evidence semantics

Earlier CI failures and the portable/exact-source split remain valid historical evidence. This change does not rewrite those records: remote source addressability changed later. The stale CI skip message is now automation debt because continuing to skip an available exact-source regression would under-enforce a reviewed control.

## Non-goals

No approval envelope is created, no external key is activated, no trust anchor is installed, no LAB is started, no native case is executed, no qualification is issued, no SITE validation occurs and HOST_READY is not evaluated.
