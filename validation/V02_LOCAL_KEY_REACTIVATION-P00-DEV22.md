# Phase00 dev22 — V02 local key reactivation after identity-parity finding

REACTIVATION_ID: V02-LOCAL-KEY-REACTIVATION-P00-DEV22-001
RUN_ID: RUN-P00-VALIDATION-002
STEP_ID: V02_LOCAL_OPERATOR_LAB_AUTHORITY
BASE_VALIDATION_HEAD: 9673283c3a8422485db4c3e48baa481dd720551d
STATUS: DEPLOYED_ON_AUDIT_PROMOTION
FINDING: V02-LOCAL-KEY-PARITY-001
PREVIOUS_KEY_ID: AI-FILM-LOCAL-DEV22-20260918-5d5957324955
PREVIOUS_PUBLIC_KEY_SHA256: 5d5957324955fb92d998aa7ab54bf551f580ef14b29cad0086274328526a285e
PREVIOUS_ACTIVATION_DISPOSITION: SUPERSEDED_PRIVATE_KEY_IDENTITY_UNAVAILABLE
NEW_KEY_ID: AI-FILM-P00-DEV22-LOCAL-001
NEW_PUBLIC_KEY_SHA256: 7f14c158dd09ec9e40572131538bab6818e768cc9f33cb1ec3708a09df9a8a69
NEW_PROVENANCE_REF: WSL_LOCAL_OPERATOR_SELF_MANAGED:7f14c158dd09ec9e40572131538bab6818e768cc9f33cb1ec3708a09df9a8a69
PRIVATE_KEY_LOCATION_CLASS: WSL_OWNER_ONLY_OUTSIDE_GIT
PRIVATE_KEY_MODE_REQUIRED: 0600
AUTHORITY_MODEL: LOCAL_OPERATOR_SAME_WSL_TRUST_DOMAIN
NATIVE_EXECUTION_STARTED: false

## Finding

Post-audit deployment for the previous activation verified the trust-anchor bytes and recorded only `PRIVATE_KEY_MODE=600`. A later pre-signing parity check proved that the durable private/public key pair on the host derived public SHA `7f14c158dd09ec9e40572131538bab6818e768cc9f33cb1ec3708a09df9a8a69`, while the reviewed trust anchor selected `5d595732...`. No private key deriving the reviewed `5d595732...` identity is present in the searched host, temporary or bounded backup locations. The old activation therefore cannot produce a valid signature and must not be used.

The old key identity remains immutable historical evidence; it is not regenerated or silently substituted. The durable local pair at `/home/dragon/ai-film-dev/local-authority/dev22/` existed before the failed activation, remains owner-only mode 0600, and has metadata binding key ID `AI-FILM-P00-DEV22-LOCAL-001`, public SHA `7f14c158dd09ec9e40572131538bab6818e768cc9f33cb1ec3708a09df9a8a69` and truthful same-host provenance.

## Hardening

This reactivation adds `verify_local_authority_key_parity.py`. Deployment/recovery must now prove, without emitting private bytes: owner/mode 0600, Ed25519 private-key parse, derived-public equality to the raw public file, metadata equality, and exact ACTIVE trust-anchor key/provenance equality. A mode-only receipt can no longer satisfy key deployment parity.

The committed trust anchor is rebound to the durable key above and the signature verifier/manifest are repinned. This transaction does not approve an envelope, rebuild LAB, create READY/native policy, or advance V03.

## Deployment transaction

Exact reviewed/audited reactivation head `665d34959c48854bd089423874ea9abb9e6515bc` was deployed to the WSL validation-ops surface after canonical CI `35319634603` succeeded. Deployment is governed by `validation/V02_LOCAL_KEY_REACTIVATION_DEPLOYMENT-P00-DEV22.md` and becomes canonical deployment authority only with its predeclared independent deployment review/audit records on promotion.
