# Phase00 dev21 — pre-V03 authority gate

```yaml
GATE_ID: V02-PRE-V03-GATE-P00-DEV21-001
RUN_ID: RUN-P00-VALIDATION-001
STEP_ID: V02_LAB_EXECUTION_AUTHORITY
CURRENT_STATUS: BLOCKED_EXTERNAL_AUTHORITY
PRE_V03_STAGE_SHA256: cbf4e25d7d6a544ca5709f7661f56b927ac766cdbc5bb5292c4475bc410a407a
POLICY_MATERIALIZER_SHA256: cd71be5a65dfc90fa6fdf76f2e865a4651fd717c03fbb6b05cc1dad147020b0e
TRUST_ANCHOR_INSTALLER_SHA256: 34fa9e84a63f54c9164873db99d85aa914b662237714bd945744046e52f96f3c
TRUST_ANCHOR_EXISTS: false
APPROVAL_ENVELOPE_EXISTS: false
LAB_STATE: STOPPED
POLICY_CANDIDATE_EXISTS: false
HKLM_WRITTEN: false
NATIVE_EXECUTION_STARTED: false
```

## Staging sequence

`pre-v03-authority-stage.sh` is fail-closed. It first runs the V02 intake validator; only after intake is READY does it verify the sealed LAB artifacts, invoke the non-installing NativeStore policy materializer, require a real policy candidate, and re-check that `AI-FILM-P00-LAB` is still Stopped. It currently exits 12 at the authority step and creates no policy candidate.

`materialize-v02-native-policy.py` can only write a mode-600 candidate policy after the approved intake has passed exact dev21 admission/suite checks and after the candidate policy successfully instantiates dev21 `NativeStore`. It never writes HKLM.

`install-phase00-trust-anchor.ps1` is the final provisioning tool but defaults to non-commit behavior. A registry write requires explicit `-Commit`, an existing policy file, exact expected SHA-256, matching MachineGuid-derived host scope, matching current operator SID and an elevated Windows administrator context. It refuses to overwrite an existing Phase00 trust anchor and removes a newly-created key if create/write/readback fails.

## Negative install check

The Windows host normally blocks the UNC `.ps1` under its current execution policy. A one-process test used `-ExecutionPolicy Bypass` only to reach the script's first guard with a deliberately nonexistent policy path. The installer rejected it with `POLICY_NOT_FOUND` and returned nonzero. The machine execution policy was not changed.

A subsequent read-only Windows check confirmed both `HKLM\SOFTWARE\AI-FILM-SERVER\Phase00\Trust` and the real `approval-envelope.json` remain absent.

This record is preparation only. No trust authority has been installed and V02 remains BLOCKED.

## Deployed external-authenticity hardening

Finding `V02-AUTHENTICITY-001` shows that the operator-writable approved inbox is not by itself proof of external provenance. The independently reviewed/audited hardening in `validation/V02_EXTERNAL_AUTHENTICITY_HARDENING-P00-DEV21.md` is deployed. The Ed25519 trust config intentionally remains `PENDING_EXTERNAL_KEY`; therefore this step remains BLOCKED until external key provenance is established and separately activated, and no readiness/preflight result may be interpreted as authority.
