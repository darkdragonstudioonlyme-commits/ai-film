# NEXT WORK ITEM — implement dev23 stage-derived LAB authority

~~~yaml
RUN_ID: RUN-P00-VALIDATION-002
WORKFLOW_ID: WF-P00-VALIDATION-ENTRY
MODE: IMPLEMENTATION
LANE: IMPLEMENT
STATUS: READY
WORK_ITEM: IMPL-P00-V03-STAGE-DERIVED-AUTHORITY-DEV23
ASSIGNEE: CHATGPT
AUTHOR_ACTOR: CHATGPT
TARGET_VERSION: 0.1.0.dev23
PARENT_SOURCE_COMMIT: 86bb64938a136e3f8d6cfd0266685a01cb832b77
PRESERVED_CURSOR: RUN-P00-VALIDATION-002/V02B_LOCAL_AUTHORITY_PACKAGE
INPUT_IDENTITY:
  VALIDATION_EVIDENCE_HEAD: 1defbf3422903a694215df9e2c11374fc5b1b785
  DESIGN_RECORD: docs/PHASE00_STAGE_AUTHORITY_FEASIBILITY_CORRECTION_V2.md
  DESIGN_AUTHOR_COMMIT: c16745e994396f2c05e4408dbb909d0c94389e82
  DESIGN_REVIEW: reviews/DESIGN-REVIEW-P00-V03-AUTHORITY-FEASIBILITY-003.md
  TEST_CHANGE: test-governance/TEST_CHANGE-P00-V03-AUTHORITY-CONSTRUCTIBILITY-007.md
  TEST_REVIEW: test-governance/TEST_REVIEW-P00-V03-AUTHORITY-CONSTRUCTIBILITY-007.md
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
GOAL: "Implement the reviewed four-mode temporal authority model plus V3 acyclic publication/recovery/proof-scope contract without changing Phase00 business/test oracles or public dynamic-plan authority."
REQUIRED_IMPLEMENTATION:
  - TD006_01_THROUGH_TD006_16
  - TD007_01_THROUGH_TD007_12
  - DETACHED_BASE_MANIFEST
  - SIGNED_STAGE_DERIVATION_SLOT_RESOLVER
  - DESTINATION_LOCATOR_AND_COPY_BINDING
  - NINE_LATE_PROOF_SCOPE_VALIDATORS
  - SERIALIZED_POLICY_PUBLICATION_P0_THROUGH_P8
  - IDEMPOTENT_PUBLICATION_RECOVERY_MATRIX
  - MONOTONIC_GENERATION_AND_ATOMIC_DERIVED_REVOCATION
  - HARNESS_LINEAGE_AND_FINALIZER_BINDING
STEPS:
  - DESIGN_REVIEW_V3: COMPLETE_PASS
  - TEST_REVIEW_007: COMPLETE_PASS
  - AUTHOR_DEV23_PRODUCT: READY
  - AUTHOR_REGRESSION_STATIC_PACKAGE: NOT_STARTED
  - FORMAL_CODE_REVIEW: NOT_STARTED
  - CANDIDATE_VALIDATION_RECONCILIATION: BLOCKED
  - RETURN_TO_V02B: BLOCKED
CURRENT_STEP: V02_LOCAL_OPERATOR_LAB_AUTHORITY
SUCCESS_OUTPUT: "Exact dev23 source candidate within the reviewed file allowlist, TD006+TD007 and full author regression/static/package evidence, ready for non-author CODE_REVIEW."
ON_SUCCESS: CODE-REVIEW-P00-001_DEV23_STAGE_DERIVED_AUTHORITY
ON_FAIL: SAME_CAUSAL_FAMILY_IMPLEMENTATION_CORRECTION_OR_DESIGN_GAP
ON_BLOCK: BLOCK-P00-VAL-V03-STAGE-DERIVED-IMPLEMENTATION-008
RETURN_TO: RUN-P00-VALIDATION-002/V02B_LOCAL_AUTHORITY_PACKAGE
EXIT_CONDITION: "Dev23 changes only the authorized product/test files, passes TD006+TD007 and full author regression/static/package checks, preserves all byte-identical files and is frozen for CODE_REVIEW."
~~~

ChatGPT is the author for this candidate because Claude WSL_IMPLEMENT is not activated; actual authorship overrides the default responsibility matrix. Claude remains the required non-author CODE_REVIEW consumer through bounded TEXT_REVIEW. Do not sign authority, install native policy, start LAB or run native cases during authoring.
