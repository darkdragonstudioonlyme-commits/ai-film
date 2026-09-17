# MEASUREMENT-LEARNING-RECOVERY-STATE-VERSIONING-006-001

```yaml
LEARNING_ID: LEARNING-RECOVERY-STATE-VERSIONING-006
METRIC_ID: RECOVERY_STATE_VERSIONING_V1
METRIC_VERSION: 1
SUCCESS_METRIC_SHA256: aa3e1d84ceee7011326b829f210796e5af0c0e67cd25cfafabf7c7d55189b974
SCOPE: "real post-V40 recovery/control-plane transition"
SAMPLE_REQUIREMENT: "V40 to V41 recovery-state transition with producer-first refresh and rotating-state change"
OBSERVATIONS: "V41 recovery health evidence shows producer-first regeneration before strict consumer success, no weakened recovery predicates, stable-vs-rotating identity separation, and exact candidate CI success."
EXPECTED_PREDICATE: "A real later recovery transition regenerates producers before stricter consumer success, does not weaken recovery predicates, and separates stable from rotating identity."
MEASUREMENT_COMMIT: 59b288a39470475acdc34a545f0edfa5b4303650
RESULT: PASS
REVIEW_ID: DOC-V2-R9-REVIEW-011
```

## Immutable success metric

Future recovery/control-plane schema changes complete producer migration before stricter consumer success is claimed; no verifier/rehearsal requirement is weakened to accept an old-schema payload; and off-host metadata does not pin rotating state as if it were stable identity.

## Observations

V41 recovery health evidence shows producer-first regeneration before strict consumer success, no weakened recovery predicates, stable-vs-rotating identity separation, and exact candidate CI success.

## Evidence identities

- `workflow-health/HEALTH_REVIEW-DOCSYS-R9-V41-RECOVERY-011.md`
- `AI_FILM_PROJECT_STATE_V40.json`
- `AI_FILM_PROJECT_STATE_V41.json`

## Review boundary

This receipt is candidate semantic evidence. R10/A10 must independently verify that the observations and evidence satisfy the immutable metric; the lifecycle checker only verifies metric identity, receipt structure and referenced repository evidence existence.
