# NEXT WORK ITEM — dual-lane execution after dev8 review FAIL

```yaml
PROJECT_MODE: IMPLEMENTATION
PHASE: "00 — Host / WSL"
CURRENT_DELIVERY: PARTIAL_SOURCE_DROP_DEV8
LAST_CODE_REVIEW: CODE-REVIEW-P00-001 / FAIL
TARGET_GATE: CODE_REVIEW_PASS
EXECUTION_MODEL: DUAL_LANE
IMPLEMENT_LANE: lane/implement-p00
REVIEW_LANE: lane/review-p00
```

Read `EXECUTION_LANES.md` before work.

## IMPLEMENT lane — ACTIVE

```yaml
WORK_ITEM_ID: IMPL-P00-001
REMOTE_BRANCH: lane/implement-p00
WSL_WORKTREE: /home/dragon/ai-film-dev/implement
LOCAL_SOURCE_BRANCH: impl/p00
BASE_COMMIT: c44c2f87084f8082ce29af5935c6b47d03f7b96c
SOURCE_WRITABLE: true
```

Immediate queue:

1. Fix `CR-P00-002` — re-authorize immediately before durable owner-wait relabel; test expiry/generation/actor/request drift after observation.
2. Fix `CR-P00-003` — persist a safe typed/bounded actual wait cause at the durable wait boundary instead of dropping pending-reboot context.
3. Fix `CR-P00-004` — exact per-wait schemas, unknown-key rejection, canonical size/privacy bound, digest/reference preference for larger evidence.
4. Run targeted tests then `/home/dragon/ai-film-dev/lane-test.sh implement`.
5. Commit coherent source increment on `impl/p00`; package and byte-verify exact candidate.
6. Continue prior pre-C3/checkpoint + nested E00, publication/E17, non-DIRECT transport, causal 86-case controller and production-factory integration scope.
7. `CR-P00-001` closes only when full author-complete scope exists.

IMPLEMENT may not issue review verdicts.

## REVIEW lane — WAITING_FOR_NEXT_CANDIDATE

```yaml
FORMAL_WORK_ITEM: CODE-REVIEW-P00-001
REMOTE_BRANCH: lane/review-p00
WSL_WORKTREE: /home/dragon/ai-film-dev/review
SOURCE_MODE: detached exact candidate
CURRENT_CANDIDATE: dev8
CURRENT_COMMIT: c44c2f87084f8082ce29af5935c6b47d03f7b96c
LAST_VERDICT: FAIL
SOURCE_WRITABLE: false
```

Review lane remains frozen on dev8 for audit. It does not follow IMPLEMENT changes.

When IMPLEMENT produces a new immutable handoff, REVIEW must be reset/recreated detached at the exact candidate commit, verify package/digests, then review independently. It may write findings/verdicts only; it must not patch source.

## Exact dev8 recovery anchor

```yaml
PACKAGE: IMPL-P00-001_IMPLEMENTATION_PACKAGE_V8.zip
SIZE_BYTES: 1091121
SHA256: d4e6b67eebd40fbc173f85205792499021cf6eea9b82309e54c2a76a9a9e3cb5
DRIVE_FILE_ID: 125T2wVf0CVkcmQND0PSmF3HHvXh8AgxD
AUTHOR_BASELINE: "683 PASS / 92 static PASS"
```

## Lane commands

IMPLEMENT:

```bash
source /home/dragon/ai-film-dev/implement-env.sh
/home/dragon/ai-film-dev/lane-test.sh implement
```

REVIEW:

```bash
source /home/dragon/ai-film-dev/review-env.sh
/home/dragon/ai-film-dev/lane-test.sh review
```

## Forbidden cross-lane behavior

- REVIEW never patches candidate source.
- IMPLEMENT never self-approves CODE_REVIEW.
- REVIEW never formally reviews uncommitted IMPLEMENT state.
- Candidate handoff must bind exact source commit + package SHA + author evidence.
- Findings must bind the exact reviewed candidate.
- Native Windows/WSL/LAB/SITE proof cannot be inferred from either lane's author tests.
- FD/D00/public contracts remain unchanged unless routed through design/review.

## Exit condition

IMPLEMENT reaches author-complete exact candidate and writes an immutable handoff with `AUTHOR_COMPLETE=true` and `CODE_REVIEW_HANDOFF_READY=true`; REVIEW then independently reviews that exact candidate. Only a REVIEW PASS on that identity can satisfy `CODE_REVIEW_PASS`.
