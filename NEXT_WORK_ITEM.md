# NEXT WORK ITEM — Independent dev19 delta review

```yaml
WORKFLOW_ID: WF-P00-REVIEW-DEV19
LANE: REVIEW
STATUS: READY
MODE: IMPLEMENTATION
PHASE: "00 — Host / WSL"
WORK_ITEM: CODE-REVIEW-P00-001-DEV19-DELTA
INPUT_IDENTITY:
  CANDIDATE_ID: IMPL-P00-001-DEV19
  SOURCE_COMMIT: 2ac37acdd3f81d3b86d4ffb019689655110a80c2
  PACKAGE_PATH: /home/dragon/ai-film-dev/artifacts/IMPL-P00-001_IMPLEMENTATION_PACKAGE_V19.zip
  PACKAGE_SIZE_BYTES: 1165317
  PACKAGE_SHA256: 564ad67c2ddc00f1f4ffbc891afa1aeb1c0c194b0d2fb6c30767f6ae381491e1
  MANIFEST_SHA256: dbb940526db699e6810ee5f8844e00b1cba22c3843f2667479daad91c303211e
  SOURCE_DIGEST: 2271c07575e4217dabde324c7de0d35a1188c965d32f1aee38648d44d35873c4
  TEST_DIGEST: 8deb2d74dc098ad161557773382afb54293dc0ea4e59b95fe6b591fc7d803fdb
  AUTHOR_TESTS: "759 PASS"
  STATIC_CHECKS: "100 PASS"
GOAL: "Independently verify dev19 CR-P00-012/014 remediation while preserving closed CR-P00-013 behavior."
SUCCESS_OUTPUT: "Immutable review + TEST_REVIEW verdict bound to exact dev19 candidate."
ON_SUCCESS: WF-P00-IMPL-CR001-RESIDUAL-AUDIT
ON_FAIL: WF-P00-IMPL-DEV20-REVIEW-FIX
```

## Required REVIEW

1. Checkout detached exact `2ac37ac...`; verify package SHA/size/manifest and member hashes.
2. Independently rerun workspace/static checks.
3. Verify a production-shaped `collector_release` without `contract_digest` is accepted under a valid contract-bound suite.
4. Verify wrong collector build rejects at collector authority; wrong suite contract rejects at suite/contract authority.
5. Re-run CR-P00-013 continuity/window/route-binding/T07-H regression to ensure dev19 did not reopen it.
6. Review dev18→dev19 diff against D00-14 and `native/proofs.py` authority split; search for new provenance/schema gaps.
7. Review `TEST_CHANGE-P00-DEV19-HARNESS-002` independently; implementation code cannot define fixture authority.
8. Ensure REVIEW source remains clean; persist review/test-review records.

If delta PASS, close CR-P00-012/014, keep CR-P00-013 closed, mark workflow-health incident recovered, and route immediately to residual CR-P00-001 author-completeness audit. Overall CODE_REVIEW_PASS remains false until that umbrella blocker closes.
