# LEARNING-ADVERSARIAL-STATE-INDEPENDENCE-004

```yaml
LEARNING_ID: LEARNING-ADVERSARIAL-STATE-INDEPENDENCE-004
SCORE: 10
SOURCE: HEALTH_REVIEW-DOCSYS-R9-V36-005
CATEGORY: DOCUMENTATION_GOVERNANCE_TESTING
DISCOVERED_IN: DOCSYS-V2-R9 / V36 candidate
ACTIVATION_TARGET: DOCSYS-V2-R9
STATUS: CANDIDATE_PENDING_R4_A4
```

## Observation

An adversarial regression is not state-independent merely because it normalizes promotion verdict files. Each negative test must construct every semantic precondition required for the invariant it intends to violate. Otherwise a valid evolution of the live register can make the mutation a no-op and turn the regression harness into the failing component.

At V36 the live register legitimately reached zero pending effectiveness measurements. The `overdue_measurement_drift` test still assumed one existed, so increasing `STATE_VERSION` did not create an overdue item and the checker correctly passed.

## General rule

Adversarial lifecycle fixtures must be **self-contained semantic worlds**:

1. normalize any ambient evidence that affects the invariant;
2. create the minimum valid preconditions for the target invariant;
3. introduce exactly one intentional inconsistency;
4. assert the checker rejects that inconsistency by a stable semantic error class; and
5. remain valid when the live repository has zero, one or many records in the relevant lifecycle state.

## Required correction

`overdue_measurement_drift` must choose an active learning, set it to `PENDING_MEASUREMENT`, supply a due `STATE_VERSION_AT_LEAST` gate, clear effectiveness evidence, set the canonical pending-measurement aggregate to the matching value, and deliberately keep the overdue aggregate incorrect. It must not rely on any ambient pending record.

Future adversarial cases should follow the same pattern instead of mutating only one field and assuming the surrounding repository already provides the rest of the scenario.

## Success metric

The unchanged lifecycle checker plus the corrected adversarial suite must PASS on a canonical state with zero ambient pending measurements while the synthesized overdue fixture is still rejected as `learning-overdue-measurement-drift`. A later effectiveness measurement must also show the suite remains stable across subsequent canonical lifecycle-state changes.

This learning changes regression-fixture construction only. It does not alter lifecycle policy, checker acceptance predicates, product code or native execution authority.