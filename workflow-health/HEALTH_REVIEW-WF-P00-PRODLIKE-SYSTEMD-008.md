# HEALTH_REVIEW-WF-P00-PRODLIKE-SYSTEMD-008

HEALTH_REVIEW_ID: HEALTH-WF-P00-PRODLIKE-SYSTEMD-008
WORKFLOW_ID: WF-P00-VALIDATION-ENTRY
RUN_ID: RUN-P00-VALIDATION-001
FINDING_CLASS: PRODLIKE_USER_SYSTEMD_DEPLOYMENT_RECOVERABILITY
STATUS: CORRECTED_PENDING_REVIEW
PRODUCT_SOURCE_CHANGED: false
NATIVE_EXECUTION_ADVANCED: false

## Finding

Live audit found the eleven documented production-like timers absent although current runtime/control bytes and portable backups were healthy. The supervision definitions existed only inside rotating control backups/offhost export, while the validation lane had no machine verifier for live deployment parity. This allowed the host to lose the user-systemd layer without repository CI detecting it.

## Correction

Recovery restored exact manifest-bound user-systemd bytes from verified backup, re-enabled the lingering `dragon` user manager timers, reran periodic services, required runtime-health PASS, and refreshed backup/export evidence. The first wrong-scope system-unit attempt was detected and rolled back before timer activation; the durable runbook now forbids that scope.

A new portable verifier plus five-case regression binds backup manifest → archive members → deployed user-unit bytes. Validation CI executes the regression and path/branch filters now include prodlike recovery design/review/audit records.

## Boundary

V02 remains BLOCKED on external Ed25519 provenance and signed approval. All 86 native cases remain NOT_RUN; LAB/SITE/qualification/HOST_READY do not advance. The recovery is non-native operational control-plane repair only.
