# DOCSYS-V2-R9 — V48 CI credential isolation

DESIGN_ID: DOCSYS-R9-V48-CI-CREDENTIAL-ISOLATION
TARGET_RELEASE: DOCSYS-V2-R9
TARGET_STATE_VERSION: 48
REVISION: R21_V48_CI_CREDENTIAL_ISOLATION
BASE_MAIN_COMMIT: 49a4829c879c5964ecad235c79d504bd6ccfc5d0
DESIGN_BRANCH: lane/docs-v2-r9-v48-ci-credential-isolation-design
REVIEW_BRANCH: lane/docs-v2-r9-v48-ci-credential-isolation-review
AUDIT_BRANCH: lane/docs-v2-r9-v48-ci-credential-isolation-audit
REQUIRED_REVIEW_ID: DOC-V2-R9-REVIEW-022
REQUIRED_AUDIT_ID: DOC-V2-R9-AUDIT-022
PRODUCT_SOURCE_CHANGED: false
NATIVE_EXECUTION_ADVANCED: false

## Purpose

Prevent Documentation Governance from exposing a persisted checkout authorization header to repository-controlled code, and convert the repeated validation/governance CI exposure into a reusable lifecycle-managed learning.

## Evidence and correction

V47 main run `35296390094` / job `105449688523` logs `persist-credentials: true` and a masked `http.https://github.com/.extraheader AUTHORIZATION: basic ***` that remains configured until checkout post-job cleanup. Repository-controlled Python checkers execute before that cleanup.

V48 sets checkout `persist-credentials: false` and immediately verifies no local `http.*.extraheader` exists before Python/checker execution. The workflow remains `contents: read` and uses no custom token. Transient masked authentication internal to the fetch is acceptable only if removed before checkout action completion.

## Learning lifecycle

`LEARNING-CI-CREDENTIAL-ISOLATION-013` captures the systemic rule because the same exposure occurred independently in validation CI and Documentation Governance. R22/A22 may activate it, but its effectiveness remains PENDING_MEASUREMENT until the next qualifying CI workflow change or documentation promotion after activation.

## Invariants

- V02/native state and accepted dev21 identity remain unchanged;
- validation head remains `cf819edd0e05ffd8afd4bc2051116d5a4392368b`;
- continuity remains 0/3 PENDING_MEASUREMENT;
- platform branch protection remains NOT_ENFORCED;
- no credential value may be printed by the explicit isolation check.

## Exact-tree rule

R22/A22 are final verdict IDs for one semantic tree. Only verdict records may be added after exact review; any workflow/state/learning edit reopens review/audit.
