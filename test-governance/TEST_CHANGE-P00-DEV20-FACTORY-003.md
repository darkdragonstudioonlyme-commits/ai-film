# TEST_CHANGE-P00-DEV20-FACTORY-003

```yaml
TEST_CHANGE_ID: TEST_CHANGE-P00-DEV20-FACTORY-003
TARGET_CANDIDATE: IMPL-P00-001-DEV20
TARGET_SOURCE_COMMIT: 51c9d3f7373a2922c1ea6a3e973d817bb4e16523
TARGET_PACKAGE_SHA256: 8104985b355815d58fbc28fec3e1b9b17c72dbf9d5a9c6dc8f7eb66f77a67fff
CHANGE_CLASS: INFRASTRUCTURE_ONLY_INTEGRATION_COVERAGE
ORACLE_CHANGED: false
EXPECTED_BUSINESS_BEHAVIOR_CHANGED: false
UPSTREAM_AUTHORITY:
  - contracts/PHASE00_INFRA_DESIGN_V2.md
  - contracts/PHASE00_ACCEPTANCE_MATRIX_V2.md
  - TEST_STRATEGY.md integration-test production-composition rule
TEST_FILE: tests/test_dev20_factory_integration.py
TEST_REVIEW_STATUS: PENDING
STATUS: PENDING_INDEPENDENT_REVIEW
```

## Why this test was added

The residual CR-P00-001 completeness audit found an author-coverage gap rather than a production-behavior gap: production request entry and the production native factory had been exercised separately, so author regression did not prove their real composition seam end-to-end.

Dev20 adds one integration test that calls the real `prepare_execution()` request entry and requires it to return the real `SessionRunner` composed with the real `NativeDriver` and real `Coordinator` for apply, verify, support-bundle and reconciliation purposes. Only lower OS/authority constructors are patched to deterministic synthetic ports.

## Oracle preservation

No expected business result, reviewed FD/D00 behavior, native acceptance criterion, error mapping, qualification rule or HOST_READY rule changes. The new assertions check production composition identity and lower-port wiring; they do not redefine success behavior and do not convert any native `NOT_RUN` case to PASS.

## Author evidence

- full workspace regression: 760 PASS / 0 failure / 0 error / 0 skip;
- static checks: 101 PASS / 0 failed;
- source digest: `1aa44211cd215b9c9691209d132a723c3b666fb5fee279b68c7f077da632d9dc`;
- test digest: `c645f3d9f88fcb716f78fcff9cd9b4144b320dc4f0c8c7082346a5cfbe6d9383`.

Independent TEST_REVIEW must verify that this remains infrastructure-only coverage and does not encode implementation-specific behavior as a new business oracle before the dev20 candidate is handed to formal CODE_REVIEW.
