# NEXT WORK ITEM — implement dev23 stage-derived LAB authority

~~~yaml
RUN_ID: RUN-P00-VALIDATION-002
WORKFLOW_ID: WF-P00-VALIDATION-ENTRY
MODE: IMPLEMENTATION
LANE: IMPLEMENT
STATUS: READY
PHASE: "00 — Host / WSL"
WORK_ITEM: IMPL-P00-V03-STAGE-DERIVED-AUTHORITY-DEV23
TARGET_VERSION: 0.1.0.dev23
PARENT_SOURCE_COMMIT: 86bb64938a136e3f8d6cfd0266685a01cb832b77
PRESERVED_CURSOR: RUN-P00-VALIDATION-002/V02B_LOCAL_AUTHORITY_PACKAGE
INPUT_IDENTITY:
  VALIDATION_EVIDENCE_HEAD: 1defbf3422903a694215df9e2c11374fc5b1b785
  DESIGN_RECORD: lane/validation-p00:docs/PHASE00_STAGE_DERIVED_LAB_AUTHORITY_CHANGE.md
  DESIGN_REVIEW: lane/validation-p00:reviews/DESIGN-REVIEW-P00-V03-STAGE-DERIVED-AUTHORITY-001.md
  TEST_CHANGE: lane/validation-p00:test-governance/TEST_CHANGE-P00-V03-AUTHORITY-BINDING-PRODUCER-006.md
  TEST_REVIEW: lane/validation-p00:test-governance/TEST_REVIEW-P00-V03-AUTHORITY-BINDING-PRODUCER-006.md
  COVERAGE: lane/validation-p00:test-governance/design-evidence/TEST-DESIGN-P00-V03-STAGE-DERIVED-AUTHORITY-006-COVERAGE.json
  ORACLE_CHANGED: false
AUTHORIZED_PRODUCT_DELTA:
  ADD:
    - src/aifilm_p00/native/stage_authority.py
  MODIFY:
    - src/aifilm_p00/native/harness_controller.py
  TEST_ADD:
    - tests/test_dev23_stage_authority.py
  TEST_MODIFY:
    - tests/test_dev15_harness.py
  BYTE_IDENTICAL_REQUIRED:
    - src/aifilm_p00/authority.py
    - src/aifilm_p00/plans.py
    - src/aifilm_p00/native/harness_cases.py
    - src/aifilm_p00/native/request_entry.py
    - src/aifilm_p00/resume.py
    - src/aifilm_p00/recovery.py
    - config/required-native-test-inventory.json
    - contracts/PHASE00_INFRA_DESIGN_V2.md
    - contracts/PHASE00_ACCEPTANCE_MATRIX_V2.md
    - contracts/PHASE00_FAILURE_RECOVERY_PLAN_V2.md
    - contracts/PHASE00_EVIDENCE_AND_RESEARCH_REGISTER_V2.md
GOAL: "Implement the reviewed four-mode temporal LAB authority model without changing Phase00 business/test oracles or public dynamic-plan authority."
REQUIRED_IMPLEMENTATION:
  - SIGNED_STAGE_DERIVATION_SLOT_RESOLVER
  - CONTENT_ADDRESSED_STAGE_STATE_HANDOFF
  - MULTI_PRODUCER_LINEAGE
  - DERIVED_NATIVE_BINDING_AND_PLAN
  - ENTRY_PROBE_AUTHORITY_RESOLUTION
  - FENCE_BOUND_RECONCILIATION_RESOLUTION
  - MONOTONIC_SIGNED_BASE_REF_PARTITION_CHECK
  - HARNESS_EXECUTE_AND_FINALIZER_LINEAGE
  - TD006_01_THROUGH_TD006_16
STEPS:
  - DESIGN_AND_TEST_REVIEW: COMPLETE_REVIEWED
  - AUTHOR_DEV23_PRODUCT: READY
  - AUTHOR_REGRESSION_AND_STATIC: NOT_STARTED
  - PACKAGE_EXACT_SOURCE: NOT_STARTED
  - FORMAL_CODE_REVIEW: NOT_STARTED
  - VALIDATION_TOOLING_IMPLEMENTATION: BLOCKED_UNTIL_CANDIDATE_IDENTITY
  - CANDIDATE_VALIDATION_RECONCILIATION: BLOCKED
  - RETURN_TO_V02B: BLOCKED
CURRENT_STEP: V02_LOCAL_OPERATOR_LAB_AUTHORITY
CURRENT_IMPLEMENTATION_STEP: AUTHOR_DEV23_STAGE_DERIVED_AUTHORITY
SUCCESS_OUTPUT: "Exact dev23-or-later source candidate within the reviewed file allowlist, with TD006 coverage and full author regression/static/package evidence, ready for independent formal CODE_REVIEW."
ON_SUCCESS: CODE_REVIEW-P00-001_DEV23_STAGE_DERIVED_AUTHORITY
ON_FAIL: WORKFLOW_REVIEW
ON_BLOCK: BLOCK-P00-VAL-V03-STAGE-DERIVED-IMPLEMENTATION-006
EXIT_CONDITION: "Dev23 candidate changes only the authorized product/test files, passes the full author regression/static/package checks with TD006 coverage, and is frozen for independent formal CODE_REVIEW."
~~~

Do not modify validation-ops, sign V02 authority, install native policy, start the LAB or run native cases during product authoring.
