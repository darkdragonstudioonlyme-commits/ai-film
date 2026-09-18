# HEALTH_REVIEW-WF-P00-V02-LOCAL-KEY-PARITY-011

HEALTH_REVIEW_ID: WF-P00-V02-LOCAL-KEY-PARITY-011
RUN_ID: RUN-P00-VALIDATION-002
BASE_VALIDATION_HEAD: 9673283c3a8422485db4c3e48baa481dd720551d
FINDING: V02-LOCAL-KEY-PARITY-001
SEVERITY: HIGH
STATUS: CORRECTED_PENDING_REVIEW_AUDIT
PREVIOUS_KEY_ID: AI-FILM-LOCAL-DEV22-20260918-5d5957324955
PREVIOUS_PUBLIC_KEY_SHA256: 5d5957324955fb92d998aa7ab54bf551f580ef14b29cad0086274328526a285e
DURABLE_KEY_ID: AI-FILM-P00-DEV22-LOCAL-001
DURABLE_PUBLIC_KEY_SHA256: 7f14c158dd09ec9e40572131538bab6818e768cc9f33cb1ec3708a09df9a8a69
NATIVE_EXECUTION_STARTED: false

## Finding

The audited activation selected public identity `5d595732...`, but the durable owner-only local key directory held a different key pair `7f14c158...`. The deployment receipt recorded mode 0600 but did not prove that the private key derived the public fingerprint in the reviewed trust anchor. Search of the bounded host, temporary and AI-FILM local storage found no private key matching `5d595732...`; therefore that activation is unusable for signing and is superseded rather than silently substituted.

## Correction

The reactivation binds the already durable mode-0600 local key identity and adds an independent verifier that parses the Ed25519 private key, derives its raw public key, compares the raw public file, metadata and ACTIVE trust anchor, checks current-user ownership and exact 0600 modes, and outputs only non-secret identity/status. A mode-only deployment receipt can no longer pass key identity verification.

Design-time evidence: key-parity regression 6/6 PASS; live parity PASS; signature regression 7/7; hardened validator 7/7; watcher 3/3; pre-V03 5/5; manifest 20/20; prodlike user-systemd verifier 5/5. No approval envelope, READY flag, native policy or native case result was created.
