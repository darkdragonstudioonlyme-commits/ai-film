# Documentation System V2 R8 — Detailed Review R3

```yaml
REVIEW_ID: DOC-V2-R8-REVIEW-001-R3
REVIEW_LANE: lane/docs-v2-r8-review
TARGET_COMMIT: 71b7a7c0b9715d776bce1cfad767edcb9176a76c
SOURCE_IMPLEMENTATION_MODIFIED: false
VERDICT: FAIL
```

## Prior findings

- `DOCV2-R8-01` closed: run/workflow identity is state-derived rather than incident-hard-coded.
- `DOCV2-R8-02` closed for the current incident: the live IMPLEMENT run contains a machine-readable current-step contract with input identity, idempotency SHA-256, done-when probe, output identity and replay policy; the checker verifies the key/JSON/state semantics.

## Finding DOCV2-R8-03 — HIGH — continuity checker still hard-codes the IMPLEMENT worktree

`tools/check_workflow_continuity.py` fetches the owning branch from the state-derived run locator, but local output reconciliation is still guarded by `(WS/'implement').is_dir()` and reads HEAD from `WS/'implement'`. Therefore a future active DOC-DESIGN, TEST, REVIEW, MODEL-EVAL or other lane can have a valid state-derived RUN_ID yet be reconciled against the wrong local worktree.

Required correction:
- canonical active-run state must declare a safe relative local worktree identity (or explicitly declare no local worktree);
- continuity checker derives the worktree from that field and rejects traversal/absolute paths;
- no generic continuity code may contain an IMPLEMENT-only local-worktree assumption;
- add audit coverage against hard-coded `WS/'implement'`/equivalent in the generic continuity checker;
- current dev20 run must still resolve to `implement` and remain producer-only, with no product gate promotion.

## Verdict

FAIL. Return to DOC-DESIGN. Holistic DOC-AUDIT remains blocked until a revised exact candidate passes detailed review.
