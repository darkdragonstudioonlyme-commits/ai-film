# NEXT WORK ITEM — rebuild corrected dev23 prodlike release 013

~~~yaml
RUN_ID: RUN-P00-VALIDATION-002
WORKFLOW_ID: WF-P00-VALIDATION-ENTRY
MODE: IMPLEMENTATION
LANE: IMPLEMENT
STATUS: READY
WORK_ITEM: REBUILD-P00-DEV23-PRODLIKE-RELEASE-013
ASSIGNEE: CHATGPT
AUTHOR_ACTOR: CHATGPT
PRESERVED_CURSOR: RUN-P00-VALIDATION-002/V02B_LOCAL_AUTHORITY_PACKAGE
INPUT_IDENTITY:
  CURRENT_MAIN: fe3550fae7305bd8327f5326e5ed2752ce549909
  CURRENT_VALIDATION: abac81bd8b9e5e2df206b554950919ae3d754e37
  VERIFY_RUNTIME_AUTHOR_COMMIT: 0a05cd4b0ef49565f77eb503d918828a539b6237
  VERIFY_RUNTIME_AUTHOR_TREE: ca0be120320a8d6aa7af201a9d58523de8a087ff
  VERIFY_RUNTIME_REVIEW: lane/validation-p00:reviews/CODE-REVIEW-P00-DEV23-PRODLIKE-VERIFY-RUNTIME-013.md
  PRODUCT_CANDIDATE: 2f7da39984a7a582c7cf2a84f743299fc7fe735f
  PACKAGE_SHA256: d60433b2b559c975dd93378db7c3c8481ba80896deb539d8227b28b169a83dbf
  WHEEL_SHA256: 55853acf55374db3e8da6159ae6fe26dcad2d0a6b7f022aef79b2009c40253df
GOAL: "Rebuild corrected dev23 release and rebuild-set under a new evidence root using reviewed package/wheel plus promoted builder, prove verify-runtime/runtime-manifest identity and host non-mutation, then hand exact artifact identities to independent review."
STEPS:
  - VERIFY_RUNTIME_CODE_REVIEW: COMPLETE_PASS
  - VALIDATION_LANE_PROMOTION: COMPLETE
  - REVIEWED_PACKAGE_WHEEL_LOCATE: READY
  - STAGED_BROKEN_DEV23_BEFORE_SNAPSHOT: NOT_STARTED
  - CORRECTED_RELEASE_BUILD: NOT_STARTED
  - VERIFY_RUNTIME_EXECUTION: NOT_STARTED
  - REBUILD_SET_BUILD: NOT_STARTED
  - CORRECTED_ARTIFACT_IDENTITY_RECEIPT: NOT_STARTED
  - HOST_AFTER_SNAPSHOT: NOT_STARTED
  - RELEASE_IDENTITY_CODE_REVIEW: BLOCKED
  - NEW_DEPLOYMENT_AUTHORIZATION: BLOCKED
  - LAB_REBUILD_RESEED: BLOCKED
  - NATIVE_SIGNING_HKLM: BLOCKED
CURRENT_STEP: V02_LOCAL_OPERATOR_LAB_AUTHORITY
SUCCESS_OUTPUT: "Corrected release/rebuild-set artifact identities plus verifier PASS and exact non-mutation proof; no deployment proof."
ON_SUCCESS: CODE-REVIEW-P00-DEV23-PRODLIKE-RELEASE-REBUILD-013
ON_FAIL: CORRECT_RELEASE_REBUILD_INPUT_OR_IMPLEMENTATION_WITHOUT_DEPLOYMENT
ON_BLOCK: BLOCK-P00-VAL-V03-DEV23-PRODLIKE-RELEASE-REBUILD-013
RETURN_TO: RUN-P00-VALIDATION-002/V02B_LOCAL_AUTHORITY_PACKAGE
EXIT_CONDITION: "Corrected evidence-only release contains regular 0750 bin/verify-runtime bound by final runtime manifest and passes execution; rebuild-set builds; package/wheel/input identities exact; broken staged dev23/current/user-systemd unchanged; no deployment/LAB/native/signing/HKLM action."
~~~

Evidence build/review only. Do not switch prodlike current, repair/delete staged broken dev23, mutate user-systemd, create deployment authorization, rebuild LAB, sign authority, write HKLM, run native routes, issue qualification or mark HOST_READY.
