# HEALTH_REVIEW-DOCSYS-R9-V41-CI-013

```yaml
HEALTH_REVIEW_ID: DOCSYS-R9-V41-CI-013
TRIGGER: "GitHub Actions run 35218316047 failed the adversarial lifecycle suite on exact design SHA 57296ccf4dc726a5dd58a28d6c0a02d1c41d4e20"
WORKFLOW: DOCSYS-V2-R9
STATE_BEFORE: "Learning 004 classified EFFECTIVE; local 16-case suite PASS"
HEALTH_STATE: META_REVIEW_REQUIRED
ROOT_CAUSE_CLASS: TEST_FIXTURE_AMBIENT_ENVIRONMENT
LEARNING_IDS: [LEARNING-ADVERSARIAL-STATE-INDEPENDENCE-004, LEARNING-EVIDENCE-SEMANTICS-007]
RETURN_TO: "forensic design branch before R10"
RESULT: CORRECTION_AUTHORED_REVIEW_PENDING
```

## Failure evidence

GitHub Actions job `105192004580` inherited `GITHUB_REF_NAME=lane/docs-v2-r9-v41-forensic-design`. The adversarial test harness copied the repository into a temporary directory but inherited that environment variable. The lifecycle checker therefore correctly identified the copied fixture as DESIGN role. `partial_promotion_verdict` added only the review artifact and expected generic copied-tree failure `partial-promotion-verdict-set`, but the checker returned the equally valid stage-specific error `design-stage-has-verdict-artifact`.

Local execution did not expose the defect because no `GITHUB_REF_NAME` was present. The fixture therefore did not construct a self-contained semantic world across environments.

## Learning disposition

This is a recurrence of the immutable success metric for `LEARNING-ADVERSARIAL-STATE-INDEPENDENCE-004`: adversarial fixtures were not fully independent of ambient state. Learning 004 is reclassified `INEFFECTIVE`; successor `LEARNING-EVIDENCE-SEMANTICS-007` absorbs branch-role/environment isolation together with semantic evidence binding.

## Correction

The adversarial runner now removes GitHub branch-role environment variables and any inherited `AIFILM_DOCSYS_ROLE` before generic copied-tree cases. Explicit DESIGN/REVIEW/AUDIT positive cases inject only the role they intend to test. The same suite must pass locally and on GitHub Actions before R10 review.

No product/native state changes.
