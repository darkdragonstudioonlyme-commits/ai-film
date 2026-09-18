# DOCSYS-V2-R9 — V57 local-key parity/deployment reconciliation

DESIGN_ID: DOCSYS-R9-V57-LOCAL-KEY-PARITY-DEPLOYMENT-RECONCILIATION
TARGET_RELEASE: DOCSYS-V2-R9
TARGET_STATE_VERSION: 57
REVISION: R30_V57_LOCAL_KEY_PARITY_DEPLOYMENT_RECONCILIATION
BASE_MAIN_COMMIT: a893ae1d1cbe1dda6d8fb5119eeb0b36e3578b7d
VALIDATION_EVIDENCE_HEAD: c5f2d43aaa0d2e0ae796ea7981f578bcb2b0a148
DESIGN_BRANCH: lane/docs-v2-r9-v57-local-key-parity-deployment-design
REVIEW_BRANCH: lane/docs-v2-r9-v57-local-key-parity-deployment-review
AUDIT_BRANCH: lane/docs-v2-r9-v57-local-key-parity-deployment-audit
REQUIRED_REVIEW_ID: DOC-V2-R9-REVIEW-031
REQUIRED_AUDIT_ID: DOC-V2-R9-AUDIT-031
PRODUCT_SOURCE_CHANGED_BY_DOCSYS: false
VALIDATION_TOOLING_CHANGED_BY_DOCSYS: false
NATIVE_EXECUTION_ADVANCED: false

## Reconciliation

V56 accurately activated run002 but its trust/deployment summary became stale after a real parity finding. Canonical validation now ends at `c5f2d43aaa0d2e0ae796ea7981f578bcb2b0a148`. The old reviewed public identity `5d595732...` has no corresponding durable private key and is explicitly historical/superseded. Current authority is durable owner-only key `AI-FILM-P00-DEV22-LOCAL-001` / public SHA `7f14c158dd09ec9e40572131538bab6818e768cc9f33cb1ec3708a09df9a8a69`, trust SHA `0af4f9adadcd64bbc2b23a51d572d01af08bdf197c7d96150abdf1ffc9acbbe8`.

Current validation includes a machine verifier that derives raw public bytes from the actual private key and binds them to the public file, local metadata and ACTIVE trust anchor while enforcing owner/mode 0600. The corrected reactivation passed current-base design/review/audit plus canonical CI, and exact audited bytes were deployed to `validation-ops`. Independent deployment review/audit reverified 20/20 deployed hashes, key parity, preserved sensitive local identity context, watcher success, blocked real gates and stopped LAB. Canonical validation CI on `c5f2d43aaa0d2e0ae796ea7981f578bcb2b0a148` is `35320747377` SUCCESS.

## Remaining V02 boundary

Deployment PASS is not V02 closure. Prodlike runtime and the stopped LAB still contain dev21 product identity and must be rebuilt/resealed to exact dev22. Only then may a fresh candidate-specific local authority graph be constructed and signed with the durable current key. Current preflight/intake/pre-V03 remain blocked/missing; all 86 native cases remain NOT_RUN.

## Learning

`LEARNING-LOCAL-AUTHORITY-KEY-PARITY-015` captures the identity-parity defect. R31/A31 activate the reusable rule, but the incident that produced the learning is not post-activation effectiveness evidence. The measurement waits for the next qualifying local-authority key deployment/recovery recheck. Learning 014 remains separately pending on the next prodlike supervision deployment/recovery recheck; continuity remains 0/3.

## Exact-tree rule

Historical/prior-tree R30/A30 remain V56 authority. R31/A31 are the final verdict identities for this exact V57 semantic tree. Verdict artifacts may be appended after design freeze; any semantic edit to trust identity, deployment status, active run, learning state or native boundary reopens review/audit.
