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

CURRENT_CANDIDATE: 0.1.0.dev12
CURRENT_SOURCE_COMMIT: 536b86f97467a165e21a8b3038a72a91b7311a79
CURRENT_PACKAGE_SHA256: d5e519335e4ad1f9ce005596834f80a229f459e1b77720a2317697a7b4bec4d4
INDEPENDENT_TESTS: "728 PASS / 0 failure / 0 error / 0 skip"
INDEPENDENT_STATIC: "95 PASS"

DELTA_VERDICT: FAIL
NEW_FINDING:
  ID: CR-P00-006
  SEVERITY: HIGH
  SUMMARY: "No-archive normal publication accepts a pre-existing approved final output, while recovery rejects the same state."
OPEN_FINDINGS: [CR-P00-001, CR-P00-006]
CODE_REVIEW_PASS: false
```

## CR-P00-006 evidence

For an E16 `BLOCKED_REDACTION/23` no-archive result, REVIEW pre-populated the exact approved `bundle_output` with stale bytes. `NativeBundlePublisher.publish(...)` returned `published=false` and durable no-archive intent without rejecting the pre-existing final file. The stale file remained at the approved path. By contrast, `observed_publication(...)` for the same no-archive intent rejects an existing final path as `PUBLISH_UNEXPECTED_FINAL`.

Impact: normal and recovery paths disagree about output ownership. A stale artifact at the exact approved output path can survive a blocked run and be mistaken by operators/downstream tooling for current output even though the run says no archive was published.

Required fix: before durably accepting a no-archive outcome, observe that the exact approved final output path is absent. Reject any pre-existing final as output collision/drift. Add a positive no-output test and a stale-final negative test. Do not delete/overwrite the stale file.

No source was modified during REVIEW.
