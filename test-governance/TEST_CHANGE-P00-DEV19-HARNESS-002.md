# TEST_CHANGE-P00-DEV19-HARNESS-002

```yaml
TEST_CHANGE_ID: TEST_CHANGE-P00-DEV19-HARNESS-002
TARGET_CANDIDATE: IMPL-P00-001-DEV19
TARGET_SOURCE_COMMIT: 2ac37acdd3f81d3b86d4ffb019689655110a80c2
SUPERSEDES_FAILED_CHANGE: TEST_CHANGE-P00-DEV18-HARNESS-001
CHANGE_CLASS: INFRASTRUCTURE_AND_AUTHORITY_FIXTURE_CORRECTION
ORACLE_CHANGED: false
EXPECTED_BUSINESS_BEHAVIOR_CHANGED: false
UPSTREAM_AUTHORITY:
  - contracts/PHASE00_INFRA_DESIGN_V2.md#D00-14
  - src/aifilm_p00/native/proofs.py existing reviewed authority split
  - reviews/CODE-REVIEW-P00-001_DEV18_DELTA.md CR-P00-012/014
TEST_REVIEW_STATUS: PENDING
STATUS: FIXED_PENDING_REVIEW
```

## Authority correction

The synthetic `collector_release` fixture returns to the production-shaped fields `withdrawn`, `review_verdict`, and `build_digest`. Contract authority is independently exercised through the exact LAB suite `contract_digest`, which must equal the approved contract digest before collector acceptance.

## Coverage

- production-shaped collector + valid suite contract passes;
- wrong collector build rejects;
- wrong suite contract rejects at the suite authority boundary;
- CR-P00-013 continuity/window/exact route-binding tests remain unchanged and passing.

Independent TEST_REVIEW must verify this fixture matches the production authority consumer/producer model and that no expected business behavior was changed to follow implementation.
