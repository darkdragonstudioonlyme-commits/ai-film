# Documentation System V2 — Design

## Design goal

Make the project control plane progressively more capable instead of progressively more verbose. V2 extends V1 with business-first testing, meta-review on ineffective work, knowledge pruning, environment/model-evaluation identity, and a third independent holistic audit.

## New control surfaces

- `TEST_STRATEGY.md` — business/contract-derived test doctrine and test-change classification.
- `SELF_LEARNING_SYSTEM.md` — deadlock/inefficiency/user-correction triggers and retrospective/recovery loop.
- `KNOWLEDGE_LIFECYCLE.md` — active/deprecated/superseded/archived lifecycle plus compaction.
- `SERVER_ENVIRONMENT.md` + snapshot — environment truth and model-evaluation readiness.
- `tools/run_test_workflow.py` — policy-preflighted test execution; low-level runner is not the oracle.
- `tools/check_test_strategy.py` — verifies each active workflow carries a business-facing test contract.
- `tools/check_knowledge_hygiene.py` — detects version-pinned policy, memory bloat and environment metadata gaps.
- `tools/capture_server_environment.py` — read-only environment evidence/fingerprint capture.
- DOC-AUDIT workflow — full-system review after detailed DOC-REVIEW.

## Trust model

DOC-DESIGN produces an immutable candidate. DOC-REVIEW reviews design correctness. DOC-AUDIT then reviews the entire active documentation system and explicitly searches for shared assumptions/blind spots that design and first review may both have missed. Neither consumer edits the candidate it reviews.

## Test doctrine

Expected behavior comes from business/approved contracts/acceptance/review evidence. Implementation is only the measured subject. Test semantic changes require classification; harness fixes cannot silently change oracles.

## Self-learning doctrine

Repeated ineffective work is itself evidence that workflow design may be wrong. Objective triggers initiate a retrospective. Useful lessons are persisted, promoted to policy/tooling when repeated, and then compacted out of active memory so the system gets smarter without growing without bound.

## Environment doctrine

Development, native-validation and model-evaluation environments are separate classes. Observations are timestamped/fingerprinted. Missing GPU tooling means capability is unestablished, not absent. Benchmark comparison requires environment + model/run identity.

## Compatibility

V2 does not change FD/D00/public product contracts or source acceptance. It governs how work, tests, knowledge and environment evidence are managed.
