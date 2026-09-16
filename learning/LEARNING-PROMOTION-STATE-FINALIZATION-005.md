# LEARNING-PROMOTION-STATE-FINALIZATION-005

```yaml
LEARNING_ID: LEARNING-PROMOTION-STATE-FINALIZATION-005
SCORE: 10
OBSERVED_AT_STATE: V37
TARGET_RELEASE: DOCSYS-V2-R9
CLASS: lifecycle-state-finalization
```

## Observation

The V37 exact lifecycle checker failed before review because `LEARNING-ADVERSARIAL-STATE-INDEPENDENCE-004` still carried the transition-only state `ACTIVE_ON_PROMOTION / PASS_ON_FINAL_REVIEW` from the already completed V36 R4/A4 promotion. When V37 predeclared a new R5/A5 promotion contract, the historical promotion-only record no longer matched `PROJECT_STATE` final-review/final-audit fields.

This was not a checker defect. The current lifecycle state had not finalized a transient promotion state into durable `ACTIVE / PASS` after the prior verdict pair and post-promotion CI succeeded.

## Generalized learning

`ACTIVE_ON_PROMOTION` is a transition state, not a durable cross-release state. Before a later canonical promotion contract replaces `FINAL_REVIEW_* / FINAL_AUDIT_*`, every prior successfully promoted learning must be normalized to durable `ACTIVE / PASS` while preserving its immutable activation evidence.

The normalization must happen in a reviewed/audited canonical state transition. Automation may detect the stale transition state but may not silently self-promote or rewrite lifecycle evidence.

## Success metric

Across later canonical promotion boundaries, no learning from a completed prior promotion remains dependent on the new promotion's final-review/final-audit fields. Exact lifecycle/adversarial suites remain PASS before and after promotion, and transient promotion state is finalized without deleting immutable evidence.

## Measurement

Measure after subsequent promotion-state transitions, with a structured effectiveness gate at state version 39. A recurrence makes this learning ineffective and requires another explicit successor/meta-review path.