# TEST_CHANGE-P00-DEV18-HARNESS-001

```yaml
TEST_CHANGE_ID: TEST_CHANGE-P00-DEV18-HARNESS-001
TARGET_CANDIDATE: IMPL-P00-001-DEV18
TARGET_SOURCE_COMMIT: f680067c2f23d7eea4c016247015359ffe431971
CHANGE_CLASS: INFRASTRUCTURE_AND_HARNESS_CORRECTION
ORACLE_CHANGED: false
EXPECTED_BUSINESS_BEHAVIOR_CHANGED: false
UPSTREAM_AUTHORITY:
  - "CR-P00-012 independent review finding: collector build/contract provenance must match authorizing suite"
  - "CR-P00-013 independent review finding: causal preparation/controller trace must be bound to exact production stage windows"
  - "Existing reviewed 86-case harness requirement: causal controller procedures and exact outcome/evidence oracles"
CHANGED_TEST_FILE: tests/test_dev15_harness.py
CHANGED_HARNESS_FILES:
  - src/aifilm_p00/native/harness_cases.py
  - src/aifilm_p00/native/harness_controller.py
  - config/required-native-test-inventory.json
TEST_REVIEW_STATUS: PENDING
STATUS: FIXED_PENDING_REVIEW
```

## Why this is not an oracle change

The reviewed product/business acceptance is unchanged. The harness is made stricter so evidence must prove the reviewed behavior instead of allowing weaker provenance or caller-selected controller mappings. No expected native PASS/FAIL outcome is changed to match implementation code.

## New/extended negative coverage

- wrong collector build/contract is rejected;
- arranged condition expiring before stage end is rejected;
- controller temporal relation not covering the bound stage window is rejected;
- a correct controller action cannot be rebound by result evidence to a different route index;
- all 86 inventory rows must mirror exact procedure-owned `controller_stage_indices` and procedure digests;
- T07-H must include CREATE invocation before reconciliation.

## Review requirement

Independent REVIEW must confirm `ORACLE_CHANGED=false`, ensure the route-binding rule follows reviewed procedure intent rather than current implementation convenience, rerun the former failure scenarios, and persist `TEST_REVIEW-P00-DEV18-HARNESS-001.md` before this test change is considered reviewed governance.
