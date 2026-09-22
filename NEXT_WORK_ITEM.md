# NEXT WORK ITEM — implement and qualify the foreground text-review bridge

~~~yaml
RUN_ID: RUN-P00-VALIDATION-002
WORKFLOW_ID: WF-P00-VALIDATION-ENTRY
MODE: IMPLEMENTATION
LANE: IMPLEMENT
STATUS: READY
WORK_ITEM: IMPL-DUAL-AI-TEXT-BRIDGE-001
ASSIGNEE: CHATGPT
AUTHOR_ACTOR: CHATGPT
PRESERVED_CURSOR: RUN-P00-VALIDATION-002/V02B_LOCAL_AUTHORITY_PACKAGE
INPUT_IDENTITY:
  SOURCE_COMMIT: 86bb64938a136e3f8d6cfd0266685a01cb832b77
  DESIGN: docs/DUAL_AI_AUTOMATIC_HANDOFF.md
  REQUIRED_POLICY_VERDICTS: R38_REVIEW_AND_AUDIT_AT_EXACT_TARGET
GOAL: "Implement a single-task foreground tool-less bridge, review its exact code with Claude, and qualify context, permission, duplicate and timeout handling without enabling implementation/native permissions."
STEPS:
  - POLICY_ACCEPTANCE: VERIFY_CANONICAL_R38_RECORDS_BEFORE_AUTHORING
  - TEXT_BRIDGE_AUTHOR_REVIEW_TEST: READY_AFTER_POLICY_ACCEPTANCE
  - TEXT_PROFILE_QUALIFICATION: NOT_STARTED
  - PRODUCT_FEASIBILITY_REVIEW: PRESERVED_FOLLOW_ON
CURRENT_STEP: V02_LOCAL_OPERATOR_LAB_AUTHORITY
SUCCESS_OUTPUT: "Reviewed exact bridge plus real text-profile qualification receipt; shared learning effectiveness remains separately measured."
ON_SUCCESS: TEXT_PROFILE_QUALIFICATION_THEN_PRODUCT_FEASIBILITY_REVIEW
ON_FAIL: SAME_CAUSAL_FAMILY_AUTHOR_CORRECTION
ON_BLOCK: BLOCK-DUAL-AI-TEXT-BRIDGE-QUALIFICATION
RETURN_TO: RUN-P00-VALIDATION-002/V02B_LOCAL_AUTHORITY_PACKAGE
EXIT_CONDITION: "Exact code is non-author reviewed, guards are exercised in integration, no duplicate worker/replay occurs, real constrained invocation succeeds, and setup/usage scope is verified."
~~~

This is the intended post-promotion cursor. While this candidate is under review,
its current author/reviewer work is owned by the explicit excursion receipt, not by
executing this future step. Installation/login are already evidenced; do not repeat.
No WSL_IMPLEMENT, product source patch, V02 signing, native policy or LAB action is
included. Product feasibility and affected test review still precede dev23.

## DESIGN_REVIEW_FEASIBILITY_CORRECTION
Preserved product follow-on: `docs/PHASE00_STAGE_AUTHORITY_FEASIBILITY_CORRECTION_V2.md`.
