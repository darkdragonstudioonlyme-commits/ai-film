# Phase00 dev21 — V02 CI credential isolation

```yaml
DESIGN_ID: V02-CI-CREDENTIAL-ISOLATION-P00-DEV21-001
RUN_ID: RUN-P00-VALIDATION-001
STEP_ID: V02_LAB_EXECUTION_AUTHORITY
BASE_VALIDATION_COMMIT: f1d4755759c5abb1f4008cf757b75a0b2072277a
CANDIDATE_BRANCH: lane/validation-p00-v02-ci-credential-isolation
EXACT_SOURCE_COMMIT: 934659f535d81d9a4a07389531acc2b9c304fa6d
STATUS: CANDIDATE_REVIEW_REQUIRED
PRODUCT_SOURCE_CHANGED: false
NATIVE_EXECUTION_ADVANCED: false
V03_AUTHORIZED: false
```

## Purpose

Remove persisted GitHub checkout credentials from the V02 CI workspace before any exact product source is imported. Canonical validation run `35295269302` proved the exact-source regression is server-enforced, but its checkout logs also showed both `actions/checkout@v4` invocations using `persist-credentials: true` and writing the masked GitHub authorization extraheader into local Git config until post-job cleanup.

The source is accepted/reviewed, but source-under-test does not need repository credentials. Least-privilege CI should not expose a reusable checkout authorization header to code executed during regression when the job only performs read-only checkout and tests.

## Design

Both repository checkouts set `persist-credentials: false`. Before source identity verification, path binding or hardened-validator execution, CI must prove that neither the primary checkout nor `exact-source` checkout has an `http.*.extraheader` entry in local Git config.

The workflow still has only `contents: read` GitHub-token permissions and still checks out exact dev21 by immutable SHA. No custom token, secret file or external credential is introduced.

## Fail-closed rule

If either checkout persists an HTTP authorization extraheader, the explicit credential-isolation step fails and exact-source code is not executed. This check is server evidence about credential storage state; it never prints the authorization value.

## Non-goals

No validator/tooling byte changes, no trust-anchor changes, no external key/envelope handling, no LAB start, no native execution, no qualification, SITE or HOST_READY advancement.
