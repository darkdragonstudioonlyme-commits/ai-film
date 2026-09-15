# Documentation System V2 — Detailed Review R1

```yaml
REVIEW_ID: DOC-V2-REVIEW-R1
TARGET_COMMIT: b77f78881e0bdd7489d2599c53718d1c7453f02c
REVIEW_BRANCH: lane/docs-review-v2
SOURCE_MODIFIED_DURING_REVIEW: false
VERDICT: FAIL
```

## Independent review method

DOC-REVIEW-V2 checked out detached exact candidate `b77f788...`, ran all governance/static audit checks, then adversarially tested the business-test and knowledge-lifecycle controls. The review worktree remained clean.

## Findings

### D2R-F01 — HIGH — code-derived oracle wording bypasses the test checker

`tools/check_test_strategy.py` rejects only one literal phrase (`current code behavior`). An adversarial copy changed `ORACLE_SOURCE` to `existing source implementation output and observed current behavior`; the checker still returned PASS.

**Impact:** policy says source is never the oracle, but the automated preflight does not enforce that invariant robustly.

**Required fix:** parse the active `TEST_CONTRACT` field, require an allowlisted business/contract/review authority class, and reject implementation/source/code-derived oracle classes independent of wording.

### D2R-F02 — HIGH — test workflow is not bound to the active workflow/lane

While `NEXT_WORK_ITEM.md` declared `DOC-REVIEW-V2_THEN_DOC-AUDIT-V2`, running `tools/run_test_workflow.py implement` succeeded and executed 756 implementation tests.

**Impact:** the canonical test wrapper can apply the wrong test executor under the wrong business/test contract. The script is therefore not yet truly contract-driven.

**Required fix:** parse active workflow/lane/environment/test permission from `NEXT_WORK_ITEM.md`; reject incompatible requested modes before executing the low-level runner. Bind `ENVIRONMENT_CLASS` and `NATIVE_EXECUTION_ALLOWED` as preconditions.

### D2R-F03 — MEDIUM — knowledge-compaction threshold can self-trigger after successful compaction

`KNOWLEDGE_LIFECYCLE.md` triggers compaction when >20% of active-memory entries are promoted/superseded, while `PROJECT_MEMORY.md` intentionally retains compact provenance pointers for promoted lessons. Those pointers can make the threshold perpetually true.

**Impact:** the system can repeatedly compact already-compacted memory or pressure future chats to remove useful provenance pointers.

**Required fix:** distinguish detailed active entries from compact provenance pointers. Compaction threshold must count only detailed promoted/superseded entries, not compact index pointers.

## Disposition

Return to DOC-DESIGN-V2. New immutable candidate required. DOC-AUDIT-V2 must not start until detailed review passes.
