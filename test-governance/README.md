# Test Governance Records

Canonical immutable records for material test-policy/oracle changes and explicit test gaps.

Naming:

- `TEST_CHANGE-<scope>-<nnn>.md` — reviewed change to expected behavior/oracle or material harness semantics.
- `TEST_GAP-<scope>-<nnn>.md` — known missing test capability/coverage.
- `TEST_REVIEW-<scope>-<nnn>.md` — independent review of a TEST_CHANGE.

`TEST_CHANGE` that changes expected business behavior is not active until its upstream business/design authority and independent TEST_REVIEW are recorded. Infrastructure-only fixes must declare `ORACLE_CHANGED: false`. Every canonical `TEST_REVIEW` must resolve the exact proposal/gap it disposes from the same canonical tree or an explicit immutable commit/ref plus digest; an orphan PASS review is provenance debt.

Current active test strategy is `../TEST_STRATEGY.md`; this directory contains immutable records, not mutable policy.
