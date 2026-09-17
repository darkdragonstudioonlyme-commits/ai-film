# DOCSYS-V2-R9 — V45 continuity measurement instrumentation

DESIGN_ID: DOCSYS-R9-V45-CONTINUITY-MEASUREMENT-INSTRUMENTATION
TARGET_RELEASE: DOCSYS-V2-R9
TARGET_STATE_VERSION: 45
REVISION: R18_V45_CONTINUITY_MEASUREMENT_INSTRUMENTATION
BASE_MAIN_COMMIT: 122f3d98bb0f069413c18899e37959e0a488cea6
DESIGN_BRANCH: lane/docs-v2-r9-v45-continuity-measurement-design
REVIEW_BRANCH: lane/docs-v2-r9-v45-continuity-measurement-review
AUDIT_BRANCH: lane/docs-v2-r9-v45-continuity-measurement-audit
REQUIRED_REVIEW_ID: DOC-V2-R9-REVIEW-019
REQUIRED_AUDIT_ID: DOC-V2-R9-AUDIT-019
PRODUCT_SOURCE_CHANGED: false
NATIVE_EXECUTION_ADVANCED: false

## Purpose

Make LEARNING-WORKFLOW-CONTINUITY-001 measurable without inventing interruption/resume events. Existing run-ledger continuity stays authoritative for current execution; the new event domain is immutable effectiveness evidence.

## Measurement contract

Canonical state declares event domain, event kind, qualifying count, required count and measurement status. The generic checker derives the actual count from receipts and compares it to state. Only PASS + measurement_eligible=true receipts count. FAIL receipts remain valid evidence but do not improve the metric.

Semantic event identity hashes all event semantics except event_id and the hash field itself, preventing one actual event from being double-counted under multiple receipt IDs. PASS events require same logical run, no duplicate logical runs and no repeated completed expensive step unless relevant identity changed.

At count 3, machine status becomes READY_FOR_EFFECTIVENESS_REVIEW, not EFFECTIVE. Learning lifecycle transition still requires an explicit metric-bound receipt and independent review/audit. Documentation Governance CI runs both the continuity measurement checker and its adversarial regression suite on every relevant branch/commit.

## Authoring review findings

Pre-review execution caught three defects and corrected them without weakening the metric: the initial checker treated a state-file Path as JSON; its semantic hash accidentally included event_id despite the anti-double-count contract; and FAIL receipts were incorrectly forced through PASS success predicates even though they must preserve failed behavior without counting it. The corrected checker parses the latest state JSON, excludes event_id plus the hash field from semantic identity, and applies success predicates only to measurement-eligible PASS events while retaining structural validation for FAIL evidence.

## Exact-tree invariant

R19/A19 are the final verdict identities for this exact semantic tree. The same semantic state is valid across DESIGN, REVIEW, AUDIT and PROMOTED roles; only verdict-record presence changes.

## Non-goals

No prior event is backfilled without evidence. No product/source/package, code-review verdict, validation tooling, external key/approval/trust state, native execution, qualification, SITE or HOST_READY state changes.
