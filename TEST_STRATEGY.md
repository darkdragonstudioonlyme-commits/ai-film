# AI-FILM-SERVER — Business-First Test Strategy

## 1. Test authority

Tests exist to evaluate reviewed business/system behavior, not to preserve current implementation behavior.

Authority order:

1. approved requirements / Blueprint / frozen decisions;
2. reviewed phase design + acceptance/failure contracts;
3. explicitly approved business/design change;
4. test strategy and traceability derived from those sources;
5. implementation code last — code is the subject under test, never the oracle authority.

A failing test does **not** justify changing the test to match code. Change the expected behavior only when upstream reviewed business/design authority changed or independent evidence proves the test itself is defective.

## 2. Test-change decision table

| Situation | Default suspect | Allowed action |
|---|---|---|
| code change breaks unchanged reviewed behavior | code | fix code; keep oracle |
| approved business/design behavior changed | test + code may both change | update requirement/design first, then test oracle, then implementation |
| harness/parser/test infrastructure bug | test infrastructure | fix script without weakening business assertion; independent review required |
| flaky/non-deterministic test | harness/environment | isolate source of nondeterminism; never hide with retries alone |
| environment changed | environment/profile | update environment snapshot/applicability, not expected business result |
| test impossible to execute | workflow/test architecture | create TEST_GAP / WORKFLOW_REVIEW; do not mark PASS |

## 3. Test workflow

```text
BUSINESS/CONTRACT SOURCE
→ TEST DESIGN (behavior, preconditions, oracle, failure modes)
→ TEST REVIEW (independent of implementation author)
→ TEST SCRIPT / HARNESS
→ HARNESS SELF-TESTS
→ EXECUTE AGAINST CANDIDATE
→ RESULT + EVIDENCE
```

For material test-oracle changes, the person/lane changing production code must not be the only reviewer of the oracle change.

## 4. Required test case anatomy

Every material case defines:

```yaml
TEST_ID:
BUSINESS_SOURCE:
PURPOSE:
PRECONDITIONS:
INPUT_PROFILE:
ACTION:
EXPECTED_BEHAVIOR:
FAILURE_ORACLE:
EVIDENCE_REQUIRED:
ENVIRONMENT_REQUIREMENTS:
NON_GOALS:
IMPLEMENTATION_INDEPENDENCE:
```

`IMPLEMENTATION_INDEPENDENCE` explains why the oracle does not merely assert current internal structure.

## 5. Test layers

- **Contract/schema tests** — input/output and frozen behavior.
- **Pure policy/unit tests** — deterministic predicates and transforms.
- **Integration tests** — production composition seams with explicit lower ports, not fake production backends.
- **Failure/recovery tests** — causal fault, interruption, retry, resume, rollback, uncertainty.
- **Security/trust tests** — wrong actor/build/contract/ref/tamper/replay.
- **Concurrency/resource tests** — contention, limits, exhaustion, bounded persistence.
- **Native/LAB/SITE validation** — actual environment proof; never substituted by author tests.
- **Model-evaluation tests** — governed separately by `MODEL_EVALUATION.md` and exact server environment snapshots.

## 6. Test script rules

1. Test script version and digest belong to evidence.
2. Test runners must fail closed on malformed output, missing evidence, skipped mandatory cases, stale environment or wrong candidate identity.
3. `--list`, inventory presence, process exit, fixture labels and PASS-shaped envelopes are not execution proof.
4. Scripts may normalize transport/tool differences, but cannot normalize away business failures.
5. Retry is diagnostic unless the business contract explicitly permits retry semantics.
6. Generated evidence should stay outside source or be restored after test runs so verification does not dirty the candidate.
7. Any script change that changes expected behavior requires a documented `TEST_CHANGE` record and independent review.

## 7. Test debt and gaps

A missing test is represented explicitly:

```yaml
TEST_GAP_ID:
BUSINESS_RISK:
MISSING_CAPABILITY:
WHY_BLOCKED:
TEMPORARY_COVERAGE:
OWNER_WORKFLOW:
EXIT_CONDITION:
```

Do not delete a requirement from coverage to make the suite green.

## 8. Regression and mutation discipline

For critical policy/security/recovery code, add negative tests that would fail if the protection were removed. Where practical, review uses adversarial scenarios or mutation-style reasoning to demonstrate the test can detect the defect it claims to cover.

## 9. Test philosophy review trigger

Route to `WORKFLOW_HEALTH.md` when tests repeatedly need expectation edits after code changes, flaky retries grow, failures move between scripts without root cause, or the suite passes while review repeatedly finds the same class of defect. That pattern indicates test architecture debt, not just more code bugs.

## 10. Traceability requirement for changed tests

Every added/changed material test must be traceable to one of:

- a reviewed business/acceptance/failure contract reference;
- an existing reviewed requirement already mapped in project traceability;
- an explicitly `INFRASTRUCTURE_ONLY` harness correction that proves expected business behavior did not change.

A candidate that changes expected outcomes without one of these routes has `TEST_AUTHORITY_MISSING` and is not review-ready.
