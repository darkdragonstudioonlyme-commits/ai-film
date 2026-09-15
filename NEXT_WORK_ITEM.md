# NEXT WORK ITEM — dev19 remediation after dev18 review

```yaml
WORKFLOW_ID: WF-P00-IMPL-DEV19-REVIEW-FIX
LANE: IMPLEMENT
STATUS: READY
MODE: IMPLEMENTATION
PHASE: "00 — Host / WSL"
WORK_ITEM: IMPL-P00-001
INPUT_COMMIT: f680067c2f23d7eea4c016247015359ffe431971
GOAL: "Correct CR-P00-012/014 using the existing authority model; preserve accepted CR-P00-013 behavior."
SUCCESS_OUTPUT: "Exact dev19 candidate with production-compatible collector provenance + independently reviewable tests."
ON_SUCCESS: WF-P00-REVIEW-DEV19
ON_FAIL: WF-P00-IMPL-DEV19-REVIEW-FIX
ON_BLOCK: WORKFLOW_ROUTER_BLOCK_PROTOCOL
```

## Required implementation order

1. Preserve exact dev18 commit/package/review records; start dev19 from clean `f680067c...`.
2. Re-read D00-14 evidence-record semantics and `native/proofs.py` collector/measurement authority split before editing.
3. Do **not** add or depend on `collector_release.contract_digest` unless a genuine reviewed contract requires it; if so, create DESIGN_GAP instead of silently changing authority schema.
4. Bind exact approved contract at the existing suite/causal evidence record boundary and bind collector release to exact reviewed build. If an explicit contract field is added to harness causal records, it must be suite-bound and covered by raw/content-addressed provenance where applicable.
5. Restore test collector fixtures to the production authority shape. Add regression showing a production-shaped reviewed collector is accepted under a valid contract-bound suite and wrong build/contract provenance is still rejected at the correct boundary.
6. Preserve all accepted CR-P00-013 stage-window/continuity/procedure-owned route-binding behavior and T07-H mapping.
7. Run targeted tests, then full author regression/static checks under V2 test governance. Create a new TEST_CHANGE/TEST_REVIEW cycle; do not reuse the failed dev18 test review as PASS evidence.
8. Diff/secret/inventory audit, commit exact dev19, package from exact commit, then immutable handoff to REVIEW.

## Review findings

- `CR-P00-012`: OPEN — dev18 remediation uses unsupported collector-release contract field.
- `CR-P00-013`: CLOSED on dev18 — preserve its behavior.
- `CR-P00-014`: OPEN HIGH — author fixture diverged from production authority schema and produced false-green coverage.
- `CR-P00-001`: OPEN umbrella author-completeness blocker.

## Forbidden

- change FD/D00/public contract merely to make dev18 approach legal;
- update tests to mirror implementation-specific authority fields without upstream authority;
- reopen/loosen accepted CR-P00-013 behavior;
- treat author tests as native proof;
- patch source in REVIEW.
