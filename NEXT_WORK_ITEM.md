# NEXT WORK ITEM — update Windows host, then complete V02 authority

```yaml
RUN_ID: RUN-P00-VALIDATION-002
WORKFLOW_ID: WF-P00-VALIDATION-ENTRY
LANE: VALIDATION
STATUS: BLOCKED_USER_WINDOWS_UPDATE_BEFORE_EPHEMERAL_AUTHORITY_PACKAGE
MODE: VALIDATION
PHASE: "00 — Host / WSL"
WORK_ITEM: M-P00-VALIDATION-DEV22
INPUT_IDENTITY:
  ACCEPTED_VERSION: 0.1.0.dev22
  SOURCE_COMMIT: 86bb64938a136e3f8d6cfd0266685a01cb832b77
  PACKAGE_SHA256: c2ea52087039f4c7b98c53a7cc0eaf1a4a0f931645f86491bf2eb8ef12956aae
  VALIDATION_EVIDENCE_HEAD: 517783d29aecb3d6ae1b0548109480733fa36fe6
  CANDIDATE_ID: 6f895394-e0b4-5434-bebc-79ee4e576282
  AUTHORITY_MODEL: LOCAL_OPERATOR_SAME_WSL_TRUST_DOMAIN
  AUTHORITY_INBOX: /home/dragon/ai-film-dev/local-authority/dev22/inbox
  KEY_ID: AI-FILM-P00-DEV22-LOCAL-001
  WSL_INBOX_DEPLOYMENT_RECEIPT_SHA256: 8bb2f75cfe493d3e4d50f5a78e16f77d902870a7607928cb58fe2a69dbedc014
  PRODLIKE_RUNTIME_STATUS: READY_NON_NATIVE_PRODLIKE_OPERATIONS
  LAB_TECHNICAL_STATUS: DEV22_REBUILT_SEALED_RESTORE_PROBED
  HOST_EDITION: Professional
  HOST_DISPLAY_VERSION: 23H2
  HOST_BUILD: 22631
  HOST_UBR: 3296
  SUPPORT_MARGIN_REQUIRED_DAYS: 90
  MINIMUM_TARGET: 25H2_OR_LATER_WITH_90_DAY_MARGIN
GOAL: "Update the Windows host to a supported release with >=90-day margin, reboot, then create/sign/verify the fresh dev22 local-authority graph entirely inside WSL and only then enter V03."
STEPS:
  - V00_VALIDATION_LANE_ACTIVATION: COMPLETE
  - V01_CODE_REVIEW_GATE: COMPLETE
  - V02A_WINDOWS_HOST_SUPPORT_UPDATE: BLOCKED_USER_ACTION
  - V02B_LOCAL_AUTHORITY_PACKAGE: NOT_STARTED
  - V03_NATIVE_LAB_REGRESSION: NOT_STARTED
  - V04_QUALIFICATION_RECEIPT: NOT_STARTED
  - V05_SITE_VALIDATION: NOT_STARTED
  - V06_GATE_ASSESSMENT: NOT_STARTED
CURRENT_STEP: V02_LOCAL_OPERATOR_LAB_AUTHORITY
CURRENT_SUBSTEP: V02A_WINDOWS_HOST_SUPPORT_UPDATE
SUCCESS_OUTPUT: "Post-update live facts satisfy exact support/profile policy; fresh <=24h WSL-local authority package passes V02 intake/pre-V03; no native case ran before V02 closure."
ON_SUCCESS: RUN-P00-VALIDATION-002/V03_NATIVE_LAB_REGRESSION
ON_FAIL: VALIDATION_FAILURE_ROUTE
ON_BLOCK: BLOCK-P00-VAL-HOST-SUPPORT-001
EXIT_CONDITION: "Windows host is updated/rebooted and re-observed with >=90-day support margin, then the fresh WSL-local authority graph passes current V02 verification before V03 starts."
```

## User action now

1. Open Windows Settings → Windows Update.
2. Install Windows 11 **25H2 or a newer supported release** (not 24H2 for this project, because its remaining support is below the required 90-day margin).
3. Restart Windows completely.
4. Return here and say **"đã cập nhật Windows"**.

Do not create or move any key/authority files manually. After the reboot, validation will re-read the live Windows facts and handle the authority graph/signature/preflight/intake entirely inside WSL.
