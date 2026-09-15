# IMPLEMENT Lane State — Phase 00

```yaml
LANE_ID: IMPLEMENT-P00
LANE_ROLE: IMPLEMENT
STATUS: ACTIVE
GLOBAL_MODE: IMPLEMENTATION
GLOBAL_WORK_ITEM: IMPL-P00-001
REMOTE_BRANCH: lane/implement-p00
WSL_WORKTREE: /home/dragon/ai-film-dev/implement
LOCAL_SOURCE_BRANCH: impl/p00
BASE_SOURCE_COMMIT: c44c2f87084f8082ce29af5935c6b47d03f7b96c
BASE_DELIVERY: 0.1.0.dev8
BASE_PACKAGE_SHA256: d4e6b67eebd40fbc173f85205792499021cf6eea9b82309e54c2a76a9a9e3cb5
SOURCE_WRITABLE: true
REVIEW_WRITABLE: false
```

## Mission

Implement source/tests/docs only. This lane may modify the source worktree, run author tests, create local source commits, package candidates, and prepare immutable handoffs to REVIEW.

It may **not** issue CODE_REVIEW verdicts, qualification, validation PASS, or HOST_READY.

## Immediate queue

1. Fix review findings `CR-P00-002`, `CR-P00-003`, `CR-P00-004` from exact dev8 review.
2. Run targeted + full author regression/static checks.
3. Persist a new exact candidate delivery.
4. Continue remaining IMPL-P00-001 scope: prior pre-C3/checkpoint provenance, nested cross-stage E00, publication/E17 recovery, non-DIRECT transport, causal 86-case controllers, production-factory integration.
5. Only when author-complete, create a formal implementation→review handoff.

`CR-P00-001` is the umbrella blocker: full code review cannot PASS while implementation remains incomplete.

## Candidate handoff contract

A candidate is handed to REVIEW only through an immutable record containing:

- candidate ID/version;
- exact local source commit SHA;
- exact package name/size/SHA-256 and artifact-store ID;
- source/test content digests;
- author regression/static results;
- approved contract digest;
- changed scope;
- known/open findings;
- `AUTHOR_COMPLETE` and `CODE_REVIEW_HANDOFF_READY` flags.

REVIEW must never inspect uncommitted IMPLEMENT changes as a formal candidate.
