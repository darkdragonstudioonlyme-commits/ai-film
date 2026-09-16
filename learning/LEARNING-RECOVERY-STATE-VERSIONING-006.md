# LEARNING-RECOVERY-STATE-VERSIONING-006

```yaml
LEARNING_ID: LEARNING-RECOVERY-STATE-VERSIONING-006
SCORE: 9
STATUS: REVIEW_GATED
ACTIVATION_TARGET: DOCSYS-V2-R9
REVIEW_ID: DOC-V2-R9-REVIEW-007
AUDIT_ID: DOC-V2-R9-AUDIT-007
EFFECTIVENESS_GATE: STATE_VERSION_AT_LEAST_41
```

## Observation

Two recovery-state versioning failures were exposed during the long-horizon production-like readiness program.

First, a stricter full-DR rehearsal was deployed before the rotating recovery payload had been regenerated with the expanded control schema. The new rehearsal correctly rejected the old export because the newly required control files/timers were absent. The safe response was not to weaken the rehearsal; it was to migrate producers in order: create the new control backup, mirror it, rebuild the transfer export, then rerun the stricter rehearsal.

Second, a private off-host metadata document pinned the checksum of a rotating export/control backup. Scheduled backups legitimately changed that checksum, making the off-host metadata stale even though runtime health was good. The correct model is to pin stable exact-candidate/rebuild identities off-host and leave rotating control/export hashes under host-side freshness/integrity verification until the binary payload itself can be transferred and verified off-host.

## Generalized rule

Recovery control state has both **stable identity** and **rotating operational state**. Stable identities may be pinned across hosts. Rotating state must use freshness/versioned producer-consumer migration and must not be presented as immutable off-host identity.

When a recovery consumer becomes stricter because the control schema expands, update the producer chain before expecting the new consumer to pass:

`health/integrity -> control backup -> mirror -> transfer export -> full DR rehearsal -> negative campaign -> health`.

A failure caused by old-schema recovery payload is evidence that the migration is incomplete, not a reason to remove the new required check.

## Success metric

Future recovery/control-plane schema changes complete producer migration before stricter consumer success is claimed; no verifier/rehearsal requirement is weakened to accept an old-schema payload; and off-host metadata does not pin rotating state as if it were stable identity.

## Measurement

Measure after at least two later canonical state transitions or the next recovery-schema/off-host-metadata change, whichever comes first. Evidence must include a successful migration or a clean no-drift review under the generalized rule. V39 activation alone is not effectiveness evidence.
