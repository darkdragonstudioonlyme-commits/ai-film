# MEASUREMENT-LEARNING-CONTROL-001-001

```yaml
LEARNING_ID: LEARNING-CONTROL-001
METRIC_ID: CONTROL_SCHEMA_SEMANTIC_GENERALITY_V1
METRIC_VERSION: 1
SUCCESS_METRIC_SHA256: 1732750a2caab873b339de2981886628c31c80ec27ff9de054514e65a45d7df8
SCOPE: "V41 documentation-governance state/checker schema evolution after R11/A11 promotion"
SAMPLE_REQUIREMENT: "one qualifying state/checker schema-evolution event with an independently reviewable semantic-invariant change"
OBSERVATIONS: "Commit 0d106cbad7e144b737cb43eb17409339d107021d changed the checker because a new semantic invariant was required: current prose verdict authority must agree with canonical final review/audit IDs while explicit historical references remain allowed. The detector failed closed on stale authority during earlier design attempts, then GitHub Actions run 35223256888 / job 105208358932 passed lifecycle, adversarial lifecycle, governance, active-doc consistency, workflow continuity and holistic audit with existing runtime/lane/artifact drift predicates retained."
EXPECTED_PREDICATE: "A qualifying state/checker schema evolution changes checker logic only when a semantic invariant changes, preserves semantic derivation from current state rather than snapshot-specific pins, and retains fail-closed runtime/lane/artifact drift checks."
MEASUREMENT_COMMIT: 0d106cbad7e144b737cb43eb17409339d107021d
RESULT: PASS
REVIEW_ID: DOC-V2-R9-REVIEW-012
```

## Immutable success metric

Future state schema evolution does not require checker edits unless a semantic invariant changes; true lane/worktree/artifact drift still fails closed.

## Evidence identities

- `workflow-health/HEALTH_REVIEW-DOCSYS-R9-V41-AUTHORITY-015.md`
- GitHub Actions run `35223256888`, job `105208358932`, exact measurement commit `0d106cbad7e144b737cb43eb17409339d107021d`
- failed detector-refinement runs `35223022725` and `35223154818` are negative evidence that the new authority invariant failed closed before historical-context wording/rules were made precise

## Review boundary

This receipt is candidate semantic evidence, not self-authorization. R12/A12 must independently verify that the schema/checker change was semantically warranted, that the observed negative/positive CI sequence satisfies the immutable metric, and that existing runtime/lane/artifact drift predicates were not weakened. The lifecycle checker verifies binding and structure only.
