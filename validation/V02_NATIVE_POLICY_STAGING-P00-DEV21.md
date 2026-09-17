# Phase00 dev21 — V02 native policy staging

```yaml
STAGING_ID: V02-NATIVE-POLICY-STAGING-P00-DEV21-001
RUN_ID: RUN-P00-VALIDATION-001
STEP_ID: V02_LAB_EXECUTION_AUTHORITY
MATERIALIZER_SHA256: cd71be5a65dfc90fa6fdf76f2e865a4651fd717c03fbb6b05cc1dad147020b0e
CURRENT_STATUS: BLOCKED
CURRENT_REASON: AUTHORITY_INTAKE_NOT_READY
VALIDATOR_REASON: APPROVAL_ENVELOPE_MISSING
POLICY_WRITTEN: false
HKLM_WRITTEN: false
NATIVE_EXECUTION_STARTED: false
```

`materialize-v02-native-policy.py` is a staging boundary, not an authority issuer. It first runs the hardened V02 intake validator. Unless intake returns `READY_TO_ADVANCE`, it exits 12 and writes no policy candidate.

Only after a valid external intake exists may it build a candidate NativeStore policy from the exact approved `role_pins` and hash-addressed object bytes. Before writing the mode-600 candidate file it instantiates dev21 `NativeStore`, requires single registration/design/code selection, verifies the LAB registration class and approved suite ref, and reuses the exact contract files from dev21.

The materializer never writes the Windows registry. The current run against the real protected inbox returned `AUTHORITY_INTAKE_NOT_READY / APPROVAL_ENVELOPE_MISSING`; `native-policy.candidate.json` was confirmed absent afterward.

This staging step therefore cannot close V02, start the LAB, install an HKLM trust anchor, execute native acceptance, or issue qualification/HOST_READY.

## Deployed external-authenticity hardening

Finding `V02-AUTHENTICITY-001` shows that the operator-writable approved inbox is not by itself proof of external provenance. The independently reviewed/audited hardening in `validation/V02_EXTERNAL_AUTHENTICITY_HARDENING-P00-DEV21.md` is deployed. The Ed25519 trust config intentionally remains `PENDING_EXTERNAL_KEY`; therefore this step remains BLOCKED until external key provenance is established and separately activated, and no readiness/preflight result may be interpreted as authority.
