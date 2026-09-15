# AI-FILM-SERVER — Business-First Test Strategy

## Purpose

Testing exists to evaluate **approved business/system behavior**, not to mirror whatever the current implementation happens to do. Source code is the subject under test; it is never the authority for expected behavior.

## Test-basis precedence

Use this order when defining an oracle:

1. owner/business goal and phase exit criteria;
2. frozen decisions and approved design/public contracts;
3. acceptance matrix, failure/recovery plan and evidence requirements;
4. independently accepted review findings / validation failures;
5. current implementation only as the thing being measured.

If implementation and a test disagree, first classify the disagreement. Never automatically change the test to match code or code to match an unreviewed test.

## Required test viewpoints

Every meaningful workflow chooses applicable viewpoints explicitly:

- **Business outcome** — does the user/phase goal hold?
- **Contract/interface** — exact input/output/authority behavior.
- **Negative/failure** — denial, timeout, corruption, missing evidence, wrong actor/profile.
- **Recovery/idempotency** — crash, resume, replay, no duplicate mutation.
- **Security/privacy/trust** — authorization, provenance, redaction, byte identity.
- **Concurrency/resource** — guards, budgets, capacity, OOM/resource pressure.
- **Lifecycle/freshness** — reboot/OOBE/epoch/final-state evidence.
- **Observability/evidence** — actual proof, not process-exit or PASS-shaped envelopes.
- **Performance/quality** — only when the relevant phase and environment are qualified.

A high test count is not a substitute for coverage of these viewpoints or named acceptance cases.

## Test contract per workflow

Every active workflow in `NEXT_WORK_ITEM.md` must expose:

```yaml
TEST_CONTRACT:
  BUSINESS_GOAL:
  TEST_BASIS:
  ACCEPTANCE_IDS:
  ORACLE_SOURCE:
  VIEWPOINTS:
  POSITIVE_CASES:
  NEGATIVE_CASES:
  TARGETED_COMMAND:
  FULL_COMMAND:
  ENVIRONMENT_CLASS:
  TEST_DATA_CLASS:
  NATIVE_EXECUTION_ALLOWED:
  PASS_MEANS:
  PASS_DOES_NOT_MEAN:
```

`ORACLE_SOURCE` must identify requirements/contracts/review evidence. It must never say “current code behavior”.

## Changing tests when business changes

Test expectations may change only under one of these classifications:

- `APPROVED_BEHAVIOR_CHANGE` — reviewed business/design contract changed; update test basis first, then tests and implementation.
- `TEST_DEFECT` — test contradicts the already-approved behavior; document evidence and independently review the test correction.
- `HARNESS_DEFECT` — executor/fixture/timing/provenance is wrong while the oracle remains correct.
- `ENVIRONMENT_DEFECT` — test cannot establish its required environment; do not weaken the oracle.
- `IMPLEMENTATION_DEFECT` — test is correct; fix code, not expectation.

A producer may change implementation and add tests in one increment, but any **semantic change to expected results** must name one classification and its independent authority. “Make CI green” is never a test basis.

## Test-script architecture

Test scripts are **executors**, not business-spec generators. They may discover files/cases, provision synthetic author fixtures, run tests and aggregate evidence. They must not derive expected results from production constants/functions merely to make the test agree with the implementation.

Required script properties:

- deterministic, explicit exit codes and bounded output;
- source/test/environment identity included in evidence;
- no hidden network/native execution outside the workflow permission;
- generated evidence stored outside mutable source or restored after verification;
- skipped/not-run cases remain visible and never become PASS;
- expectation changes are reviewable separately from executor changes;
- test data/fixtures cannot become production authority.

## Test workflow

```text
read TEST_CONTRACT
→ verify business/contract basis
→ verify environment class
→ run targeted tests
→ classify each failure before editing anything
→ fix the correct layer (test / harness / environment / implementation / design)
→ run full regression at delivery boundary
→ independent REVIEW inspects tests/oracles before trusting result
```

The canonical wrapper is `tools/run_test_workflow.py`. The existing WSL `lane-test.sh` is a low-level executor; it does not define business expectations.

## Model-evaluation testing

Model benchmarks are invalid unless bound to a fresh `SERVER_ENVIRONMENT.md` / environment snapshot and a model/run identity. Record at least model/version/hash, runtime stack, precision, scheduler, seed, input profile, resolution, frames/FPS/duration, batch/concurrency, wall time, throughput, peak RAM/VRAM, output artifacts and quality metrics.

Performance or quality numbers from different environment fingerprints are not directly comparable unless the comparison explicitly controls or explains the difference.

## Anti-patterns

Forbidden:

- changing expected values because current code returns something else;
- deleting/relaxing negative cases to raise pass rate;
- treating mocks/fixtures/process exit/test count as native proof;
- source-code coverage percentage as the primary business coverage metric;
- benchmark comparisons without environment/model identity;
- silently editing tests and calling the old review verdict still applicable.
