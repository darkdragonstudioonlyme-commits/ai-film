# Phase00 dev22 — V02 WSL-local authority inbox simplification

DESIGN_ID: V02-WSL-LOCAL-AUTHORITY-INBOX-P00-DEV22-001
RUN_ID: RUN-P00-VALIDATION-002
STEP_ID: V02_LOCAL_OPERATOR_LAB_AUTHORITY
BASE_VALIDATION_HEAD: 4b5a25ef3ec1ebdaefeaac5e9f5bf4231b641f36
AUTHORITY_MODEL: LOCAL_OPERATOR_SAME_WSL_TRUST_DOMAIN
OLD_DEFAULT_INBOX: /mnt/c/Users/Admin/AppData/Local/AI-FILM/LAB/authority-approved/dev22
NEW_DEFAULT_INBOX: /home/dragon/ai-film-dev/local-authority/dev22/inbox
PRIVATE_KEY_LOCATION: /home/dragon/ai-film-dev/local-authority/dev22/authority-ed25519-private.pem
PRODUCT_SOURCE_CHANGED: false
TRUST_IDENTITY_CHANGED: false
NATIVE_EXECUTION_ADVANCED: false

## Intent

Keep the complete local-authority workflow inside the owner's WSL trust domain. The approval object graph, detached signature and intake staging move from the mounted Windows filesystem to a private WSL-local inbox. The durable private key stays outside the inbox in the existing sibling key location and remains mode 0600.

## Exact semantic change

Only default inbox paths and their fail-closed regression fixtures change. Candidate/source/package/build/test/contract identities, trust-anchor bytes, durable key identity, signature verification, content addressing, role pins, <=24h suite lifetime, artifact-seal checks, current-evaluation invalidation and V03 boundaries are unchanged.

The canonical WSL-local inbox is `/home/dragon/ai-film-dev/local-authority/dev22/inbox`. Explicit `--inbox` overrides remain available for isolated regression tests.

## Security boundary

Private key bytes never enter Git or the inbox. Moving the inbox to WSL does not upgrade same-trust-domain authority into independent provenance. Missing/invalid authority remains BLOCKED and stale READY/native-policy artifacts remain fail-closed.