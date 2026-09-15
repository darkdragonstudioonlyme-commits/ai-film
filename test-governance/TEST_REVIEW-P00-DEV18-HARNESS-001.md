# TEST_REVIEW-P00-DEV18-HARNESS-001

```yaml
TEST_REVIEW_ID: TEST_REVIEW-P00-DEV18-HARNESS-001
TARGET_TEST_CHANGE: TEST_CHANGE-P00-DEV18-HARNESS-001
TARGET_CANDIDATE: IMPL-P00-001-DEV18
TARGET_SOURCE_COMMIT: f680067c2f23d7eea4c016247015359ffe431971
ORACLE_CHANGED_DECLARATION: false
VERDICT: FAIL
SOURCE_MODIFIED_DURING_REVIEW: false
FINDING: CR-P00-014
```

## What passed

The business/native acceptance oracle was not intentionally weakened. CR-P00-013 continuity/window/route-binding negative tests exercise stricter provenance and independently reproduce the intended failures.

## Why the test change fails governance

The dev18 helper `collector()` adds `contract_digest` to the synthetic `collector_release`, but the existing production proof path and pre-dev18 collector-release fixtures define only reviewed/withdrawn state plus `build_digest`. No reviewed producer/schema for `collector_release.contract_digest` was found.

This is exactly the class prohibited by `TEST_STRATEGY.md`: a test fixture was adapted to current implementation structure instead of verifying compatibility with the existing authority model. The green unit test therefore cannot approve CR-P00-012.

## Required next test change

A new candidate must use production-shaped collector-release fixtures and test contract binding at the suite/evidence record boundary. If an authority schema change is needed, route through DESIGN_GAP before updating tests or implementation.
