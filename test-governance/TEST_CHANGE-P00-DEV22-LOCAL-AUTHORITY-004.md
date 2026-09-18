# TEST_CHANGE-P00-DEV22-LOCAL-AUTHORITY-004

```yaml
TEST_CHANGE_ID: TEST_CHANGE-P00-DEV22-LOCAL-AUTHORITY-004
TARGET_CANDIDATE: IMPL-P00-001-DEV22
BASE_SOURCE_COMMIT: 934659f535d81d9a4a07389531acc2b9c304fa6d
TARGET_SOURCE_COMMIT: 86bb64938a136e3f8d6cfd0266685a01cb832b77
REMOTE_SOURCE_REF: source/p00-dev22-local-authority-exact
TARGET_PACKAGE_SHA256: c2ea52087039f4c7b98c53a7cc0eaf1a4a0f931645f86491bf2eb8ef12956aae
TARGET_WHEEL_SHA256: e5a7ae51c73e5e9bea1e9d62c2220d2f39133a2bd74f73ccf97c38d75019147f
SOURCE_DIGEST: 69fdc1840472a96bce8f8841e4d780543827e3cefdd3fe3bc8445f8a1fb4a0d6
TEST_DIGEST: 47d4ae767b26b05ef16d6809ea9377ef4e1b21bfbc4c44093dbd1cc158b75698
CONTRACT_DIGEST: f259656c48ed24c15bd48da2bb040950ed94d8edcf1473cf6456b96578c933ee
CHANGE_CLASS: MATERIAL_AUTHORITY_MODEL_CHANGE
ORACLE_CHANGED: true
EXPECTED_BUSINESS_BEHAVIOR_CHANGED: true
UPSTREAM_AUTHORITY:
  - docs/PHASE00_LOCAL_OPERATOR_LAB_AUTHORITY_CHANGE.md
  - owner decision: local-only WSL execution / Choice B
CHANGED_TESTS:
  - tests/test_core.py::AuthorityTests
  - tests/test_dev15_harness.py::LocalControllerFixtureTests
TEST_REVIEW_STATUS: PENDING
STATUS: PENDING_INDEPENDENT_REVIEW
```

## Requirement change

The owner selects an explicitly lower-assurance local authority model so LAB authorization can be prepared and signed inside the same WSL/Windows trust domain. The product must no longer require an external controller as a condition of LAB containment. `controller_external=false` becomes a valid, truthful local-controller mode and must never be represented as independent/external provenance.

The existing external-controller mode remains valid. Both modes retain the exact same mandatory containment barriers: disposable LAB, no real credentials, and no production mappings. Fixture authority mode must match registration authority mode.

## Oracle delta

Before dev22, a LAB registration with `controller_external=false` fails `LAB_REGISTRATION_INCOMPLETE` because the implementation requires all four LAB flags to be true.

After dev22:

- `controller_external=false` is accepted for LAB when the other containment predicates are true;
- `controller_external=true` remains accepted;
- missing/non-boolean controller mode fails `LAB_CONTROLLER_MODE`;
- local-controller mode does not relax `disposable`, `no_real_credentials`, or `no_production_mappings`;
- a fixture whose `controller_external` value differs from its registration fails `LAB_FIXTURE_CONTROLLER_MODE`.

No qualification, SITE, HOST_READY, exact build/test/contract binding, plan authorization, <=24h window, role pin, content-addressing, host/operator scope, or native evidence oracle is weakened.

## Author evidence

- targeted local/external controller regression: 7/7 PASS;
- full workspace regression: 766 PASS / 0 failure / 0 error / 0 skip;
- static checks: 101 PASS / 0 failed;
- fresh wheel install: `0.1.0.dev22`, contract digest unchanged;
- wheel module-byte verification: 58/58 PASS;
- package exact-source verification: 284 tracked source files + manifest, 0 hash errors;
- native Windows/WSL acceptance remains NOT_RUN.

Independent TEST_REVIEW must verify that the new acceptance is exactly the owner-authorized local-controller behavior and that the negative tests still enforce containment and registration/fixture mode consistency. It must not infer native PASS from workspace regression.
