# AI-FILM-SERVER Git + Documentation Persistence Workflow

This repository is the persistent cross-chat project ledger for AI-FILM-SERVER.

## 1. Durable-increment rule

A meaningful increment is not durable until applicable source/tests/evidence/docs and exact artifacts are persisted and independently verified.

```text
VERIFY CURRENT REMOTE + EXACT SOURCE/ARTIFACT
→ SELECT ONE EXECUTION LANE
→ WORK WITHIN THAT LANE'S PERMISSIONS
→ TARGETED TEST / EVIDENCE
→ DELIVERY-BOUNDARY REGRESSION WHEN APPLICABLE
→ DOCUMENTATION SYNC GATE
→ DIFF REVIEW / SECRET SCAN
→ PERSIST EXACT ARTIFACT IF PRODUCED
→ COMMIT/PUSH LANE + CANONICAL STATE AS REQUIRED
→ VERIFY ARTIFACT HASH + REMOTE GIT
→ ONLY THEN CONTINUE
```

## 2. Two independent execution lanes

The project now has two operationally independent lanes. Full rules are in `EXECUTION_LANES.md`.

### IMPLEMENT

```text
remote branch: lane/implement-p00
WSL worktree:  /home/dragon/ai-film-dev/implement
source branch: impl/p00
```

IMPLEMENT may change source/tests/docs, create author commits and packages, and fix review findings. It cannot issue CODE_REVIEW verdicts.

### REVIEW

```text
remote branch: lane/review-p00
WSL worktree:  /home/dragon/ai-film-dev/review
source mode:   detached exact candidate
```

REVIEW may inspect/retest an immutable candidate and write findings/verdicts. It must not patch source.

`main` remains the canonical project mode/gate ledger. Parallel lanes do not create parallel gate authority.

## 3. Immutable handoff rule

IMPLEMENT never hands REVIEW a mutable directory or branch head by implication. Every candidate handoff must bind exact source commit SHA, delivery/package SHA-256, artifact ID, source/test digests, author-test result, contract digest, changed scope, known findings, and handoff-readiness flags.

REVIEW must verify target identity before work. REVIEW never follows IMPLEMENT branch head automatically.

A REVIEW→IMPLEMENT finding must bind the exact reviewed candidate and include severity, evidence, impact, required disposition and status.

## 4. Persistence roles

- **GitHub `main`**: canonical project state, living memory, next work, workflow, review history and lane pointers.
- **`lane/implement-p00`**: implementation-lane operational state.
- **`lane/review-p00`**: review-lane operational state.
- **Byte-preserving artifact store**: exact packaged delivery bytes; current store is connected Google Drive.
- **WSL local Git worktrees**: source authoring/review isolation; local commits alone are not remote approval.

Every external exact artifact must be referenced by file ID/name, size and SHA-256.

## 5. Binary artifact verification

```text
UPLOAD FILE REFERENCE / RAW BYTES
→ DOWNLOAD RAW BYTES AGAIN
→ RECOMPUTE SHA-256
→ COMPARE WITH SOURCE HASH
→ RECORD STORE ID + SIZE + HASH IN GIT
```

Upload success alone is not identity proof.

## 6. Canonical documentation roles

| File | Responsibility |
|---|---|
| `PROJECT_STATE.md` | Global current truth and gate state |
| `NEXT_WORK_ITEM.md` | Current implementation queue and lane disposition |
| `EXECUTION_LANES.md` | Lane isolation/handoff protocol |
| `PROJECT_MEMORY.md` | Reusable discoveries/optimizations/risks/lessons |
| `GIT_WORKFLOW.md` | Standing persistence protocol |
| `WORKSPACE_WSL.md` | Local WSL paths/helpers/baselines |
| `reviews/*` | Immutable review records/findings |
| `deliveries/*` | Exact delivery identity records |
| `AI_FILM_STATE_CHECKPOINT_Vn.*` | Immutable milestone snapshots |
| lane branch `LANE_STATE.md` | Lane-specific current state |

Historical checkpoints are not current truth.

## 7. Automatic Documentation Sync Gate

Before a meaningful increment is durable, update without waiting for the user:

| Trigger | Persistent update |
|---|---|
| global mode/phase/baseline/gate/blocker/test/review changed | `PROJECT_STATE.md` |
| next implementation scope/order changed | `NEXT_WORK_ITEM.md` |
| lane status/candidate changed | selected lane's `LANE_STATE.md` + global pointer if material |
| reusable optimization/discovery/tooling/failure/risk | `PROJECT_MEMORY.md` |
| lane/workflow policy changed | `EXECUTION_LANES.md` / `GIT_WORKFLOW.md` + memory |
| WSL environment/layout changed | `WORKSPACE_WSL.md` |
| implementation progress changed | implementation/remaining/traceability docs |
| review finding/verdict changed | review artifact + state |
| milestone/gate transition | new checkpoint MD + JSON |

**No silent knowledge:** if a new chat would lose a fact that prevents duplicated work, wrong decisions, repeated failure or safety/reproducibility regression, documentation sync is incomplete.

## 8. Evidence discipline

Persistent claims remain classified as observed/tested fact, reviewed decision, inference/hypothesis, proposed optimization, or unresolved blocker. Markdown is not evidence by itself. Author workspace tests are not Windows/WSL/LAB/SITE proof.

## 9. IMPLEMENT commit sequence

1. Verify `main`, IMPLEMENT lane state and exact base candidate.
2. Work only in `/home/dragon/ai-film-dev/implement` / branch `impl/p00`.
3. Run targeted tests.
4. At delivery boundary run full author regression/static checks.
5. Documentation Sync Gate.
6. Review diff and secret-scan.
7. Commit local source increment.
8. Package exact candidate if applicable; upload + raw re-download/hash verify.
9. Persist delivery/handoff/state records.
10. Verify remote state before next increment.

## 10. REVIEW sequence

1. Read canonical state + REVIEW lane state.
2. Verify immutable candidate source commit/package SHA.
3. Ensure REVIEW worktree is detached at that exact commit.
4. Re-read requirements and diff; search failure scenarios/negative cases first.
5. Run review-safe tests/scenarios without patching source.
6. Write findings/verdict bound to exact candidate.
7. Update REVIEW lane state to verdict / waiting-for-next-candidate.
8. Update canonical state/checkpoint if project status changes.
9. Verify source worktree remained unchanged.

## 11. Branch/history policy

`main` is not an implementation scratch branch. The lane branches are operational ledgers, and source authoring occurs in the local `impl/p00` worktree until exact source mirroring/push is intentionally supported.

Do not force-push or rewrite published history by default. REVIEW candidates are immutable; create a new candidate rather than editing the reviewed one.

## 12. CODE_REVIEW boundary

Formal `CODE_REVIEW_PASS` requires an exact immutable candidate with `AUTHOR_COMPLETE=true` and `CODE_REVIEW_HANDOFF_READY=true`. Early review may produce findings before that, but cannot pass the full gate.

Implementation commits/artifact uploads never self-approve code. REVIEW cannot patch code during review.

## 13. Cross-chat bootstrap

1. Read `PROJECT_STATE.md`.
2. Read `NEXT_WORK_ITEM.md`.
3. Read `EXECUTION_LANES.md`.
4. Choose IMPLEMENT or REVIEW from the requested task.
5. Read that remote branch's `LANE_STATE.md`.
6. Read relevant `PROJECT_MEMORY.md` entries and `WORKSPACE_WSL.md`.
7. Verify exact candidate/source identity before work.
8. Never mix lane permissions in one work increment.
