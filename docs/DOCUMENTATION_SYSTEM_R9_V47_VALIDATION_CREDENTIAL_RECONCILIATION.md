# DOCSYS-V2-R9 — V47 validation credential-isolation reconciliation

DESIGN_ID: DOCSYS-R9-V47-VALIDATION-CREDENTIAL-RECONCILIATION
TARGET_RELEASE: DOCSYS-V2-R9
TARGET_STATE_VERSION: 47
REVISION: R20_V47_VALIDATION_CREDENTIAL_RECONCILIATION
BASE_MAIN_COMMIT: 6a9d5327257ce930d68be1425e74413a1047ca8d
DESIGN_BRANCH: lane/docs-v2-r9-v47-validation-credential-reconciliation-design
REVIEW_BRANCH: lane/docs-v2-r9-v47-validation-credential-reconciliation-review
AUDIT_BRANCH: lane/docs-v2-r9-v47-validation-credential-reconciliation-audit
REQUIRED_REVIEW_ID: DOC-V2-R9-REVIEW-021
REQUIRED_AUDIT_ID: DOC-V2-R9-AUDIT-021
PRODUCT_SOURCE_CHANGED: false
NATIVE_EXECUTION_ADVANCED: false

## Purpose

Reconcile canonical main after validation lane promotion `cf819edd0e05ffd8afd4bc2051116d5a4392368b` and publish the audited rule that checkout credentials must not persist into exact-source regression execution.

## Evidence

Validation credential-isolation design `1070344d2199e49d9539cda16fc678af4067fbdb`, review `68bd8622229aacfd0b0534279d61ee2ad46f9672`, audit/current lane `cf819edd0e05ffd8afd4bc2051116d5a4392368b`, and post-promotion lane run `35296006311` / job `105448549183` preserve all existing V02 regressions while requiring `persist-credentials: false` on both checkouts and proving no HTTP authorization extraheader remains before exact source executes.

## Invariants

- canonical validation evidence head equals `cf819edd0e05ffd8afd4bc2051116d5a4392368b`;
- exact source identity remains immutable SHA `934659f535d81d9a4a07389531acc2b9c304fa6d`;
- checkout authentication may be used transiently by `actions/checkout` for fetch but is not persisted into later regression steps;
- V02 remains BLOCKED and all 86 native cases remain NOT_RUN;
- continuity remains 0/3 PENDING_MEASUREMENT;
- no new learning effectiveness claim or platform branch-protection claim is introduced.

## Exact-tree rule

R21/A21 are final verdict IDs for this semantic tree. The reviewed design already describes intended post-promotion state; only immutable verdict records may be added before exact fast-forward.
