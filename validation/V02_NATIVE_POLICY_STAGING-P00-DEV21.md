# Phase00 dev21 — V02 native policy staging

```yaml
STAGING_ID: V02-NATIVE-POLICY-STAGING-P00-DEV21-001
RUN_ID: RUN-P00-VALIDATION-001
STEP_ID: V02_LAB_EXECUTION_AUTHORITY
MATERIALIZER_SHA256: 52083c05fc4fbeab15897a0ae4268f9963a13365909d37c1eca39da00d5c3b74
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
