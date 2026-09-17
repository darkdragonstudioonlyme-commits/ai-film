# Phase00 dev21 — V02 post-deployment fail-closed hardening

```yaml
DESIGN_ID: V02-POSTDEPLOY-FAILCLOSED-P00-DEV21-001
RUN_ID: RUN-P00-VALIDATION-001
STEP_ID: V02_LAB_EXECUTION_AUTHORITY
BASE_VALIDATION_COMMIT: 9a3854d80b7e4c35c5d2ec933709280ce0baa7fa
CANDIDATE_BRANCH: lane/validation-p00-v02-postdeploy-failclosed
STATUS: CANDIDATE_REVIEW_REQUIRED
PRODUCT_SOURCE_CHANGED: false
NATIVE_EXECUTION_ADVANCED: false
V03_AUTHORIZED: false
```

## Purpose

This correction closes two post-deployment fail-closed gaps without making V02 more permissive:

1. a `native-policy.candidate.json` derived from an earlier READY evaluation must not remain actionable after a later evaluation fails; and
2. a staging preflight that claims the tree was unchanged must bind regular-file bytes and symlink identity, not only size/mtime metadata.

The exact findings and evidence lifecycle are recorded in `workflow-health/HEALTH_REVIEW-WF-P00-V02-POSTDEPLOY-005.md`.

## Invariants

- `native-policy.candidate.json` is an ephemeral current-evaluation artifact. It is removed before each pre-V03 stage and on every unsuccessful exit.
- The policy candidate is retained only if intake, sealed-artifact verification, NativeStore materialization and final stopped-LAB verification all succeed in the same stage execution.
- Preflight snapshot identity includes path kind, mode, size, mtime and SHA-256 for regular files; symlink identity binds link text without following it.
- Any before/after snapshot difference yields `PREFLIGHT_MUTATED_STAGING` and cannot produce `READY_FOR_INTAKE`.
- Runtime trust installation, external key activation, approval-envelope creation and LAB start remain outside this change.
- Exact dev21 source remains artifact-only on GitHub; CI may run portable checks but must not substitute stale repository source for exact source authority.

## Regression contract

Portable server suite:

- Ed25519 external-authenticity negative/positive cases;
- same-size/same-mtime content mutation detection;
- stale READY watcher cleanup;
- stale/partial policy cleanup across authority, seal, materializer and LAB-state failures;
- current-success policy retention;
- tooling-manifest hash integrity;
- Python compile and shell syntax.

Exact-source review suite:

- `test_v02_hardened_validator.py` must run in a detached candidate tree while importing exact dev21 source commit `934659f535d81d9a4a07389531acc2b9c304fa6d` from the reviewed local source store;
- LAB artifact seal verification must remain PASS;
- real authoritative inbox must remain blocked while external key/envelope are absent.

## CI evidence semantics

The workflow intentionally separates portable server checks from exact-source review obligations. Earlier failed runs are retained as evidence of incorrect assumptions rather than hidden:

- `35268841620`: root editable-install assumption rejected;
- `35269310254`: GitHub checkout cannot substitute for artifact-only exact source;
- `35269442201`: portable split green.

Review/audit/evidence changes under the V02 surfaces trigger the portable suite again so verdict-bearing commits receive server-side regression evidence.

## Deployment rule

After independent exact-target review and audit, deployment copies only reviewed runtime/tooling files from the audited tree into `/home/dragon/ai-film-dev/validation-ops/`, verifies every manifest-bound hash, reruns portable and exact-source regressions, proves the real inbox remains blocked, proves the policy candidate/READY flag/HKLM trust remain absent, and proves `AI-FILM-P00-LAB` remains stopped. Deployment requires a separate immutable deployment record and review before `lane/validation-p00` may fast-forward.

This design does not activate authority, execute native cases, issue qualification, authorize SITE or evaluate HOST_READY.
