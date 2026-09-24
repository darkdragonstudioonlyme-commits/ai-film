# NEXT WORK ITEM — implement verify-runtime release contract 013

~~~yaml
RUN_ID: RUN-P00-VALIDATION-002
WORKFLOW_ID: WF-P00-VALIDATION-ENTRY
MODE: IMPLEMENTATION
LANE: IMPLEMENT
STATUS: READY
WORK_ITEM: IMPL-P00-DEV23-PRODLIKE-VERIFY-RUNTIME-013
ASSIGNEE: CHATGPT
AUTHOR_ACTOR: CHATGPT
PRESERVED_CURSOR: RUN-P00-VALIDATION-002/V02B_LOCAL_AUTHORITY_PACKAGE
INPUT_IDENTITY:
  CURRENT_MAIN: 30040e36f356a742a9054a0debe42e0016ab050f
  TEST_REVIEW_COMMIT: f4c68b47f154c3f4ff38acf64127d4adc1e02c28
  TEST_CHANGE: test-governance/TEST_CHANGE-P00-DEV23-PRODLIKE-VERIFY-RUNTIME-013.md
  TEST_REVIEW: test-governance/TEST_REVIEW-P00-DEV23-PRODLIKE-VERIFY-RUNTIME-013.md
  PRODUCT_SOURCE: 2f7da39984a7a582c7cf2a84f743299fc7fe735f
AUTHORIZED_MODIFY:
  - validation/tooling/build_prodlike_release-v2.py
  - validation/tooling/tests/test_prodlike_release_v2.py
GOAL: "Implement candidate-generic bin/verify-runtime generation, runtime-manifest verifier hash binding, final verifier self-check, and TV013-01..12 tests within exactly the reviewed two-file scope."
STEPS:
  - TEST_REVIEW_013: COMPLETE_PASS
  - IMPLEMENT_VERIFY_RUNTIME: READY
  - TV013_TARGETED_TESTS: NOT_STARTED
  - TV010_TV011_TV012_TV009_REGRESSION: NOT_STARTED
  - HISTORICAL_11_REGRESSION: NOT_STARTED
  - STAGED_DEV23_NON_MUTATION_SNAPSHOT: NOT_STARTED
  - AUTHOR_FREEZE: BLOCKED
  - CLAUDE_CODE_REVIEW: BLOCKED
  - NEW_DEPLOYMENT_AUTHORIZATION: BLOCKED
  - LAB_REBUILD_RESEED: BLOCKED
  - NATIVE_SIGNING_HKLM: BLOCKED
CURRENT_STEP: V02_LOCAL_OPERATOR_LAB_AUTHORITY
SUCCESS_OUTPUT: "Exact two-file candidate commit/tree plus TV013/predecessor/non-mutation evidence; no deployment proof."
ON_SUCCESS: CODE-REVIEW-P00-DEV23-PRODLIKE-VERIFY-RUNTIME-013
ON_FAIL: SAME_CAUSAL_FAMILY_IMPLEMENTATION_CORRECTION_OR_REOPEN_TEST_DESIGN
ON_BLOCK: BLOCK-P00-VAL-V03-DEV23-PRODLIKE-VERIFY-RUNTIME-013-IMPLEMENTATION
RETURN_TO: RUN-P00-VALIDATION-002/V02B_LOCAL_AUTHORITY_PACKAGE
EXIT_CONDITION: "Only two authorized files changed; generated verifier 0750/self-bound/clean-env passes; all TV013 negative cases and predecessor regressions pass; staged broken dev23 before/after snapshot exact; no deployment/LAB/native/signing/HKLM action."
~~~

Authoring/tests only. Do not create deployment authorization, switch prodlike current, repair/delete staged dev23, mutate user-systemd, rebuild LAB, sign authority, write HKLM, run native routes, issue qualification or mark HOST_READY.
