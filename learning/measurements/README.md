# Learning Effectiveness Measurement Receipts

Immutable semantic measurement receipts live here when a learning moves toward `EFFECTIVE` or `INEFFECTIVE` based on a success metric that requires explicit scope/sample/predicate proof.

A receipt does not own lifecycle state. `learning/LEARNING_STATE.json` remains the current lifecycle owner; this directory owns evidence explaining **why** the effectiveness conclusion is justified.

Minimum fields:

```yaml
LEARNING_ID:
METRIC_ID:
METRIC_VERSION:
SUCCESS_METRIC_SHA256:
SCOPE:
SAMPLE_REQUIREMENT:
OBSERVATIONS:
EXPECTED_PREDICATE:
RESULT: PASS|FAIL
EVIDENCE_IDENTITIES:
MEASUREMENT_COMMIT:
REVIEW_ID:
```

Evidence path existence alone is not sufficient. The receipt must show that the observations satisfy or fail the declared predicate at the required scope/sample size. When current tooling cannot machine-evaluate the metric, independent review is required and the limitation remains visible as semantic-evidence debt.
