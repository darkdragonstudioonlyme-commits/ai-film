# NEXT WORK ITEM — implement reviewed V02B/V03 binding producer tooling

~~~yaml
RUN_ID: RUN-P00-VALIDATION-002
WORKFLOW_ID: WF-P00-VALIDATION-ENTRY
MODE: IMPLEMENTATION
LANE: VALIDATION
STATUS: READY
PHASE: "00 — Host / WSL"
WORK_ITEM: IMPL-P00-V03-AUTHORITY-BINDING-PRODUCER-001
PRESERVED_CURSOR: RUN-P00-VALIDATION-002/V02B_LOCAL_AUTHORITY_PACKAGE
INPUT_IDENTITY:
  SOURCE_COMMIT: 86bb64938a136e3f8d6cfd0266685a01cb832b77
  VALIDATION_EVIDENCE_HEAD: 5e6d2f41bd1513ae6e488add304fba4d00498e9b
  TEST_CHANGE: lane/validation-p00:test-governance/TEST_CHANGE-P00-V03-AUTHORITY-BINDING-PRODUCER-005.md
  TEST_REVIEW: lane/validation-p00:test-governance/TEST_REVIEW-P00-V03-AUTHORITY-BINDING-PRODUCER-005.md
  RECIPE_CATALOG: lane/validation-p00:test-governance/P00_V03_AUTHORITY_BINDING_PRODUCER_RECIPE_CATALOG_V1.json
  RECIPE_CATALOG_SHA256: 5d321d4b6b8f8c47bbd257324a51af7d0bb564ec73d1e2532c2dba2b6645c2b5
  COVERAGE_EVIDENCE: lane/validation-p00:test-governance/design-evidence/TEST-DESIGN-P00-V03-AUTHORITY-BINDING-PRODUCER-005-COVERAGE.json
  COVERAGE_EVIDENCE_SHA256: 3aadec58f279005c4dbc29c11b55679f02d11593ad90d6fb6e4868f0749f4fc7
  ORACLE_CHANGED: false
  EXPECTED_BUSINESS_BEHAVIOR_CHANGED: false
  PRODUCT_SOURCE_CHANGE_AUTHORIZED: false
  NATIVE_EXECUTION_AUTHORIZED: false
  AUTHORITY_GRAPH_SIGNING_AUTHORIZED: false
GOAL: "Implement and test the independently reviewed validation-only producer contract without modifying accepted dev22 product source or performing authority signing/native execution."
REQUIRED_COMPONENTS:
  - V02B_AUTHORITY_GRAPH_COMPILER
  - STATIC_NATIVE_RESOLVABILITY_VERIFIER
  - V03_FIXTURE_PREPARATION_CONTROLLER
STEPS:
  - GAP_DISCOVERY_AND_TEST_REVIEW: COMPLETE
  - WORKFLOW_ROOT_CAUSE_REVIEW: COMPLETE_REVIEWED
  - TEST_DESIGN_AND_REVIEW: COMPLETE_REVIEWED
  - AUTHOR_VALIDATION_TOOLING: READY
  - INDEPENDENT_IMPLEMENTATION_REVIEW: NOT_STARTED
  - DEPLOY_REVIEWED_TOOLING: NOT_STARTED
  - RETURN_TO_V02B: BLOCKED
CURRENT_STEP: V02_LOCAL_OPERATOR_LAB_AUTHORITY
CURRENT_IMPLEMENTATION_STEP: AUTHOR_VALIDATION_TOOLING
SUCCESS_OUTPUT: "Exact validation-tooling candidate implementing all three reviewed components with no-execution/adversarial tests, exact catalog coverage, no oracle/product change and no signing/native side effects, ready for independent implementation review."
ON_SUCCESS: REVIEW-P00-V03-AUTHORITY-BINDING-PRODUCER-001
ON_FAIL: WORKFLOW_REVIEW
ON_BLOCK: BLOCK-P00-VAL-V03-BINDING-PRODUCER-001
RETURN_TO: RUN-P00-VALIDATION-002/V02B_LOCAL_AUTHORITY_PACKAGE
EXIT_CONDITION: "All three reviewed components and required negative self-tests exist in validation/test tooling, pass without native execution or private-key/signing access, leave accepted product source unchanged, and are frozen for independent implementation review."
~~~

Do not deploy the tooling to validation-ops, modify the canonical authority inbox, sign an authority graph, install native policy, start the LAB, or run native cases until the implementation candidate has passed its independent review.
