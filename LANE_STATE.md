# IMPLEMENT Lane State — Phase 00

```yaml
LANE_ID: IMPLEMENT-P00
LANE_ROLE: IMPLEMENT
STATUS: ACTIVE_NEXT_INCREMENT
GLOBAL_MODE: IMPLEMENTATION
GLOBAL_WORK_ITEM: IMPL-P00-001
REMOTE_BRANCH: lane/implement-p00
WSL_WORKTREE: /home/dragon/ai-film-dev/implement
LOCAL_SOURCE_BRANCH: impl/p00
CURRENT_SOURCE_COMMIT: 3da3ddc771c15d175a2c5045c86a7c1ff9987dbd
CURRENT_DELIVERY: 0.1.0.dev9
SOURCE_WRITABLE: true
REVIEW_WRITABLE: false

LAST_HANDOFF:
  CANDIDATE: IMPL-P00-001-DEV9
  REVIEW_DELTA_VERDICT: PASS
  FINDINGS_CLOSED: [CR-P00-002, CR-P00-003, CR-P00-004]
  FINDINGS_OPEN: [CR-P00-001]

NEXT_INCREMENT: "prior pre-C3/checkpoint provenance selection + nested cross-stage E00 semantics"
```

## Immediate implementation queue

1. Implement exact prior pre-C3/checkpoint provenance selection.
2. Complete reviewed nested cross-stage E00 field/source selection.
3. Add positive/negative tests for wrong host/plan/run/step/target/checkpoint, tampering, ambiguity, staleness and provenance incompleteness.
4. Run targeted + full author regression/static checks.
5. Commit/package exact next candidate and hand it to REVIEW lane by immutable identity.

IMPLEMENT may not issue review verdicts. CR-P00-001 remains the umbrella blocker until full author-complete scope exists.
