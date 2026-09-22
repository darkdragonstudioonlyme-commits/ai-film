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

## 11. Persistence of test governance

Immutable records live under `test-governance/`:

```text
TEST_CHANGE-*  material oracle/harness change proposal
TEST_REVIEW-*  independent disposition of that change
TEST_GAP-*     explicit missing capability/risk
```

`TEST_CHANGE` includes `ORACLE_CHANGED`, upstream authority, changed test IDs/scripts, before/after behavior, migration impact and review status. A changed expected outcome without a recorded authority/review is not durable test policy.

### Canonical review provenance

Every `TEST_REVIEW` must resolve the exact `TEST_CHANGE_ID` or `TEST_GAP_ID` it disposes. Preferred form: the proposal/gap exists byte-identically in the same canonical tree. If it must remain lane-local, the review must record an immutable commit/ref plus content digest so a cold-start reviewer can retrieve the exact proposal without relying on conversation memory or a mutable branch tip.

A producer-lane proposal that is independently reviewed and then used as canonical gate evidence must be canonicalized before the gate is treated as durable. A review whose proposal cannot be resolved is `TEST_GOVERNANCE_PROVENANCE_MISSING`; its PASS label alone is not sufficient authority.

## 12. Constructibility before design/test handoff

A coverage list is not proof that a workflow can run. Before DESIGN_REVIEW or material TEST_REVIEW accepts a producer, reviewer and author must independently trace at least one positive multi-stage path and its interruption path from authorized input to consumable output. Record for every required value: producer, earliest knowable boundary, immutable identity, consumer, permitted late binding, issuer and verification rule. Include actual producer-to-consumer schema compatibility, not only enum counts.

Hash-addressed authority requires an explicit acyclic construction graph. List exactly which bytes each digest covers and excludes. Reject a manifest/partition digest embedded in an object whose own digest belongs to that manifest/partition; reject analogous plan/approval/proof self-reference. A plan may be authorized by a predeclared slot, but no static check may manufacture future observations. Exercise empty input, missing producer, wrong epoch/role/source, uncommitted output, conflict and interruption.

For stateful multi-stage designs also explain guard ownership, nested acquisition, write/verify publication and recovery after each persistence boundary. Cross-host transfer needs distinct source/export and destination/staging locators with byte equality; a local path equality rule cannot prove an external destination. Preserve acceptance requirements, containment and owner authorization.

The handoff must contain the witness or a concrete blocker. `COVERAGE_COMPLETE`, `SCHEMA_VALID`, `CONSTRUCTIBLE`, `IMPLEMENTED`, `NATIVE_VALIDATED` and `EFFECTIVE` are separate claims. Pure/synthetic constructibility tests prove only their stated model, never Windows/WSL execution or whole-system readiness.

## 13. Two-actor and transport tests

Keep business/test authority independent of either implementation model. Verify
non-author acceptance, exact task/knowledge/result binding, stale-input rejection,
duplicate dispatch, crash-before/after-output recovery, denied secrets/native actions,
permission escalation, missing account/budget and false provider success. Tool-less
reviews must not claim test execution. Queue/schema tests prove their predicates,
not actual Claude dispatch or protected WSL execution. Runtime qualification requires
the real installed version/profile and bounded smoke/interruption evidence.
## Executable conformance and test-oracle contract

Before implementation, freeze a small traceability map from each required behavior
to design/constraint, affected file or seam, positive test, negative/recovery test,
expected result and evidence class. Author and reviewer read that same map. Existing
business/failure contracts outrank both models. A test's expected rejection (for
example a denied actor) is a passing test when actually observed; product exit zero
is not the universal oracle. Unexecuted, skipped, stubbed or process-only checks must
not supply end-to-end coverage.

At each material code boundary compare the actual diff with the authorized file/seam
scope and confirm the producer/consumer trace is still constructible. An unanticipated
contract change, missing producer, circular hash, unsafe lock sequence, repeated test
escape or unexplained broad refactor triggers a scoped DESIGN_GAP/APPLICABILITY_HOLD.
Neither actor may adjust the oracle to preserve the patch. Group related discoveries
and invalidate only dependent work/reviews; preserve unrelated verified outputs.

Formal review covers the exact final tree, meaningful negatives and a deliberate
counterexample to each critical new guard. A pure model test is not proof the runtime
calls that guard. Implementation of the bridge must wire and integration-test these
checks before activation. Static text review can be useful but cannot close a command
or native execution obligation. Corrections to the collaboration policy stay distinct
from the later product-design and native-test gates.
