# HEALTH_REVIEW-DOCSYS-R9-V36-005

```yaml
HEALTH_REVIEW_ID: HEALTH_REVIEW-DOCSYS-R9-V36-005
TRIGGER: "Exact V36 design run: lifecycle checker PASSed but adversarial lifecycle regression failed in overdue_measurement_drift after pending measurement count reached zero."
WORKFLOW: DOCSYS-V2-R9
HEALTH_STATE: META_REVIEW_REQUIRED
ROOT_CAUSE_CLASS: TOOLING_TEST_FIXTURE
LEARNING_IDS:
  - LEARNING-ADVERSARIAL-FIXTURE-ISOLATION-003
  - LEARNING-ADVERSARIAL-STATE-INDEPENDENCE-004
RETURN_TO: "Correct adversarial fixture on V36 design, rerun exact-target checks, then R4/A4; product run remains RUN-P00-VALIDATION-001/V02."
RESULT: "Previous fixture-isolation learning is reclassified ineffective; successor requires every negative test to construct its own preconditions independent of the live lifecycle register."
```

## Failure evidence

Exact design SHA `45d9d97b8db7c596236a5173e5d8f57efe234fc4` produced:

- `LEARNING_LIFECYCLE_CHECK_PASS` with pending measurement `0`;
- five earlier adversarial cases PASS;
- `overdue_measurement_drift` FAILed because its mutator only raised `STATE_VERSION` and assumed an ambient `PENDING_MEASUREMENT` record existed;
- the checker therefore correctly returned PASS for the unmodified zero-pending register, causing the regression harness itself to fail.

This is not a lifecycle-checker false negative and not a product/native failure. It is a recurrence of ambient-state coupling in adversarial fixtures under a new valid lifecycle state.

## Corrective rule

Every adversarial mutator must create the semantic preconditions for the invariant it is testing inside its temporary repository. `overdue_measurement_drift` must synthesize one active pending-measurement record with a due gate, reconcile the pending-count aggregate, and deliberately leave the overdue aggregate wrong. The expected checker failure must then be `learning-overdue-measurement-drift` regardless of whether the live register has zero, one or many pending measurements.

Because learning 003 was previously marked EFFECTIVE and this new valid state disproves full state independence, it is reclassified `INEFFECTIVE` with successor `LEARNING-ADVERSARIAL-STATE-INDEPENDENCE-004`. The successor may activate only through the same R4/A4 promotion boundary and remains pending effectiveness measurement after activation.