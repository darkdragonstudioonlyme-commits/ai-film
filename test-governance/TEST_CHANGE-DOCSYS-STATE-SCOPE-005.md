# Documentation state / continuity guard correction

TEST_CHANGE_ID: TEST_CHANGE-DOCSYS-STATE-SCOPE-005
ORACLE_CHANGED: false
CLASSIFICATION: INFRASTRUCTURE_ONLY
UPSTREAM_AUTHORITY: POL-STATE-001; POL-CONTINUITY-001; POL-TEST-001
DESIGN_RECORD: docs/DOCUMENTATION_SYSTEM_R9_V61_DESIGN_OPTIMIZATION.md
REVIEW_RECORD: test-governance/TEST_REVIEW-DOCSYS-STATE-SCOPE-005.md
PRODUCT_ORACLE_CHANGED: false

## Before / after

The existing contract selects current state explicitly and forbids calling unavailable evidence PASS. Two checkers instead selected the highest filename; continuity also silently skipped remote verification. Corrections implement existing authority, not a new product oracle. COMPLETE output must be non-empty; event counters and sample requirements reject booleans/invalid counts and an EFFECTIVE claim below its declared sample requirement.

## Tests and limits

`tools/test_state_contract.py` supplies independent minimal files and local disposable Git fixtures, not production source/environment assumptions. It covers 23 selection/scope/remote-ledger negative and positive cases. `tools/test_continuity_measurements.py` retains its original 12 cases and adds 4 invalid-counter/sample-claim cases. Neither fixture asserts that a schema-valid event is real runtime evidence.

The existing test strategy and downstream contracts are unchanged. No native host/model test is executed, replaced, waived or marked PASS. CI must run the state selector, these adversarial tests and strict remote continuity. Review resolves this proposal exactly before canonical gate use.
