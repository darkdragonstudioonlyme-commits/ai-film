# REVIEW Lane State — Phase 00

```yaml
LANE_ID: REVIEW-P00
LANE_ROLE: REVIEW
STATUS: WAITING_FOR_NEXT_CANDIDATE
GLOBAL_MODE: IMPLEMENTATION
FORMAL_REVIEW_WORK_ITEM: CODE-REVIEW-P00-001
REMOTE_BRANCH: lane/review-p00
WSL_WORKTREE: /home/dragon/ai-film-dev/review
SOURCE_MODE: DETACHED_EXACT_CANDIDATE
SOURCE_WRITABLE: false
REVIEW_ARTIFACTS_WRITABLE: true
CURRENT_CANDIDATE: 0.1.0.dev8
CURRENT_SOURCE_COMMIT: c44c2f87084f8082ce29af5935c6b47d03f7b96c
CURRENT_PACKAGE_SHA256: d4e6b67eebd40fbc173f85205792499021cf6eea9b82309e54c2a76a9a9e3cb5
LAST_VERDICT: FAIL
OPEN_FINDINGS: [CR-P00-001, CR-P00-002, CR-P00-003, CR-P00-004]
```

## Mission

Review only immutable candidates produced by IMPLEMENT. This lane may re-run author tests, inspect exact source/diff/contracts, execute non-native review scenarios, and write findings/verdict artifacts.

It must **not** modify candidate source or patch findings. Any code change returns to IMPLEMENT/PATCH as required by the project mode machine.

## Independence rules

- Review target is identified by exact source commit + package SHA, never by a mutable directory name alone.
- REVIEW ignores IMPLEMENT intent and reads requirements/diff/artifact independently.
- REVIEW never reads uncommitted implementation changes as a formal candidate.
- Findings are written with severity, evidence, impact, required disposition, and exact target identity.
- A PASS cannot be issued when `AUTHOR_COMPLETE=false` or `CODE_REVIEW_HANDOFF_READY=false`.

## Current disposition

Exact dev8 review completed with FAIL. The lane is frozen on dev8 for audit and waits for the next immutable candidate handoff from IMPLEMENT.

Existing review record: `reviews/CODE-REVIEW-P00-001_DEV8.md` on canonical `main`.
