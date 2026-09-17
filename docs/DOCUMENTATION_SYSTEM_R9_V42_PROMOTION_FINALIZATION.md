# DOCSYS-V2-R9 — V42 promotion finalization

```yaml
DESIGN_ID: DOCSYS-R9-V42-PROMOTION-FINALIZATION
TARGET_RELEASE: DOCSYS-V2-R9
TARGET_STATE_VERSION: 42
REVISION: R13_V42_PROMOTION_FINALIZATION
BASE_MAIN_COMMIT: 60e030de9c234c4ec6cd242c335f94250d448188
DESIGN_BRANCH: lane/docs-v2-r9-v42-promotion-finalization-design
REVIEW_BRANCH: lane/docs-v2-r9-v42-promotion-finalization-review
AUDIT_BRANCH: lane/docs-v2-r9-v42-promotion-finalization-audit
REQUIRED_REVIEW_ID: DOC-V2-R9-REVIEW-014
REQUIRED_AUDIT_ID: DOC-V2-R9-AUDIT-014
PRODUCT_SOURCE_CHANGED: false
NATIVE_EXECUTION_ADVANCED: false
```

## Purpose

Correct a post-promotion semantic lag without rewriting the historical/prior-tree R13/A13 tree: canonical role-aware checks knew V42 was promoted, but state surfaces still said `CANDIDATE_REVIEW_REQUIRED`. The exact correction candidate must already encode its intended post-promotion state before prospective R14/A14 are issued.

## Required corrections

- set canonical promotion state to `ACTIVE_ON_PROMOTION` in Markdown and machine JSON before review;
- replace final verdict identities with prospective R14/A14 while labeling R13/A13 as historical prior-tree evidence;
- normalize learning 009 to durable `ACTIVE / PASS` using completed historical R13/A13 activation evidence before prospective R14/A14 final IDs replace the old pair;
- add learning 010 so this recurrence becomes a reusable pre-promotion invariant;
- preserve exact product/native/V02 state;
- use the post-activation authority reevaluation only as a measurement sample for learning 009 until a later receipt-bearing commit is independently reviewed.

## Exact-tree rule

No post-promotion semantic rewrite is allowed as part of the same R14/A14 promotion. The reviewed design itself must already describe the state intended on main. R14/A14 records may be the only later files added before exact fast-forward.
