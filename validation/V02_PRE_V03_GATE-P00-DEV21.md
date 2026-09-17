# Phase00 dev21 — pre-V03 authority gate

```yaml
GATE_ID: V02-PRE-V03-GATE-P00-DEV21-001
RUN_ID: RUN-P00-VALIDATION-001
STEP_ID: V02_LAB_EXECUTION_AUTHORITY
CURRENT_STATUS: BLOCKED_EXTERNAL_AUTHORITY
PRE_V03_STAGE_SHA256: 4808eabfdea1e7104100d9e2342962e0b9f3ce518db35d21bff4e57d66b50f31
POLICY_MATERIALIZER_SHA256: cd71be5a65dfc90fa6fdf76f2e865a4651fd717c03fbb6b05cc1dad147020b0e
TRUST_ANCHOR_INSTALLER_SHA256: 34fa9e84a63f54c9164873db99d85aa914b662237714bd945744046e52f96f3c
POSTDEPLOY_FAILCLOSED_HARDENING: DEPLOYED
DEPLOYMENT_EVIDENCE: validation/V02_POSTDEPLOY_FAILCLOSED_DEPLOYMENT-P00-DEV21.md
POLICY_CANDIDATE_CURRENT_EVALUATION_ONLY: true
POLICY_CANDIDATE_REMOVED_ON_FAILED_STAGE: true
TRUST_ANCHOR_EXISTS: false
APPROVAL_ENVELOPE_EXISTS: false
LAB_STATE: STOPPED
POLICY_CANDIDATE_EXISTS: false
HKLM_WRITTEN: false
NATIVE_EXECUTION_STARTED: false
```

## Staging sequence

The deployed `pre-v03-authority-stage.sh` treats `native-policy.candidate.json` as an ephemeral artifact of the **current successful evaluation**, not as durable authority. It deletes any prior candidate before evaluating V02 and registers an EXIT cleanup that removes the candidate on every unsuccessful exit. Only a run in which authority intake, artifact seal, NativeStore materialization and the final `AI-FILM-P00-LAB = Stopped` check all succeed may retain the current candidate for the separate trust-anchor installation review.

This closes the post-deployment fail-closed gap identified by `V02-EPHEMERAL-POLICY-003`: a policy candidate produced by an earlier READY evaluation cannot survive a later authority, seal, materializer or LAB-state failure and be mistaken for current evidence. Persistent tests cover blocked authority, seal failure, materializer partial-write failure, LAB-running failure and successful-current-policy retention.

`materialize-v02-native-policy.py` itself is unchanged. It can only write a mode-600 candidate policy after approved intake passes exact-dev21 admission/suite checks and after the policy successfully instantiates the exact dev21 `NativeStore`; it never writes HKLM.

## Review and deployment evidence

Exact design SHA `2ed82c780ec988caafd7dd0b8086d0cefc534e49` passed server workflow run `35270885138` and independent exact-source review. Review commit `b5d2cbcfb2ecce42886eb0b89369f4dc07e985d9` passed run `35270988157`; audit commit `3958363dd343bcb1c11ef199e4a55816111b4037` passed run `35271086586`.

Deployment copied the 17 manifest-bound audited files into `/home/dragon/ai-film-dev/validation-ops/`, preserving the private local identity context and pending external trust config byte-for-byte. Post-copy compile/syntax, 6 authenticity cases, 6 exact-source hardened-validator cases, 1 content-integrity case, 3 watcher cases, 5 pre-V03 cases, 17 manifest hashes and the six-artifact LAB seal all passed.

The earlier CI failures `35268841620` and `35269310254` remain immutable evidence of invalid package/source-addressability assumptions. They were corrected by separating portable server checks from exact-source local review rather than by substituting stale repository source.

## Trust-anchor boundary

`install-phase00-trust-anchor.ps1` remains the final provisioning tool and defaults to non-commit behavior. A registry write still requires explicit `-Commit`, an existing current policy file, exact expected SHA-256, matching MachineGuid-derived host scope, matching current operator SID and an elevated Windows administrator context. It refuses to overwrite an existing Phase00 trust anchor and removes a newly-created key if create/write/readback fails.

After deployment, the real authoritative inbox still returned `MISSING / APPROVAL_ENVELOPE_MISSING`; deployed pre-V03 returned rc=12; policy/READY remained absent; the Windows trust key remained absent; the external Ed25519 trust config remained `PENDING_EXTERNAL_KEY`; and `AI-FILM-P00-LAB` remained stopped. Deployment does not approve authority, install trust, start LAB execution, advance V02, run V03, issue qualification or change HOST_READY.
