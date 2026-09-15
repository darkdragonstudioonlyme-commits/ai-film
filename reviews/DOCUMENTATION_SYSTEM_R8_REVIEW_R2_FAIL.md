# Documentation System V2 R8 — Detailed Review R2

```yaml
REVIEW_ID: DOC-V2-R8-REVIEW-001-R2
REVIEW_LANE: lane/docs-v2-r8-review
TARGET_COMMIT: dd9134df7fd3f5d031260d4f78d91b993e699837
SOURCE_IMPLEMENTATION_MODIFIED: false
VERDICT: FAIL
```

## R1 disposition

`DOCV2-R8-01` is fixed: the continuity checker derives run/workflow/lane/path/base/current-step identity from canonical state and no longer hard-codes the motivating incident. The audit now scans the continuity checker too. Portable/runtime/continuity checks pass and source worktrees remain unchanged.

## Finding DOCV2-R8-02 — HIGH — current step is not fully idempotency-addressable

`WORKFLOW_CONTINUITY.md` defines a material step contract containing `INPUT_IDENTITY`, `IDEMPOTENCY_KEY`, `DONE_WHEN`, `OUTPUT_IDENTITY` and `REPLAY_POLICY`, but the migrated live run record on `lane/implement-p00` only has a compact table with state/output prose/replay policy. The generic checker validates run-level identity but does not require a machine-readable current-step contract.

If interruption occurs after S06 creates a package but before COMPLETE is persisted, a fresh chat still lacks an exact current-step idempotency key and done-when/output probe contract. This can reintroduce the duplicate-work failure R8 is intended to eliminate.

Required correction:
- add a structured `CURRENT_STEP_RECORD` to the live run ledger with exact `STEP_ID`, `STATE`, `INPUT_IDENTITY`, `IDEMPOTENCY_KEY`, `DONE_WHEN`, `OUTPUT_IDENTITY`, `REPLAY_POLICY`;
- checker must require those fields, ensure STEP_ID equals canonical current step, validate allowed state/replay values, and reject a missing idempotency/done-when contract;
- migration snapshot/main may remain immutable history, but the owning lane live record is the mutable current-step authority;
- before executing a duplicate-prone step, transition the current-step record to INTENT; after verified output, COMPLETE with exact output identity.

## Verdict

FAIL. Return to DOC-DESIGN. DOC-AUDIT remains blocked until the revised exact candidate passes detailed review.
