# NEXT WORK ITEM — design tests for dev23 prodlike verify-runtime release contract

~~~yaml
RUN_ID: RUN-P00-VALIDATION-002
WORKFLOW_ID: WF-P00-VALIDATION-ENTRY
MODE: TEST_DESIGN
LANE: TEST_DESIGN
STATUS: READY
WORK_ITEM: TEST-DESIGN-P00-DEV23-PRODLIKE-VERIFY-RUNTIME-013
ASSIGNEE: CHATGPT
AUTHOR_ACTOR: CHATGPT
PRESERVED_CURSOR: RUN-P00-VALIDATION-002/V02B_LOCAL_AUTHORITY_PACKAGE
INPUT_IDENTITY:
  CURRENT_MAIN: 1fe0096a13822f95bd90eb7df571afb1d8f4cab6
  CURRENT_VALIDATION: 35605267fea7cac1fa332a3fd7c90da5dd0726f8
  FORMAL_RECEIPT_REVIEW: lane/validation-p00:reviews/CODE-REVIEW-P00-DEV23-PRODLIKE-ATTEMPT4-RECONCILIATION-RECEIPT-002.md
  TRANSACTION_RECEIPT_SHA256: d225adbd11221cb593a5f1b285b3d27c788f4e14ad4d840fcc5f7778b3b55d05
  INDEPENDENT_DEV22_VERIFY_SHA256: 1d67c6197e13c3af5e69a906cc6c70f0c17f78e034bcd0f3efd7e9a5fb383021
  DEV23_CANDIDATE_COMMIT: 2f7da39984a7a582c7cf2a84f743299fc7fe735f
  SOURCE_DEBT: DEV23_RELEASE_MISSING_BIN_VERIFY_RUNTIME
  CURRENT_PRODLIKE: EXACT_DEV22
  BROKEN_STAGED_DEV23: PRESERVED_EVIDENCE_NOT_DEPLOYED
  ORACLE_CHANGED: false
GOAL: "Define TEST_CHANGE 013 so every candidate-generic prodlike release that is eligible for deployment contains the exact reviewed verify-runtime executable at bin/verify-runtime, binds it into release identity, and fails tests before deployment if missing/drifted/non-executable. Preserve existing business/native oracles."
STEPS:
  - RECONCILIATION2_RECEIPT_REVIEW: COMPLETE_PASS
  - ROOT_CAUSE: COMPLETE_MISSING_RELEASE_VERIFY_RUNTIME
  - TEST_CHANGE_013_AUTHOR: READY
  - TEST_REVIEW_013: BLOCKED
  - RELEASE_BUILDER_IMPLEMENTATION: BLOCKED
  - NEW_DEPLOYMENT_AUTHORIZATION: BLOCKED
  - LAB_REBUILD_RESEED: BLOCKED
  - AUTHORITY_SIGNING: BLOCKED
  - NATIVE_VALIDATION: NOT_STARTED
CURRENT_STEP: V02_LOCAL_OPERATOR_LAB_AUTHORITY
SUCCESS_OUTPUT: "TEST_CHANGE 013 plus coverage mapping for release verify-runtime presence/hash/mode/composition and regression retention; no implementation proof."
ON_SUCCESS: TEST-REVIEW-P00-DEV23-PRODLIKE-VERIFY-RUNTIME-013
ON_FAIL: TEST_DESIGN_CORRECTION_013
ON_BLOCK: BLOCK-P00-VAL-V03-DEV23-PRODLIKE-VERIFY-RUNTIME-013
RETURN_TO: RUN-P00-VALIDATION-002/V02B_LOCAL_AUTHORITY_PACKAGE
EXIT_CONDITION: "Independent TEST_REVIEW confirms exact affected source/test allowlist, verify-runtime release semantics, negative missing/hash/mode/composition cases, predecessor TV010/TV011/TV012 retention, ORACLE_CHANGED=false and no deployment/native/signing authority."
~~~

Test design only. Do not patch release tooling before TEST_REVIEW, create new deployment authorization, modify or delete staged dev23 evidence, rebuild LAB, sign authority, write HKLM, run native cases, issue qualification or mark HOST_READY.
