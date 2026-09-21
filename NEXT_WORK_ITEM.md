# NEXT WORK ITEM — complete V02 local authority package

```yaml
RUN_ID: RUN-P00-VALIDATION-002
WORKFLOW_ID: WF-P00-VALIDATION-ENTRY
LANE: VALIDATION
STATUS: READY_TO_RESOLVE_V02_BLOCK
MODE: VALIDATION
PHASE: "00 — Host / WSL"
WORK_ITEM: M-P00-VALIDATION-DEV22
INPUT_IDENTITY:
  ACCEPTED_VERSION: 0.1.0.dev22
  SOURCE_COMMIT: 86bb64938a136e3f8d6cfd0266685a01cb832b77
  PACKAGE_SHA256: c2ea52087039f4c7b98c53a7cc0eaf1a4a0f931645f86491bf2eb8ef12956aae
  VALIDATION_EVIDENCE_HEAD: 43956bf0f125ee551c1c815220034a42b6a82b7e
  CANDIDATE_ID: 6f895394-e0b4-5434-bebc-79ee4e576282
  AUTHORITY_MODEL: LOCAL_OPERATOR_SAME_WSL_TRUST_DOMAIN
  AUTHORITY_INBOX: /home/dragon/ai-film-dev/local-authority/dev22/inbox
  KEY_ID: AI-FILM-P00-DEV22-LOCAL-001
  WSL_INBOX_DEPLOYMENT_RECEIPT_SHA256: 8bb2f75cfe493d3e4d50f5a78e16f77d902870a7607928cb58fe2a69dbedc014
  HOST_EDITION: Professional
  HOST_DISPLAY_VERSION: 25H2
  HOST_BUILD: 26200
  HOST_UBR: 9457
  HOST_POST_UPDATE_RECEIPT_SHA256: 2cd680bbd8a411584ba60f1455833dc357327a5ac9a28d194664fcd46968692c
  HOST_SUPPORT_END_DATE: 2027-10-12
  HOST_REMAINING_SUPPORT_FLOOR_DAYS: 385
  SUPPORT_MARGIN_REQUIRED_DAYS: 90
  PRODLIKE_RUNTIME_STATUS: READY_NON_NATIVE_PRODLIKE_OPERATIONS
  LAB_TECHNICAL_STATUS: DEV22_REBUILT_SEALED_RESTORE_PROBED
GOAL: "Construct, review, sign and verify the fresh dev22 WSL-local authority graph for the current host/profile without starting native execution before V02 closes."
STEPS:
  - V00_VALIDATION_LANE_ACTIVATION: COMPLETE
  - V01_CODE_REVIEW_GATE: COMPLETE
  - V02A_WINDOWS_HOST_SUPPORT_UPDATE: COMPLETE_REVIEWED_AUDITED
  - V02B_LOCAL_AUTHORITY_PACKAGE: READY
  - V03_NATIVE_LAB_REGRESSION: NOT_STARTED
  - V04_QUALIFICATION_RECEIPT: NOT_STARTED
  - V05_SITE_VALIDATION: NOT_STARTED
  - V06_GATE_ASSESSMENT: NOT_STARTED
CURRENT_STEP: V02_LOCAL_OPERATOR_LAB_AUTHORITY
CURRENT_SUBSTEP: V02B_LOCAL_AUTHORITY_PACKAGE
SUCCESS_OUTPUT: "Fresh <=24h WSL-local authority graph binds exact current host/profile/candidate/plans, verifies the existing durable local signature, and passes preflight/intake/artifact-seal/pre-V03 while all native cases remain NOT_RUN."
ON_SUCCESS: RUN-P00-VALIDATION-002/V03_NATIVE_LAB_REGRESSION
ON_FAIL: VALIDATION_FAILURE_ROUTE
ON_BLOCK: BLOCK-P00-VAL-LOCAL-AUTH-DEV22-001
EXIT_CONDITION: "The exact current local-authority graph is independently reviewed, signed with the existing WSL-local key and passes all current V02/pre-V03 verification before V03 starts."
```

## Execution now

No user action is required for this substep. Re-observe the durable host/key/source/tooling/LAB prerequisites immediately before creating the expiring authority graph. Keep the private key outside Git and outside the inbox. Do not start the LAB or any native case until V02 verification is complete.
