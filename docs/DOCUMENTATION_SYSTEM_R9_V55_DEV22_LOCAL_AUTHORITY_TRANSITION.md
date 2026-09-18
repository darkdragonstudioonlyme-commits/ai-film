# DOCSYS-V2-R9 — V55 dev22 local-authority transition

DESIGN_ID: DOCSYS-R9-V55-DEV22-LOCAL-AUTHORITY-TRANSITION
TARGET_RELEASE: DOCSYS-V2-R9
TARGET_STATE_VERSION: 55
REVISION: R28_V55_DEV22_LOCAL_AUTHORITY_TRANSITION
BASE_MAIN_COMMIT: 34fd5cb57dae9306461e620526f60d9df1f2beb2
DESIGN_BRANCH: lane/docs-v2-r9-v55-dev22-local-authority-transition-design
REVIEW_BRANCH: lane/docs-v2-r9-v55-dev22-local-authority-transition-review
AUDIT_BRANCH: lane/docs-v2-r9-v55-dev22-local-authority-transition-audit
REQUIRED_REVIEW_ID: DOC-V2-R9-REVIEW-029
REQUIRED_AUDIT_ID: DOC-V2-R9-AUDIT-029
PRODUCT_SOURCE_CHANGED_BY_DOCSYS: false
NATIVE_EXECUTION_ADVANCED: false

## Accepted candidate transition

Dev22 exact source `86bb64938a136e3f8d6cfd0266685a01cb832b77` is a direct successor of reviewed dev21 and is remotely browseable at `source/p00-dev22-local-authority-exact`. Deterministic package `c2ea52087039f4c7b98c53a7cc0eaf1a4a0f931645f86491bf2eb8ef12956aae` contains 284 exact tracked source files plus manifest; wheel SHA is `e5a7ae51...`. Independent TEST_REVIEW and CODE_REVIEW reproduce 766 workspace PASS, 101 static PASS and unchanged contract digest.

The product behavior change is deliberate and owner-authorized: `controller_external=false` is a valid LAB local-controller mode, while `true` remains valid for external-controller LABs. Both modes preserve disposable/no-real-credential/no-production-mapping containment, and native fixture controller mode must match registration. The local mode is explicitly lower assurance and must not be described as independent external authority.

## Learning lifecycle normalization

V54 promotion completed learning 014 activation under historical/prior-tree R28/A28. Before allocating the new R29/A29 pair, V55 normalizes that completed lifecycle state from `PASS_ON_FINAL_REVIEW / ACTIVE_ON_PROMOTION` to durable `PASS / ACTIVE`. Its effectiveness remains `PENDING_MEASUREMENT`, has no receipt, and still requires a later qualifying `PRODLIKE_SUPERVISION_DEPLOYMENT_RECHECK`.

## Bridge-state invariant

V55 does not activate dev22 validation. Machine `active_run` is null. The last canonical validation head `cdb18e4b5a8f84ca0c89b9fe17a8a2d486234eaa` remains dev21 historical evidence only. `NEXT_WORK_ITEM.md` predeclares `RUN-P00-VALIDATION-002`, but run002 cannot become active until the validation lane closes dev21 run001 as superseded-before-native and publishes a dev22-bound run record.

This avoids either forbidden mismatch: main dev22 pointing at an active dev21 run, or validation run002 becoming canonical while main still accepts dev21. The transition state is deliberately short-lived but truthful.

## Operational boundary

The current prodlike runtime and stopped LAB were built for dev21. Their supervision/recovery infrastructure may remain healthy, but their product identity is not dev22 proof. Dev22 requires runtime/LAB rebuild/rebinding, a new candidate identity/object graph and V02 tooling migration before native execution.

Local key generation is deferred until the new local-authority validation schema/tooling is independently reviewed/audited. No private key is committed. No dev21 external-authenticity package is reused.

## Exact-tree rule

R29/A29 are the final verdict identities allocated to this exact semantic tree. Verdict artifacts may be appended after design freeze; any accepted-candidate, source-visibility, transition or assurance-boundary semantic edit reopens review/audit.
