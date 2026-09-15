# REVIEW Lane State — Phase 00

```yaml
LANE_ID: REVIEW-P00
LANE_ROLE: REVIEW
STATUS: FINDING_RETURNED_TO_IMPLEMENT
GLOBAL_MODE: IMPLEMENTATION
FORMAL_REVIEW_WORK_ITEM: CODE-REVIEW-P00-001
REMOTE_BRANCH: lane/review-p00
WSL_WORKTREE: /home/dragon/ai-film-dev/review
SOURCE_MODE: DETACHED_EXACT_CANDIDATE
SOURCE_WRITABLE: false
REVIEW_ARTIFACTS_WRITABLE: true

CURRENT_CANDIDATE: 0.1.0.dev10
CURRENT_SOURCE_COMMIT: 2d4704d6dcf12ff47e311e10294c2129e78d8b2c
CURRENT_PACKAGE_SHA256: 7ff3588dc7fce263f74682282d98221a552e34661cf33a82ebb36a7986d27c8e
INDEPENDENT_TESTS: "710 PASS / 0 failure / 0 error / 0 skip"
INDEPENDENT_STATIC: "94 PASS"

DELTA_VERDICT: FAIL
NEW_FINDING:
  ID: CR-P00-005
  SEVERITY: HIGH
  SUMMARY: "PRE_C3 historical event time is not bounded by the current evidence-capture time."
OPEN_FINDINGS: [CR-P00-001, CR-P00-005]
CODE_REVIEW_PASS: false
```

## CR-P00-005 evidence

`_prior_guest_from_events` rejects future observations with `not_after`, but `_pre_c3_events` / `_validated_pre_c3` in dev10 do not compare `checked_at` with the current capture time. A review-only executable scenario supplied `checked_at=2026-09-16T00:00:00Z`; the selector accepted it as prior evidence.

Impact: a future-dated protection event/receipt can be consumed as historical pre-C3 provenance when the receipt itself is valid at that future timestamp. That breaks cross-stage temporal ordering and can make later E12/E15 evidence claim a precondition that had not yet occurred as of the snapshot.

Required fix: bind every selected PRE_C3 event to `checked_at <= current capture/context time` before receipt consumption, and add a negative test. Do not introduce an arbitrary TTL; this is ordering, not freshness policy.

No source was modified during REVIEW.
