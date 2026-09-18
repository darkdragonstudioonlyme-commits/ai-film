# DOCSYS-V2-R9 — V51 forensic meta-review pointer parity

DESIGN_ID: DOCSYS-R9-V51-FORENSIC-META-REVIEW-PARITY
TARGET_RELEASE: DOCSYS-V2-R9
TARGET_STATE_VERSION: 51
REVISION: R24_V51_FORENSIC_META_REVIEW_PARITY
BASE_MAIN_COMMIT: 4bf36ff8c2643e1b09c1248793b549c2495a190e
DESIGN_BRANCH: lane/docs-v2-r9-v51-forensic-meta-review-parity-design
REVIEW_BRANCH: lane/docs-v2-r9-v51-forensic-meta-review-parity-review
AUDIT_BRANCH: lane/docs-v2-r9-v51-forensic-meta-review-parity-audit
REQUIRED_REVIEW_ID: DOC-V2-R9-REVIEW-025
REQUIRED_AUDIT_ID: DOC-V2-R9-AUDIT-025
PRODUCT_SOURCE_CHANGED: false
NATIVE_EXECUTION_ADVANCED: false

## Finding

Canonical V50 contains a machine/Markdown evidence-pointer drift. `AI_FILM_PROJECT_STATE_V50.json:learning_activation.recent_ci_meta_review` points to V50 health evidence, while `PROJECT_STATE.md:RECENT_CI_META_REVIEW` still points to V49. V49 had these values aligned, so the divergence was introduced by V50 state authoring rather than by different field ownership.

## Negative-first proof

Test-only commit `c06b4979a90e5a68a24bcbffa41d2d8fe76051bc` added `recent_ci_meta_review_parity_drift` without changing the checker. Documentation Governance run `35303029689` / job `105469462142` passed baseline lifecycle/governance/docs checks and failed exactly at Adversarial active docs regression. This proves the checker lacked the parity invariant.

## Correction

V51 reconciles both canonical representations to `workflow-health/HEALTH_REVIEW-DOCSYS-R9-V51-FORENSIC-META-PARITY-028.md`. `tools/check_project_docs.py` now requires machine/Markdown equality and verifies that the evidence target exists. The adversarial active-doc suite expands from 13 to 14 cases.

## Scope

No product source/package identity, validation head, V02 predicate, LAB/SITE/native procedure, qualification, HOST_READY, learning lifecycle outcome or continuity event count changes. No new learning record is required; this implements the existing machine-state/current-document consistency principle and persists compact memory provenance.

## Exact-tree rule

R25/A25 are the final verdict identities for one semantic tree. Review/audit may add verdict artifacts only; any semantic state/checker/test change afterward reopens review/audit.
