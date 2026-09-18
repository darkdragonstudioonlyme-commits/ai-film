# LEARNING-LOCAL-AUTHORITY-KEY-PARITY-015

LEARNING_ID: LEARNING-LOCAL-AUTHORITY-KEY-PARITY-015
SCORE: 10
OBSERVED_AT_STATE: V56
TARGET_RELEASE: DOCSYS-V2-R9
CLASS: local-authority-key-identity-parity

## Observation

A reviewed/audited local-key activation selected public identity `5d595732...`, and the deployment receipt confirmed only that a private-key file existed with mode 0600. Before signing, forensic parity verification proved that the only durable owner-only private key on the host derived a different public SHA, `7f14c158dd09ec9e40572131538bab6818e768cc9f33cb1ec3708a09df9a8a69`. No private key deriving the reviewed `5d595732...` identity was found in bounded host, temporary or AI-FILM local storage. File presence and restrictive mode had therefore been mistaken for cryptographic identity parity.

## Generalized learning

Cryptographic authority deployment must verify identity, not merely permissions. A deployment/recovery verifier must derive raw public bytes from the actual private key and bind them to the public file, metadata, key ID/provenance and the ACTIVE trust anchor while separately enforcing owner/mode restrictions. A missing reviewed private identity is superseded/rotated with durable historical evidence; it is never silently regenerated or relabeled. Private bytes must never enter Git or public evidence.

## Success metric

The next qualifying local-authority key deployment or recovery recheck fails closed before an authority envelope can verify when the private key does not derive the public identity pinned by metadata/trust; verification independently binds owner/mode, private-derived raw public bytes, public file, metadata and trust anchor without emitting private bytes; and key rotation/supersession preserves historical identity rather than silently substituting it.
