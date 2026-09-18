# DOCSYS-V2-R9 — V50 promoted stage-language hardening

DESIGN_ID: DOCSYS-R9-V50-PROMOTED-STAGE-LANGUAGE-HARDENING
TARGET_RELEASE: DOCSYS-V2-R9
TARGET_STATE_VERSION: 50
REVISION: R23_V50_PROMOTED_STAGE_LANGUAGE_HARDENING
BASE_MAIN_COMMIT: 24720ac65c35c163d17c36240a3096a03c47f49c
DESIGN_BRANCH: lane/docs-v2-r9-v50-promoted-stage-language-design
REVIEW_BRANCH: lane/docs-v2-r9-v50-promoted-stage-language-review
AUDIT_BRANCH: lane/docs-v2-r9-v50-promoted-stage-language-audit
REQUIRED_REVIEW_ID: DOC-V2-R9-REVIEW-024
REQUIRED_AUDIT_ID: DOC-V2-R9-AUDIT-024
PRODUCT_SOURCE_CHANGED: false
NATIVE_EXECUTION_ADVANCED: false

## Finding

V49 promoted successfully, but its historical/prior-tree R23/A23 authority prose still described learning 013 as an EFFECTIVE candidate subject to that same verdict pair's semantic review even though the pair was already complete. `tools/check_project_docs.py` allowed this because its current-pair stage vocabulary recognized prospective/pending/awaiting/requires wording but not equivalent `subject to` / conditional review gating.

A new adversarial case was added first and failed against the unchanged checker, proving the gap independently of the correction. The detector is then generalized at the verdict-pair clause level: under PROMOTED/GENERIC roles, current-pair review/audit gating expressed through `subject to` or `conditional/conditioned on` is stage drift. DESIGN remains allowed to contain prospective current-pair wording.

## Pre-review server negative evidence

Initial atomic remote design `a106bb37f1e91eba7fe2da6777a77105affd3cac` produced Documentation Governance run `35302630870`. Baseline active-document checking passed, but the new adversarial stage-language case failed because transport reconstruction had written Python raw regex boundaries as double-escaped literals (`r'\\\\b...'`) instead of word-boundary escapes. The correction changes only those regex escapes to the already locally tested single-boundary form; the stage predicate, role contract and test expectations are unchanged. The failed run is retained as authoring evidence.

## Scope

This is documentation-governance detector/test/state hardening only. It does not change accepted product source/package identity, validation head, V02 predicates, LAB/SITE/native procedures, qualification, HOST_READY, learning effectiveness outcomes or continuity event count.

## Lifecycle disposition

No new learning is created. The reusable rule already exists in historical learning 011; this incident is an implementation/test-coverage recurrence of that rule, while learning 012 remains correctly EFFECTIVE for its narrower pair-local historical-context metric. Provenance is retained in `workflow-health/HEALTH_REVIEW-DOCSYS-R9-V50-PROMOTED-STAGE-LANGUAGE-027.md` and compact memory.

## Exact-tree rule

R24/A24 are the final verdict identities for one semantic tree. Review/audit may add verdict artifacts only; any checker/test/state semantic change afterward reopens review/audit.
