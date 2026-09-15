# NEXT WORK ITEM — WF-P00-IMPL-DEV18

```yaml
WORKFLOW_ID: WF-P00-IMPL-DEV18
LANE: IMPLEMENT
STATUS: RESUME_DOCUMENTED_WIP
MODE: IMPLEMENTATION
PHASE: "00 — Host / WSL"
WORK_ITEM_ID: IMPL-P00-001
INPUT_IDENTITY:
  BASE_COMMIT: 64ea95bf10e05e856a009be9204983182f520b45
  WORKTREE: /home/dragon/ai-film-dev/implement
  WIP_FILES: 4
  LAST_AUTHOR_RESULT: "756 PASS / 100 static PASS"
GOAL: "Complete CR-P00-012/013 remediation, finalize exact dev18, and hand it to independent REVIEW."
SUCCESS_OUTPUT: "immutable dev18 source commit/package + independent REVIEW disposition for CR-P00-012/013"
ON_SUCCESS: "continue remaining IMPL-P00-001 roadmap; CR-P00-001 stays open until full author completion"
ON_FAIL: "classify failure via TEST_STRATEGY/WORKFLOW_ROUTER; fix owning layer and re-run"
ON_BLOCK: "persist block; run SELF_LEARNING_SYSTEM retrospective if trigger conditions are met"
RETURN_TO: IMPL-P00-001
EXIT_CONDITION: "dev18 exact candidate persisted and independently reviewed"
```

## Steps

1. Fresh-fetch canonical/lane refs and run runtime-state reconciliation; confirm exactly the documented four-file WIP.
2. Read REVIEW findings `CR-P00-012` and `CR-P00-013` plus exact Phase00 acceptance/failure/evidence contracts relevant to REM-08.
3. Preserve business oracles; do not change expected results to match implementation.
4. Run focused harness tests; inspect collector build/contract binding and preparation/controller continuity through exact stage windows.
5. Run the full business-governed author workflow.
6. Update source evidence/docs/memory; classify any test change explicitly.
7. Diff/secret scan, commit exact dev18 source, package from that commit, hash/manifest verify, persist immutable handoff.
8. REVIEW lane checks out exact dev18 candidate; IMPLEMENT does not self-close findings.

## TEST_CONTRACT

```yaml
TEST_CONTRACT:
  BUSINESS_GOAL: "Causal native-harness source must reject provenance from the wrong build/contract and must prove reviewed preparation/controller conditions across the exact production stage window."
  TEST_BASIS:
    - "Exact approved Phase00 V2 acceptance matrix"
    - "Exact Phase00 failure/recovery and evidence contracts"
    - "Independent REVIEW findings CR-P00-012 and CR-P00-013"
    - "IMPL-REM-08 closure requirements"
  ACCEPTANCE_IDS: [CR-P00-012, CR-P00-013, IMPL-REM-08, T00-07, T00-13, T00-14]
  ORACLE_AUTHORITY_CLASS: COMPOSITE_APPROVED_AUTHORITIES
  ORACLE_SOURCE: "reviewed Phase00 V2 contracts + independent REVIEW findings CR-P00-012/013"
  TEST_CHANGE_CLASS: IMPLEMENTATION_DEFECT
  TEST_CHANGE_AUTHORITY: "CR-P00-012/013; no approved business expectation change"
  VIEWPOINTS: [business_outcome, negative_failure, security_trust, concurrency, lifecycle_freshness, observability_evidence, recovery_idempotency]
  POSITIVE_CASES: "exact suite/build/contract-bound collectors, stage-window continuity witnesses, exact controller-step coverage"
  NEGATIVE_CASES: "wrong-build/wrong-contract collector, expired preparation continuity, controller step outside stage window, string-only/unbound evidence"
  TARGETED_COMMAND: "cd /home/dragon/ai-film-dev/implement && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:tests /home/dragon/ai-film-dev/.venv/bin/python -m unittest tests.test_dev15_harness"
  FULL_COMMAND: "/usr/bin/python3 /home/dragon/ai-film-dev/repo/tools/run_test_workflow.py implement"
  ENVIRONMENT_CLASS: WSL_DEVELOPMENT_AUTHORING
  TEST_DATA_CLASS: SYNTHETIC_AUTHOR_TESTS_AND_PROJECT_METADATA
  NATIVE_EXECUTION_ALLOWED: false
  PASS_MEANS: "author-level source/test invariants for the exact dev18 candidate satisfy the named reviewed harness requirements sufficiently for immutable REVIEW handoff"
  PASS_DOES_NOT_MEAN: "any of the 86 native cases executed, acceptance closed, CODE_REVIEW_PASS, qualification, model-evaluation readiness or HOST_READY"
```

## Forbidden

Do not run native Windows/WSL/LAB/SITE/guest/network routes during authoring; do not lower reviewed acceptance; do not treat catalog presence, process exit, fixtures or author tests as native proof; do not discard current WIP to simplify state.
