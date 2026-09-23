# NEXT WORK ITEM — implement dev23 prodlike/LAB reconciliation successor

~~~yaml
RUN_ID: RUN-P00-VALIDATION-002
WORKFLOW_ID: WF-P00-VALIDATION-ENTRY
MODE: IMPLEMENTATION
LANE: IMPLEMENT
STATUS: READY
WORK_ITEM: IMPL-P00-DEV23-PRODLIKE-LAB-RECONCILIATION-010
ASSIGNEE: CHATGPT
AUTHOR_ACTOR: CHATGPT
PRESERVED_CURSOR: RUN-P00-VALIDATION-002/V02B_LOCAL_AUTHORITY_PACKAGE
INPUT_IDENTITY:
  VALIDATION_HEAD: 112cee0506c250ea34bd5487baf3281f98dfb189
  TEST_REVIEW_010: test-governance/TEST_REVIEW-P00-DEV23-PRODLIKE-LAB-RECONCILIATION-010.md
  PRODUCT_SOURCE_COMMIT: 2f7da39984a7a582c7cf2a84f743299fc7fe735f
  CANDIDATE_BINDING_SHA256: ed7823332afa96c3335f3353518ca0330b9e3c687b0022926c776319611c1890
AUTHORIZED_ADD:
  - validation/tooling/build_prodlike_release-v2.py
  - validation/tooling/build_prodlike_rebuild_set-v2.py
  - validation/tooling/build_prodlike_control_bundle-v2.py
  - validation/tooling/verify_prodlike_control_bundle-v2.py
  - validation/tooling/verify_prodlike_user_systemd-v2.py
  - validation/tooling/prodlike_control_templates_v2.json
  - validation/tooling/plan_lab_candidate_rebuild-v2.py
  - validation/tooling/verify_lab_candidate_rebuild_receipt-v2.py
  - validation/tooling/tests/test_prodlike_release_v2.py
  - validation/tooling/tests/test_prodlike_control_bundle_v2.py
  - validation/tooling/tests/test_prodlike_user_systemd_v2.py
  - validation/tooling/tests/test_lab_candidate_rebuild_v2.py
REUSE_BYTE_IDENTICAL:
  - validation/tooling/v02_candidate_profile.py
  - validation/tooling/build_lab_payload-v2.py
  - validation/tooling/verify-lab-artifact-seal-v2.py
  - validation/tooling/dev23-candidate-binding.json
GOAL: "Implement and author-test exact candidate-generic prodlike/LAB reconciliation tooling without deployment or native side effects."
STEPS:
  - TEST_REVIEW_010: COMPLETE_PASS
  - AUTHOR_SUCCESSOR_TOOLING: READY
  - AUTHOR_TV010_REGRESSION: NOT_STARTED
  - HISTORICAL_DEV22_REGRESSION: NOT_STARTED
  - CLAUDE_CODE_REVIEW: BLOCKED
  - PRODLIKE_DEPLOYMENT: BLOCKED
  - LAB_REBUILD_RESEED: BLOCKED
  - AUTHORITY_SIGNING: BLOCKED
  - NATIVE_VALIDATION: NOT_STARTED
CURRENT_STEP: V02_LOCAL_OPERATOR_LAB_AUTHORITY
SUCCESS_OUTPUT: "Frozen 12-file ADD-only successor candidate plus author tests/evidence; no deployment/native proof."
ON_SUCCESS: CODE-REVIEW-P00-DEV23-PRODLIKE-LAB-RECONCILIATION-010
ON_FAIL: SAME_RECONCILIATION_IMPLEMENTATION_CAUSAL_FAMILY
ON_BLOCK: BLOCK-P00-VAL-V03-DEV23-PRODLIKE-LAB-IMPLEMENTATION-020
RETURN_TO: RUN-P00-VALIDATION-002/V02B_LOCAL_AUTHORITY_PACKAGE
EXIT_CONDITION: "TV010-01..14 author tests pass; historical dev22 and reusable 009 bytes are unchanged; candidate contains exactly authorized ADD files; no deployment/LAB/native/signing side effects occur."
~~~

Do not switch prodlike current runtime, modify live user-systemd, mutate/export/import/start LAB, replace LAB facts/seal, sign authority, touch HKLM/canonical inbox, run native cases, issue qualification or mark HOST_READY.
