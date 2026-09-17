# Phase00 dev21 — pre-V03 authority gate

```yaml
GATE_ID: V02-PRE-V03-GATE-P00-DEV21-001
RUN_ID: RUN-P00-VALIDATION-001
STEP_ID: V02_LAB_EXECUTION_AUTHORITY
CURRENT_STATUS: BLOCKED_EXTERNAL_AUTHORITY
PRE_V03_STAGE_SHA256: 4808eabfdea1e7104100d9e2342962e0b9f3ce518db35d21bff4e57d66b50f31
POLICY_MATERIALIZER_SHA256: cd71be5a65dfc90fa6fdf76f2e865a4651fd717c03fbb6b05cc1dad147020b0e
TRUST_ANCHOR_INSTALLER_SHA256: 34fa9e84a63f54c9164873db99d85aa914b662237714bd945744046e52f96f3c
POSTDEPLOY_FAILCLOSED_HARDENING: CANDIDATE_REVIEW_REQUIRED
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

`pre-v03-authority-stage.sh` treats `native-policy.candidate.json` as an ephemeral artifact of the **current successful evaluation**, not as durable authority. It deletes any prior candidate before evaluating V02 and registers an EXIT cleanup that removes the candidate on every unsuccessful exit. Only a run in which authority intake, artifact seal, NativeStore materialization and the final `AI-FILM-P00-LAB = Stopped` check all succeed may retain the current candidate for the separate trust-anchor installation review.

This closes a post-deployment fail-closed gap: a policy candidate produced by an earlier READY evaluation cannot survive a later authority, seal, materializer or LAB-state failure and be mistaken for current evidence. The regression suite covers blocked authority, seal failure, materializer partial-write failure, LAB-running failure and the successful retention case.

`materialize-v02-native-policy.py` itself is unchanged. It can only write a mode-600 candidate policy after approved intake passes exact-dev21 admission/suite checks and after the policy successfully instantiates the exact dev21 `NativeStore`; it never writes HKLM.

## Review evidence boundary

Portable server-side checks are enforced by `.github/workflows/validation-v02-tooling.yml`. GitHub Actions run `35269442201` passed compile, shell syntax, external-authenticity, byte-integrity preflight, watcher fail-closed, pre-V03 stale-policy cleanup and manifest-integrity checks. The exact-source-dependent hardened-validator regression cannot be truthfully reconstructed from the GitHub checkout because exact dev21 source remains artifact-only; it was rerun in a detached local review tree against exact source commit `934659f535d81d9a4a07389531acc2b9c304fa6d` and passed all six cases.

The two earlier CI failures remain part of the evidence history: run `35268841620` exposed an invalid assumption that the stale root `pyproject.toml` could install the candidate source, and run `35269310254` exposed the invalid assumption that the GitHub checkout could stand in for exact dev21 source. Neither failure weakened a V02 predicate; the final workflow separates portable checks from exact-source review obligations.

## Trust-anchor boundary

`install-phase00-trust-anchor.ps1` remains the final provisioning tool and defaults to non-commit behavior. A registry write still requires explicit `-Commit`, an existing current policy file, exact expected SHA-256, matching MachineGuid-derived host scope, matching current operator SID and an elevated Windows administrator context. It refuses to overwrite an existing Phase00 trust anchor and removes a newly-created key if create/write/readback fails.

The Windows trust key and real `approval-envelope.json` remain absent, the external Ed25519 trust config remains `PENDING_EXTERNAL_KEY`, and `AI-FILM-P00-LAB` remains stopped. This candidate does not approve authority, install trust, start LAB execution, advance V02, run V03, issue qualification or change HOST_READY.
