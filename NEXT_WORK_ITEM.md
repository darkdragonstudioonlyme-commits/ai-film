# NEXT WORK ITEM — implement reviewed dev23 prodlike/LAB transaction executors

~~~yaml
RUN_ID: RUN-P00-VALIDATION-002
WORKFLOW_ID: WF-P00-VALIDATION-ENTRY
MODE: IMPLEMENTATION
LANE: IMPLEMENT
STATUS: READY
WORK_ITEM: IMPL-P00-DEV23-PRODLIKE-LAB-DEPLOYMENT-011
ASSIGNEE: CHATGPT
AUTHOR_ACTOR: CHATGPT
PRESERVED_CURSOR: RUN-P00-VALIDATION-002/V02B_LOCAL_AUTHORITY_PACKAGE
INPUT_IDENTITY:
  VALIDATION_HEAD: 2e813e04acc948158c170f111f5a3933b8a49435
  TEST_CHANGE_011: lane/validation-p00:test-governance/TEST_CHANGE-P00-DEV23-PRODLIKE-LAB-DEPLOYMENT-011.md
  TEST_REVIEW_011: lane/validation-p00:test-governance/TEST_REVIEW-P00-DEV23-PRODLIKE-LAB-DEPLOYMENT-011.md
  CANDIDATE_ID: acf18da3-4969-451c-8a4b-a7e46ad89c98
  CANDIDATE_BINDING_SHA256: ed7823332afa96c3335f3353518ca0330b9e3c687b0022926c776319611c1890
FILES_ALLOWED_ADD:
  - validation/tooling/deployment_transaction_common.py
  - validation/tooling/deploy_prodlike_candidate-v2.py
  - validation/tooling/rebuild_lab_candidate-v2.py
  - validation/tooling/tests/test_prodlike_deployment_transaction_v2.py
  - validation/tooling/tests/test_lab_rebuild_transaction_v2.py
GOAL: "Implement fail-closed, review-gated transaction executors with injected command runners and full fault-injection tests; do not execute real prodlike/LAB mutation."
STEPS:
  - COMMON_TRANSACTION_HARDCUTS: READY
  - PRODLIKE_EXECUTOR: READY
  - LAB_EXECUTOR: READY
  - TV011_FAULT_INJECTION_TESTS: READY
  - HISTORICAL_AND_PRIOR_REGRESSION: REQUIRED
  - CLAUDE_CODE_REVIEW: BLOCKED
  - REAL_PRODLIKE_DEPLOYMENT: BLOCKED
  - REAL_LAB_REBUILD_RESEED: BLOCKED
  - AUTHORITY_SIGNING: BLOCKED
  - NATIVE_VALIDATION: NOT_STARTED
CURRENT_STEP: V02_LOCAL_OPERATOR_LAB_AUTHORITY
SUCCESS_OUTPUT: "Frozen exact five-file candidate plus host test evidence for TV011-01..21; no real deployment/native proof."
ON_SUCCESS: CODE-REVIEW-P00-DEV23-PRODLIKE-LAB-DEPLOYMENT-011
ON_FAIL: SAME_IMPLEMENTATION_CAUSAL_FAMILY_OR_TEST_DESIGN_GAP
ON_BLOCK: BLOCK-P00-VAL-V03-DEV23-PRODLIKE-LAB-DEPLOYMENT-IMPLEMENTATION-024
RETURN_TO: RUN-P00-VALIDATION-002/V02B_LOCAL_AUTHORITY_PACKAGE
EXIT_CONDITION: "Only five ADD files changed; TV011-01..21 tests pass including fault injection/unknown completion; prior 18+34+11 regressions remain green; no real mutation occurred."
~~~

Use fake/injected command runners for author tests. Do not switch prodlike current, invoke live systemctl, export/import/unregister/start LAB, sign authority, write HKLM, run native cases, issue qualification or mark HOST_READY.
