# MEASUREMENT-LEARNING-AUTHORITY-REFERENCE-CONSISTENCY-008-001

```yaml
LEARNING_ID: LEARNING-AUTHORITY-REFERENCE-CONSISTENCY-008
METRIC_ID: CURRENT_VERDICT_AUTHORITY_SEMANTICS_V1
METRIC_VERSION: 1
SUCCESS_METRIC_SHA256: 278e7f8f0dfc2d5aca285d9e71150412e0929cf2503b039ca180b02cef640322
SCOPE: "V42 documentation revision after historical V41 R12/A12 promotion"
SAMPLE_REQUIREMENT: "one subsequent documentation revision selecting a new prospective verdict pair while retaining older verdict references only as explicit historical context, with persistent stale-live and historical-reference adversarial cases"
OBSERVATIONS: "Measurement commit 2beb094a2d2e60e5b08eed221977772e1ae87e6b selected prospective R13/A13 from canonical governance, while every R12/A12 reference on current authority surfaces is explicitly historical/prior-tree context. GitHub Actions run 35272505044 / job 105375038565 passed DOCS_CHECK_PASS for 20 active files and ADVERSARIAL_PROJECT_DOCS_TEST_PASS for baseline, stale_live_authority rejection, explicit_historical_authority acceptance and governance_parity_drift rejection. The V42 checkpoint and active design remain readable about historical R12/A12 without assigning them current authority."
EXPECTED_PREDICATE: "Current review/audit authority is derived from canonical final verdict IDs; stale/superseded verdict pairs cannot appear as live authority on current state/checkpoint/design surfaces, while explicitly historical references remain accepted and readable."
MEASUREMENT_COMMIT: 2beb094a2d2e60e5b08eed221977772e1ae87e6b
RESULT: PASS
REVIEW_ID: DOC-V2-R9-REVIEW-013
```

## Immutable success metric

Future documentation revisions derive current review/audit authority from canonical governance; superseded verdict pairs cannot appear as live authority in the current state, checkpoint, or active design record, while explicitly historical references remain readable.

## Evidence identities

- `workflow-health/HEALTH_REVIEW-DOCSYS-R9-V42-VALIDATION-016.md`
- `AI_FILM_STATE_CHECKPOINT_V42.md`
- `docs/DOCUMENTATION_SYSTEM_R9_V42_VALIDATION_RECONCILIATION.md`
- GitHub Actions run `35272505044`, job `105375038565`, exact measurement commit `2beb094a2d2e60e5b08eed221977772e1ae87e6b`

## Review boundary

This receipt is candidate semantic evidence, not self-authorization. R13/A13 must verify the current-vs-historical classification on the exact V42 tree and confirm that the adversarial detector remains neither overly permissive nor overly restrictive.
