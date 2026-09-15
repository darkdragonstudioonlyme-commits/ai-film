# AI-FILM-SERVER — Independent IMPLEMENT / REVIEW Execution Lanes

This document defines two operationally independent lanes while preserving the Blueprint's single canonical project mode/gate state.

## 1. Global invariant

`main` remains the **canonical project state ledger**. `PROJECT_STATE.md` determines the current project mode/gates.

The two lanes are independent work streams, not two authorities that may independently advance gates:

```text
IMPLEMENT lane  ── immutable candidate handoff ──> REVIEW lane
      ^                                         │
      └──────── findings / verdict ─────────────┘

main = canonical state/gate ledger
```

IMPLEMENT cannot self-approve review. REVIEW cannot modify candidate source. Only `main` records project-wide mode/gate transitions.

## 2. IMPLEMENT lane

```yaml
LANE_ID: IMPLEMENT-P00
REMOTE_BRANCH: lane/implement-p00
WSL_WORKTREE: /home/dragon/ai-film-dev/implement
LOCAL_SOURCE_BRANCH: impl/p00
SOURCE_WRITABLE: true
REVIEW_VERDICT_AUTHORITY: false
```

Responsibilities:

- change source/config/tests/docs inside reviewed implementation scope;
- fix accepted review findings;
- run targeted and full author regressions;
- create local source commits for every coherent increment;
- create exact delivery packages and byte-verify persistence;
- update implementation/traceability docs and living memory;
- create immutable implementation→review candidate handoffs.

Forbidden:

- issue CODE_REVIEW PASS/FAIL as the implementer;
- modify FD/D00/public contract without design flow;
- treat author tests as native validation;
- hand REVIEW uncommitted or unidentified source.

Current lane state is stored on branch `lane/implement-p00` in `LANE_STATE.md`.

## 3. REVIEW lane

```yaml
LANE_ID: REVIEW-P00
REMOTE_BRANCH: lane/review-p00
WSL_WORKTREE: /home/dragon/ai-film-dev/review
SOURCE_MODE: detached exact candidate
SOURCE_WRITABLE: false
REVIEW_ARTIFACTS_WRITABLE: true
```

Responsibilities:

- consume one immutable candidate at a time;
- independently re-read requirements/contracts and candidate diff/source;
- run review-safe author/static/negative scenarios;
- search failure modes before happy paths;
- write findings with evidence, severity, impact and required disposition;
- issue `PASS`, `PASS_WITH_FIXES`, or `FAIL` only for the exact reviewed candidate.

Forbidden:

- edit candidate source while reviewing;
- inspect uncommitted IMPLEMENT changes as formal candidate input;
- repair a finding in REVIEW mode;
- infer native/LAB/SITE PASS from author tests.

After a verdict, REVIEW remains frozen on that candidate for audit and moves to `WAITING_FOR_NEXT_CANDIDATE`.

Current lane state is stored on branch `lane/review-p00` in `LANE_STATE.md`.

## 4. Immutable handoff contract

IMPLEMENT→REVIEW handoff must include at least:

```yaml
CANDIDATE_ID:
SOURCE_COMMIT_SHA:
DELIVERY_VERSION:
PACKAGE_NAME:
PACKAGE_SIZE_BYTES:
PACKAGE_SHA256:
ARTIFACT_STORE_ID:
SOURCE_CONTENT_DIGEST:
TEST_CONTENT_DIGEST:
AUTHOR_TEST_RESULT:
STATIC_CHECK_RESULT:
CONTRACT_DIGEST:
CHANGED_SCOPE:
KNOWN_FINDINGS:
AUTHOR_COMPLETE:
CODE_REVIEW_HANDOFF_READY:
```

REVIEW verifies these identities before review work. If identity differs, review stops rather than silently switching target.

Formal `CODE_REVIEW_PASS` requires `AUTHOR_COMPLETE=true` and `CODE_REVIEW_HANDOFF_READY=true`. Early/advisory review may run before that, but cannot pass the full gate.

## 5. REVIEW→IMPLEMENT finding contract

Each finding must contain:

```yaml
FINDING_ID:
TARGET_CANDIDATE_ID:
TARGET_SOURCE_COMMIT_SHA:
SEVERITY: BLOCKER | HIGH | MEDIUM | LOW
CATEGORY:
EVIDENCE:
IMPACT:
REQUIRED_DISPOSITION:
STATUS: OPEN | FIXED_PENDING_REVIEW | CLOSED
```

IMPLEMENT fixes findings on its own writable branch. REVIEW validates fixes only after receiving a new immutable candidate; it does not review the mutable IMPLEMENT worktree.

## 6. WSL lane isolation

Prepared layout:

```text
/home/dragon/ai-film-dev/
├── source-dev8/       # immutable exact dev8 recovery baseline
├── implement/         # writable worktree, branch impl/p00
├── review/            # detached exact reviewed candidate
├── repo/              # canonical GitHub state clone
├── artifacts/         # exact delivery packages
├── run-evidence/
│   ├── implement/     # author lane evidence
│   └── review/        # review lane evidence
├── implement-env.sh
├── review-env.sh
└── lane-test.sh
```

Use:

```bash
source /home/dragon/ai-film-dev/implement-env.sh
/home/dragon/ai-film-dev/lane-test.sh implement
```

or:

```bash
source /home/dragon/ai-film-dev/review-env.sh
/home/dragon/ai-film-dev/lane-test.sh review
```

The evidence directories are separate; test helpers restore tracked generated evidence before exit so one lane's verification does not contaminate source diffs.

## 7. Candidate rotation

When IMPLEMENT creates a new candidate:

1. commit the IMPLEMENT source branch;
2. run required author regression/static checks;
3. package and raw re-download/hash-verify artifact;
4. create immutable handoff record;
5. update IMPLEMENT lane state to `HANDED_OFF`/continue-work status as appropriate;
6. recreate or reset REVIEW worktree detached at **that exact source commit**;
7. update REVIEW lane state with the new candidate identity;
8. REVIEW executes independently.

REVIEW never follows IMPLEMENT branch head automatically.

## 8. Current lane state

At creation of this two-lane model:

- IMPLEMENT starts from exact dev8 commit `c44c2f87084f8082ce29af5935c6b47d03f7b96c` and must address `CR-P00-002`, `CR-P00-003`, `CR-P00-004` before continuing broader implementation.
- REVIEW is detached at the same exact dev8 candidate, whose recorded verdict is `FAIL`, and is waiting for the next immutable candidate.
- `CR-P00-001` remains the umbrella blocker until full author-complete implementation exists.

## 9. Cross-chat rule

A fresh chat must choose a lane explicitly from the task:

- source changes/finding fixes → IMPLEMENT lane;
- candidate review/verdict → REVIEW lane.

Before work, read `PROJECT_STATE.md`, `NEXT_WORK_ITEM.md`, this file, and the selected branch's `LANE_STATE.md`. Never mix lane permissions within one work increment.
