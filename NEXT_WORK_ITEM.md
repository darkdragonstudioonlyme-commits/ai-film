# NEXT WORK ITEM — revise release-control TEST_CHANGE 014 after predecessor fixture gap

~~~yaml
RUN_ID: RUN-P00-VALIDATION-002
WORKFLOW_ID: WF-P00-VALIDATION-ENTRY
MODE: TEST_DESIGN
LANE: TEST_DESIGN
STATUS: READY
WORK_ITEM: REVISE-TEST-DESIGN-P00-DEV23-PRODLIKE-RELEASE-CONTROL-014-R2
ASSIGNEE: CHATGPT
AUTHOR_ACTOR: CHATGPT
PRESERVED_CURSOR: RUN-P00-VALIDATION-002/V02B_LOCAL_AUTHORITY_PACKAGE
INPUT_IDENTITY:
  CURRENT_MAIN: e2b9f0d7924d7983978753db34c0a89678f39a79
  CURRENT_VALIDATION: 4850b4d2930d6f2eaad8065f306314ea8a352867
  PRIOR_TEST_CHANGE: acfd174271173bed5a96a358fc84ffc80389b4ac
  PRIOR_TEST_REVIEW: 4850b4d2930d6f2eaad8065f306314ea8a352867
  SCOPE_FINDING: LOCAL:/home/dragon/ai-film-dev/run-evidence/v143-release-control-014-author-20260924/scope-finding.json
  TARGETED_TV014_RESULT: 13_PASS
  BLOCKED_PREDECESSOR_SUITE: validation/tooling/tests/test_prodlike_deployment_transaction_v2.py
  BLOCKED_PREDECESSOR_TESTS: 22
GOAL: "Revise TEST_CHANGE 014 minimally so the predecessor transaction fixture can supply the new mandatory runtime-manifest fields without weakening the strict 27-key V2 producer/consumer contract or expanding product/runtime behavior."
PROPOSED_AUTHORIZED_MODIFY:
  - validation/tooling/build_prodlike_control_bundle-v2.py
  - validation/tooling/verify_prodlike_control_bundle-v2.py
  - validation/tooling/prodlike_control_templates_v2.json
  - validation/tooling/tests/test_prodlike_control_bundle_v2.py
  - validation/tooling/tests/test_prodlike_deployment_transaction_v2.py
STEPS:
  - IMPLEMENTATION_SCOPE_FINDING: COMPLETE
  - HOST_NON_MUTATION_AFTER_FAILED_AUTHOR_GATE: COMPLETE_PASS
  - STRICT_PRODUCER_CONTRACT: MUST_REMAIN
  - TEST_CHANGE_014_R2_AUTHOR: READY
  - PREDECESSOR_FIXTURE_COVERAGE_MAPPING: READY
  - TEST_REVIEW_014_R2: BLOCKED
  - IMPLEMENTATION_RESUME: BLOCKED
  - PRODLIKE_DEPLOYMENT: BLOCKED
  - LAB_REBUILD_RESEED: BLOCKED
  - NATIVE_SIGNING_HKLM: BLOCKED
CURRENT_STEP: V02_LOCAL_OPERATOR_LAB_AUTHORITY
SUCCESS_OUTPUT: "Revised TEST_CHANGE/coverage evidence explicitly authorizing the fifth test-fixture file and preserving strict V2 semantics; no implementation proof."
ON_SUCCESS: TEST-REVIEW-P00-DEV23-PRODLIKE-RELEASE-CONTROL-014-R2
ON_FAIL: REVISE_TEST_DESIGN_WITHOUT_IMPLEMENTATION
ON_BLOCK: BLOCK-P00-VAL-V03-DEV23-PRODLIKE-RELEASE-CONTROL-R2-DESIGN-057
RETURN_TO: RUN-P00-VALIDATION-002/V02B_LOCAL_AUTHORITY_PACKAGE
EXIT_CONDITION: "R2 explains why four-file scope failed, authorizes only the predecessor fixture as fifth file, defines exact fixture-only edit and regression witness, keeps 27-key contract/ORACLE unchanged, and preserves all host/deployment/native/LAB boundaries."
~~~

Test design only. Do not edit the fifth file until TEST_REVIEW R2 PASS; do not weaken producer requirements, deploy, switch current, modify failed dev23 evidence, mutate user-systemd/LAB, sign authority, write HKLM, run native cases, issue qualification or mark HOST_READY.
