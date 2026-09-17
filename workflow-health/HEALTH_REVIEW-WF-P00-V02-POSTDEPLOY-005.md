# HEALTH_REVIEW-WF-P00-V02-POSTDEPLOY-005

```yaml
HEALTH_REVIEW_ID: HEALTH-WF-P00-V02-POSTDEPLOY-005
RUN_ID: RUN-P00-VALIDATION-001
STEP_ID: V02_LAB_EXECUTION_AUTHORITY
BASE_VALIDATION_COMMIT: 9a3854d80b7e4c35c5d2ec933709280ce0baa7fa
CANDIDATE_BRANCH: lane/validation-p00-v02-postdeploy-failclosed
STATUS: CANDIDATE_REVIEW_REQUIRED
PRODUCT_SOURCE_CHANGED: false
NATIVE_EXECUTION_ADVANCED: false
V03_AUTHORIZED: false
LAB_STATE_REQUIRED: STOPPED
EXTERNAL_TRUST_ANCHOR_REQUIRED: PENDING_EXTERNAL_KEY
```

## Findings

### V02-EPHEMERAL-POLICY-003 — stale derived policy could survive a failed reevaluation

The deployed pre-V03 stage previously created `native-policy.candidate.json` only after a READY intake, but it did not invalidate a pre-existing candidate before a later evaluation. A later authority, seal, materializer or LAB-state failure could therefore leave bytes from an earlier successful evaluation present even though the current gate was BLOCKED. The candidate now deletes prior policy state before evaluation and uses an EXIT cleanup to remove any partial/current candidate unless the complete stage succeeds.

Persistent regression cases prove cleanup for blocked authority, seal failure, materializer partial-write failure and LAB-running failure, while preserving the candidate only on complete success.

### V02-PREFLIGHT-CONTENT-004 — read-only proof was metadata-only

The staging preflight previously compared path/type/size/mtime before and after validation. That detected ordinary writes but did not prove byte immutability: same-size content could be changed and mtime restored. The candidate snapshot now binds regular-file SHA-256, mode and metadata, records symlink target text without following the link, and fails closed if any of those values change.

A deterministic regression mutates same-size bytes, restores the original mtime and proves `PREFLIGHT_MUTATED_STAGING` is still returned.

## CI and evidence lifecycle

The new `Validation V02 Tooling` workflow deliberately records its own learning curve rather than rewriting failures away:

- run `35268841620` failed before tests because `pip install -e .` incorrectly treated stale root package metadata as candidate source authority;
- run `35269310254` passed setup/authenticity but failed the exact-source hardened-validator test because a GitHub checkout cannot truthfully substitute for artifact-only exact dev21 source;
- run `35269442201` separated portable server checks from exact-source review obligations and passed compile, shell syntax, authenticity, byte-integrity preflight, watcher fail-closed, stale-policy cleanup and manifest integrity.

Exact-source-dependent validation was then rerun in a detached candidate tree against local exact source commit `934659f535d81d9a4a07389531acc2b9c304fa6d`: all 6 hardened-validator cases passed, all other portable suites passed again, the 17-file tooling manifest matched, and LAB artifact seal verification passed for 6 sealed artifacts.

## P2 readiness conclusion

The LAB artifact seal, baseline/pristine snapshot identities, pending bundle identity, exact dev21 candidate and stopped-LAB boundary remain unchanged. The fixes affect only fail-closed control-plane semantics. Approval envelope remains absent, external trust anchor remains pending, HKLM trust is absent, all 86 native cases remain NOT_RUN, qualification is not issued and HOST_READY is not evaluated.

## Reusable learning proposal

This event should become a canonical learning only during the next reviewed main-state reconciliation:

1. **Derived authority artifacts are current-evaluation scoped.** Any artifact whose meaning depends on a gate being READY must be invalidated before reevaluation and on every unsuccessful exit; durable existence alone must never imply current authority.
2. **Read-only claims bind content, not only metadata.** When a verifier claims a tree remained unchanged, regular-file bytes (or an equivalent cryptographic digest) and link identity must be part of the observation unless the contract explicitly limits the claim to metadata.
3. **CI must respect source addressability.** Server automation must not make an unavailable exact source appear available by substituting a stale or different tree. Portable checks and exact-source review obligations must be labeled separately.

The proposal is evidence, not an activated learning. Main `learning/LEARNING_STATE.json` remains authoritative for activation/effectiveness lifecycle.
