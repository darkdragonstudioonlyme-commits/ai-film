# NEXT WORK ITEM — implement release-control producer/consumer compatibility 014

~~~yaml
RUN_ID: RUN-P00-VALIDATION-002
WORKFLOW_ID: WF-P00-VALIDATION-ENTRY
MODE: IMPLEMENTATION
LANE: IMPLEMENT
STATUS: READY
WORK_ITEM: IMPLEMENT-P00-DEV23-PRODLIKE-RELEASE-CONTROL-014
ASSIGNEE: CHATGPT
AUTHOR_ACTOR: CHATGPT
PRESERVED_CURSOR: RUN-P00-VALIDATION-002/V02B_LOCAL_AUTHORITY_PACKAGE
INPUT_IDENTITY:
  CURRENT_MAIN: aad9eecfbf116230966dd0495fce4a52e0d30439
  CURRENT_VALIDATION: 4850b4d2930d6f2eaad8065f306314ea8a352867
  TEST_CHANGE_COMMIT: acfd174271173bed5a96a358fc84ffc80389b4ac
  TEST_REVIEW_COMMIT: 4850b4d2930d6f2eaad8065f306314ea8a352867
  REVIEW_SUPPORT_COMMIT: 8874985ba34c2a7c16068f6cd49f324c6b2a6f17
  TARGET_V2_KEY_COUNT: 27
  ORACLE_CHANGED: false
FILES_ALLOWED:
  - validation/tooling/build_prodlike_control_bundle-v2.py
  - validation/tooling/verify_prodlike_control_bundle-v2.py
  - validation/tooling/prodlike_control_templates_v2.json
  - validation/tooling/tests/test_prodlike_control_bundle_v2.py
GOAL: "Implement the reviewed exact V2 release-control contract and real producer→generated-consumer constructibility witness without host mutation or historical-byte drift."
STEPS:
  - TEST_CHANGE_014: COMPLETE
  - TEST_REVIEW_014: COMPLETE_PASS
  - FOUR_FILE_IMPLEMENTATION: READY
  - TV014_01_12_AUTHOR_TESTS: NOT_STARTED
  - PREDECESSOR_REGRESSION: NOT_STARTED
  - HISTORICAL_DEV22_HARDCUT: NOT_STARTED
  - HOST_NON_MUTATION: NOT_STARTED
  - AUTHOR_CANDIDATE_FREEZE: BLOCKED
  - CLAUDE_CODE_REVIEW: BLOCKED
  - CONTROL_BUNDLE_REBUILD: BLOCKED
  - PRODLIKE_DEPLOYMENT_AUTHORIZATION: BLOCKED
  - LAB_REBUILD_RESEED: BLOCKED
  - NATIVE_SIGNING_HKLM: BLOCKED
CURRENT_STEP: V02_LOCAL_OPERATOR_LAB_AUTHORITY
SUCCESS_OUTPUT: "Exact four-file implementation candidate plus TV014/predecessor/historical/host-nonmutation author evidence; no deployment proof."
ON_SUCCESS: CODE-REVIEW-P00-DEV23-PRODLIKE-RELEASE-CONTROL-014
ON_FAIL: FIX_WITHIN_REVIEWED_FOUR_FILE_SCOPE_OR_RETURN_TO_TEST_DESIGN
ON_BLOCK: BLOCK-P00-VAL-V03-DEV23-PRODLIKE-RELEASE-CONTROL-IMPLEMENT-056
RETURN_TO: RUN-P00-VALIDATION-002/V02B_LOCAL_AUTHORITY_PACKAGE
EXIT_CONDITION: "Only four reviewed files changed; generated V2 release-control has exact 27 keys; real generated consumer and verifier both accept the same valid document; required negative matrices reject drift; 62 other template rows and historical dev22 bytes exact; TV009/010/011/012/013 + historical regression retained; host current/failed trees/user-systemd unchanged; no deployment/LAB/native/signing/HKLM action."
~~~

Implementation/tests only. Do not deploy, switch current, modify failed dev23 evidence, mutate user-systemd, rebuild LAB, create deployment authorization, sign authority, write HKLM, run native cases, issue qualification or mark HOST_READY.
