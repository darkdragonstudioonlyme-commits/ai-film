# Phase00 dev21 — V02 external-authenticity hardening

```yaml
HARDENING_ID: V02-EXTERNAL-AUTHENTICITY-P00-DEV21-001
RUN_ID: RUN-P00-VALIDATION-001
STEP_ID: V02_LAB_EXECUTION_AUTHORITY
STATUS: CANDIDATE_NOT_DEPLOYED
FINDING: V02-AUTHENTICITY-001
HEALTH_EVIDENCE: workflow-health/HEALTH_REVIEW-WF-P00-V02-AUTHENTICITY-003.md
ALGORITHM: ED25519
SIGNED_PAYLOAD: EXACT_RAW_APPROVAL_ENVELOPE_BYTES
NATIVE_EXECUTION_STARTED: false
```

## Threat model

The current Windows operator has FullControl on the local approved inbox. Content-addressed JSON and role pins detect byte substitution and scope drift, but they do not prove that an external owner/controller authored or approved the package. V02 therefore needs an authenticity property that cannot be created merely by writing structurally valid local files.

## Local identity privacy boundary

The existing runtime validator needs exact host/operator scope, but those stable values are not required in the public tooling source. `v02_local_identity.py` loads a sibling mode-600 local context and pins only its SHA-256 in source. Host ID and operator digest are excluded from Git. Context mutation without the reviewed expected hash fails closed before authority consumption.

## Trust-anchor transaction

`validation/tooling/external-authority-trust-anchor.json` is committed in `PENDING_EXTERNAL_KEY` state. `v02_external_authenticity.py` pins the exact SHA-256 of that file. Runtime edits to the trust file without a reviewed verifier update fail `EXTERNAL_AUTHENTICITY_ANCHOR_DRIFT`.

External key activation is a separate transaction. The owner/controller must return a public Ed25519 key identity plus out-of-band provenance. A reviewed update then changes the trust config to `ACTIVE`, records `key_id`, raw-public-key base64, SHA-256 and provenance reference, and updates the verifier's pinned trust-config SHA. No private key belongs on this host or in GitHub.

## Signature contract

After the anchor is active, an approved package must contain `approval-envelope.sig.json` with exactly:

```yaml
schema_version: 1
algorithm: ED25519
key_id: <must equal activated anchor key_id>
payload_sha256: <sha256 of exact raw approval-envelope.json bytes>
signature_b64: <Ed25519 signature of those exact raw bytes>
```

The validator verifies decision/candidate/build/test/contract binding, then external signature authenticity, then protected object refs/pins/suite/fixtures/plans. Because the signed envelope carries the direct refs and `role_pins`, and referenced objects are hash-addressed, the signature transitively authenticates the exact object graph consumed by V02.

## Fail-closed ordering

```text
missing envelope -> BLOCKED
PENDING/non-approve envelope -> BLOCKED
wrong candidate/build/test/contract -> BLOCKED
missing/pending/drifted trust anchor -> BLOCKED
missing/mismatched/invalid external signature -> BLOCKED
only then -> object/pin/suite/authorize validation
only then -> READY_TO_ADVANCE
```

No CLI flag or environment variable may override the production trust config or its expected SHA. Synthetic keys are permitted only inside isolated tests and can never make the runtime anchor ACTIVE.

## Watcher fail-closed correction

The same review found that the previous watcher could leave a stale READY flag if validator output became unreadable before `status` parsing completed. The candidate deletes the flag before each evaluation and only recreates it after a current READY result; malformed output exits with READY absent. This correction does not make authority more permissive.

## Deployment rule

Candidate tooling is source-controlled under `validation/tooling/`. Deployment to `/home/dragon/ai-film-dev/validation-ops/` requires independent review of the exact candidate diff, full negative tests, exact hash verification after copy, and a fresh real-inbox check. Deployment must leave the anchor pending and V02 blocked until external key provenance exists.
