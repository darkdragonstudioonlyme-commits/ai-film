# DOCSYS-V2-R9 — V42 promoted semantic guard

```yaml
DESIGN_ID: DOCSYS-R9-V42-PROMOTED-SEMANTIC-GUARD
TARGET_RELEASE: DOCSYS-V2-R9
TARGET_STATE_VERSION: 42
REVISION: R14_V42_PROMOTED_SEMANTIC_GUARD
BASE_MAIN_COMMIT: 176aa7452e1c14c67b0768dd75181331f561d95e
DESIGN_BRANCH: lane/docs-v2-r9-v42-promoted-semantic-guard-design
REVIEW_BRANCH: lane/docs-v2-r9-v42-promoted-semantic-guard-review
AUDIT_BRANCH: lane/docs-v2-r9-v42-promoted-semantic-guard-audit
REQUIRED_REVIEW_ID: DOC-V2-R9-REVIEW-015
REQUIRED_AUDIT_ID: DOC-V2-R9-AUDIT-015
PRODUCT_SOURCE_CHANGED: false
NATIVE_EXECUTION_ADVANCED: false
```

## Finding

Historical/prior-tree R14/A14 successfully promoted V42, but a post-promotion reread found same-ordinal stage drift: current authority prose still called current R14/A14 prospective and described the current tree as a candidate awaiting replacement. Machine promotion state and lifecycle resolution were correct, so ordinal-only authority checks did not detect the contradiction.

## Correction

The active-doc checker becomes role-aware for promoted semantic surfaces. On PROMOTED/GENERIC trees it rejects candidate/pending promotion state and rejects prospective/pending/awaiting language applied to the current verdict pair. Explicitly historical prior pairs remain readable. DESIGN/REVIEW/AUDIT role semantics remain legal.

Learning 010 becomes INEFFECTIVE because its pre-encoding rule did not cover current-authority prose. Successor learning 011 generalizes the requirement to all promoted semantic surfaces.

## Exact-tree rule

R15/A15 are the final verdict IDs for this revision. The same exact design prose must be valid before and after promotion; only the R15/A15 verdict records may be added before exact fast-forward. Product/native/V02 authority remains unchanged.
