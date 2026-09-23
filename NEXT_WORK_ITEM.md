# NEXT WORK ITEM — prepare new reviewed prodlike authorization 002

~~~yaml
RUN_ID: RUN-P00-VALIDATION-002
WORKFLOW_ID: WF-P00-VALIDATION-ENTRY
MODE: IMPLEMENTATION
LANE: IMPLEMENT
STATUS: READY
WORK_ITEM: PREPARE-P00-DEV23-PRODLIKE-AUTHORIZATION-002
ASSIGNEE: CHATGPT
AUTHOR_ACTOR: CHATGPT
PRESERVED_CURSOR: RUN-P00-VALIDATION-002/V02B_LOCAL_AUTHORITY_PACKAGE
INPUT_IDENTITY:
  VALIDATION_REVIEW_HEAD: 97b248548a1291adc243f5ec95f6028c7ade6bd7
  CORRECTED_EXECUTOR_COMMIT: b94eb5b115385a6b0634b2ff424f26c34407f9ad
  CORRECTED_EXECUTOR_TREE: 0f56ea32d26a73dbe7d3a6982bcd8fc4ba109b62
  CORRECTION_REVIEW: lane/validation-p00:reviews/CODE-REVIEW-P00-DEV23-PRODLIKE-USER-BUS-012.md
  ATTEMPT1_RECEIPT_SHA256: fcb3b059634e41cf08dc61ec39c80d5dc93250e735ab2d795afbd67583ddabfd
  ATTEMPT1_REPLAY_AUTHORIZED: false
GOAL: "Prepare one new immutable PRODLIKE_DEPLOYMENT_V2 authorization with new transaction id/hash/expiry/receipt root, revalidate current dev22 and exact staged dev23, and prove preparation is non-mutating."
STEPS:
  - USER_BUS_CORRECTION_REVIEW_PROMOTION: COMPLETE_PASS
  - ATTEMPT1_REPLAY: PERMANENTLY_FORBIDDEN
  - PREP_BASELINE_REVALIDATION: READY
  - PLAN_ONLY_CORRECTED_EXECUTOR: NOT_STARTED
  - AUTHORIZATION2_AUTHOR: NOT_STARTED
  - NON_MUTATION_PROOF: NOT_STARTED
  - AUTHORIZATION2_CROSS_MODEL_REVIEW: BLOCKED
  - PRODLIKE_ATTEMPT2: BLOCKED
  - LAB_REBUILD_RESEED: BLOCKED
  - AUTHORITY_SIGNING: BLOCKED
  - NATIVE_VALIDATION: NOT_STARTED
CURRENT_STEP: V02_LOCAL_OPERATOR_LAB_AUTHORITY
SUCCESS_OUTPUT: "Fresh authorization-002 hash plus plan/non-mutation evidence, bound to corrected executor and separate receipt root; no execution proof."
ON_SUCCESS: CODE-REVIEW-P00-DEV23-PRODLIKE-DEPLOYMENT-AUTHORIZATION-002
ON_FAIL: CORRECT_OR_REVOKE_AUTHORIZATION2_BEFORE_REVIEW
ON_BLOCK: BLOCK-P00-VAL-V03-DEV23-PRODLIKE-AUTHORIZATION2-PREP-034
RETURN_TO: RUN-P00-VALIDATION-002/V02B_LOCAL_AUTHORITY_PACKAGE
EXIT_CONDITION: "New transaction id and authorization hash are distinct from attempt1; receipt root is separate; current remains exact dev22; staged dev23 is exact or drift blocks; corrected executor/validation/input hashes match; expiry is bounded; forbidden authority bits false; preparation snapshot unchanged."
~~~

Preparation only. Do not replay attempt 1, delete staged dev23, execute attempt 2, mutate user-systemd/control/current, rebuild LAB, sign authority, write HKLM, run native cases, issue qualification or mark HOST_READY.
