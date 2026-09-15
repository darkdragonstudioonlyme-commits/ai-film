# CODE-REVIEW-P00-001 — dev18 delta review

```yaml
TARGET: 0.1.0.dev18
SOURCE_COMMIT: f680067c2f23d7eea4c016247015359ffe431971
PACKAGE_SHA256: 4b52f896e583b52dbb3207bb9ebbfdcdd92f10fa463cddce430fed85a502aa09
PACKAGE_SIZE_BYTES: 1180358
SOURCE_MODIFIED_DURING_REVIEW: false
INDEPENDENT_TESTS: "757 PASS / 0 failure / 0 error / 0 skip"
INDEPENDENT_STATIC: "100 PASS"
DELTA_VERDICT: FAIL
OVERALL_CODE_REVIEW_VERDICT: FAIL
CODE_REVIEW_PASS: false
CLOSED_FINDINGS: [CR-P00-013]
OPEN_FINDINGS: [CR-P00-001, CR-P00-012, CR-P00-014]
```

## Independent verification

REVIEW checked out detached exact commit `f680067c...`, independently verified the V18 ZIP size/SHA, manifest SHA and all 276 manifest-listed member hashes, reproduced 757 PASS / 100 static PASS with the exact source/test digests, and kept the review worktree clean.

Former CR-P00-013 scenarios pass independently: preparation continuity expires fail closed, controller temporal mismatch is rejected, result evidence cannot rebind a controller action to a different procedure-owned route index, all 86 procedure digests/binding mirrors match, and T07-H binds CREATE to `INVOKE_PRODUCTION_REQUEST` before reconciliation. CR-P00-013 is therefore CLOSED for this delta.

## CR-P00-012 — remains OPEN — remediation binds contract to the wrong authority object

Dev18 changes `_collector()` so a pinned `collector_release` must contain both `build_digest` and `contract_digest`. The exact reviewed contract requires evidence records to retain collector/build/contract hashes, but the existing production proof path binds contract identity on the measurement/proof record and binds the collector release by reviewed build. `ProofReader` requires `measurement.contract_digest == CONTRACT_DIGEST` and `collector_release.build_digest == measurement.collector_digest`; it does not define or consume `collector_release.contract_digest`.

Repository-wide inspection found no pre-dev18 collector-release producer/schema/fixture containing `contract_digest`. Existing collector-release fixtures have `withdrawn`, `review_verdict`, and `build_digest`. Dev18 therefore makes valid production-shaped collector releases unable to satisfy the harness finalizer.

Required disposition: do not silently extend the collector-release authority schema. Preserve exact contract binding through the already-authorized suite/causal evidence record and exact build binding through `collector_release.build_digest`, or add explicit contract identity to the causal record if required by D00-14. If a collector-release contract field is truly required, record a DESIGN_GAP before changing that authority contract.

## CR-P00-014 — HIGH — author test fixture invented an unsupported authority field

`tests/test_dev15_harness.py::collector()` was changed to add `contract_digest` solely so dev18 `_collector()` could pass. That fixture no longer mirrors the production collector-release shape used by `ProofReader` and earlier proof tests. The author suite therefore gave a false-green result for a native path that current authority records cannot satisfy.

Impact: native acceptance finalization would block a valid reviewed collector release even though author tests pass. This violates Documentation System V2 test authority: implementation code is the subject under test and may not redefine the authority fixture/oracle.

Required disposition: restore production-shaped authority fixtures, add regression coverage that detects collector-release schema divergence, and independently prove contract identity at the correct suite/evidence boundary.

## Contract evidence used

`contracts/PHASE00_INFRA_DESIGN_V2.md` D00-14 requires evidence records to include collector/build/contract hashes. `src/aifilm_p00/native/proofs.py` implements the current authority split: measurement/proof record contract binding plus reviewed collector build binding.

## Non-claims

The 86 native cases remain NOT_RUN. This review did not execute Windows/WSL/LAB/SITE validation and did not modify source. Remote artifact-store persistence for dev18 remains pending tool capability.
