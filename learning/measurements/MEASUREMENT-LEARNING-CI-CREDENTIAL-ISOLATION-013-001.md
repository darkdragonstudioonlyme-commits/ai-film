# MEASUREMENT-LEARNING-CI-CREDENTIAL-ISOLATION-013-001

LEARNING_ID: LEARNING-CI-CREDENTIAL-ISOLATION-013
METRIC_ID: CI_CREDENTIAL_ISOLATION_RECHECK_V1
METRIC_VERSION: 1
SUCCESS_METRIC_SHA256: 55df0546e293181476c762ab7f5b28df45f4f44458f353db0e68eb3b031fdbea
SCOPE: "First qualifying Documentation Governance promotion cycle after V48 R22/A22 activation of learning 013"
SAMPLE_REQUIREMENT: "A post-activation design commit must fetch successfully with least-privilege read access, remove checkout credentials before repository-controlled code, pass an explicit no-extraheader check, and preserve the reviewed workflow isolation rule."
OBSERVATIONS: "V49 sample 171922f3c1bcdbec405687a69e06c974c88cac49 ran Documentation Governance CI 35299469231 / job 105458870819. Checkout completed with persist-credentials=false; step 3 'Verify checkout credentials are not persisted' passed before setup-python and all repository-controlled lifecycle/governance/continuity Python. The workflow retained permissions contents: read, used no custom token, read-only checkout succeeded, and the complete governance suite passed."
EXPECTED_PREDICATE: "Repository-controlled code begins only after persisted checkout authorization is absent; reviewed workflows do not reintroduce persisted checkout credentials; least-privilege read-only fetch remains functional."
MEASUREMENT_COMMIT: 171922f3c1bcdbec405687a69e06c974c88cac49
RESULT: PASS
REVIEW_ID: DOC-V2-R9-REVIEW-023

## Immutable success metric

The next qualifying CI workflow change or documentation promotion executes repository-controlled code only after checkout credentials are non-persistent and an explicit no-extraheader check passes; no reviewed workflow reintroduces persisted checkout authorization, while required read-only fetches still succeed.

## Evidence identities

- workflow-health/HEALTH_REVIEW-DOCSYS-R9-V49-VALIDATION-P7-026.md
- docs/DOCUMENTATION_SYSTEM_R9_V49_VALIDATION_P7_RECONCILIATION.md
- sample commit 171922f3c1bcdbec405687a69e06c974c88cac49
- Documentation Governance run 35299469231, job 105458870819

## Review boundary

This receipt is candidate semantic evidence. R23/A23 must independently verify that V49 is the first qualifying Documentation Governance promotion cycle after V48 activation, that the isolation check preceded repository-controlled code, that read-only fetch succeeded, and that no product/native/V02 progression occurred.
