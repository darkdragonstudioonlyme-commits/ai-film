# HEALTH_REVIEW-WF-P00-V02-CI-CREDENTIAL-ISOLATION-007

```yaml
HEALTH_REVIEW_ID: HEALTH-WF-P00-V02-CI-CREDENTIAL-ISOLATION-007
RUN_ID: RUN-P00-VALIDATION-001
STEP_ID: V02_LAB_EXECUTION_AUTHORITY
BASE_VALIDATION_COMMIT: f1d4755759c5abb1f4008cf757b75a0b2072277a
STATUS: CANDIDATE_REVIEW_REQUIRED
PRODUCT_SOURCE_CHANGED: false
NATIVE_EXECUTION_ADVANCED: false
V03_AUTHORIZED: false
```

## Finding — V02-CI-CREDENTIAL-EXPOSURE-006

Canonical validation CI run `35295269302` / job `105446413667` successfully enforced exact-source regression. Its decoded GitHub Actions log records `persist-credentials: true` for both checkout actions and shows a masked `http.https://github.com/.extraheader AUTHORIZATION: basic ***` being configured locally, then removed only during post-job cleanup.

The hardened-validator regression imports exact accepted source before that cleanup. The source does not require GitHub credentials and the job performs no authenticated Git write. Persisting the token-derived authorization header during source execution is unnecessary credential exposure.

## Correction

Set `persist-credentials: false` on both checkout actions and insert a fail-closed check that no local `http.*.extraheader` exists in either checkout before exact source is imported. The check examines key presence only and never prints a credential value.

## Boundary

This is CI credential hygiene only. Validation tooling/runtime bytes, exact source identity, V02 predicates and the external authority contract remain unchanged. V02 stays blocked and V03 stays unauthorized.
