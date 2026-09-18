# HEALTH_REVIEW-WF-P00-V02-WSL-INBOX-011

HEALTH_REVIEW_ID: HEALTH-WF-P00-V02-WSL-INBOX-011
BASE_VALIDATION_HEAD: 4b5a25ef3ec1ebdaefeaac5e9f5bf4231b641f36
FINDING_CLASS: LOCAL_AUTHORITY_STORAGE_SIMPLIFICATION
PRODUCT_SOURCE_CHANGED: false
TRUST_IDENTITY_CHANGED: false
NATIVE_EXECUTION_ADVANCED: false

## Finding

The owner selected same-WSL local authority, but the remaining authority inbox still defaulted to a mounted Windows path. That split trust-domain storage without adding independence and complicated the final V02 workflow.

## Correction

Use `/home/dragon/ai-film-dev/local-authority/dev22/inbox` as the single default authority inbox. Keep the existing private key as a sibling outside the inbox and retain every fail-closed validator/signature/role-pin/current-evaluation boundary. No authority is granted by this storage change.
