# AI-FILM-SERVER Git + Documentation Persistence Workflow

This repository is the persistent cross-chat project ledger for AI-FILM-SERVER.

## 1. Durable-increment rule

A meaningful increment is not durable until all applicable source/tests/evidence/docs and exact delivery artifacts have been persisted and independently verified.

```text
VERIFY CURRENT REMOTE + EXACT SOURCE/ARTIFACT
→ WORK IN ONE ACTIVE MODE ONLY
→ TARGETED TEST / EVIDENCE
→ DELIVERY-BOUNDARY REGRESSION WHEN APPLICABLE
→ DOCUMENTATION SYNC GATE
→ DIFF REVIEW
→ SECRET SCAN
→ PERSIST EXACT ARTIFACT IF PRODUCED
→ COMMIT/PUSH GIT STATE/SOURCE/DIFFS
→ VERIFY ARTIFACT HASH + REMOTE GIT
→ ONLY THEN CONTINUE
```

## 2. Persistence roles

- **GitHub `darkdragonstudioonlyme-commits/ai-film`**: canonical current state, living memory, workflow, next-work, reviewable source/diffs that can be written reliably, and commit history.
- **Byte-preserving artifact store**: exact packaged delivery bytes when a binary artifact is produced. Current store: connected Google Drive.
- **Cryptographic identity in Git**: every external exact artifact must be referenced by stable file ID/name, byte size, and SHA-256 in Git documentation/state.

A binary artifact is not considered persisted merely because upload succeeded. Required pattern:

```text
UPLOAD FILE REFERENCE / RAW BYTES
→ DOWNLOAD RAW BYTES AGAIN
→ RECOMPUTE SHA-256
→ COMPARE WITH SOURCE HASH
→ RECORD STORE ID + SIZE + HASH IN GIT
```

## 3. Canonical documentation roles

| File | Primary responsibility |
|---|---|
| `PROJECT_STATE.md` | Current operational truth |
| `NEXT_WORK_ITEM.md` | Exact next executable work |
| `PROJECT_MEMORY.md` | Reusable discoveries/optimizations/tooling/risk/testing/process knowledge |
| `GIT_WORKFLOW.md` | Standing persistence and automatic documentation-sync protocol |
| `CHAT_HANDOFF.md` | Compact bootstrap template |
| `SOURCE_IMPORT_STATUS.md` | Source/binary recovery-anchor status and procedure |
| `AI_FILM_STATE_CHECKPOINT_Vn.md` + JSON | Immutable milestone snapshots |
| Git commits/diffs | Reviewable source/document change history |

Do not duplicate mutable state unnecessarily. Historical checkpoints are not current truth.

## 4. Automatic Documentation Sync Gate

Before a meaningful increment is durable, evaluate without waiting for the user:

| Trigger | Mandatory persistent update |
|---|---|
| mode/phase/baseline/gate/blocker/test/review status changed | `PROJECT_STATE.md` |
| exact next scope/order changed | `NEXT_WORK_ITEM.md` |
| reusable optimization, discovery, tooling behavior, failure pattern, risk, clarification | `PROJECT_MEMORY.md` |
| persistence/document workflow improved | `GIT_WORKFLOW.md` + `PROJECT_MEMORY.md` |
| implementation progress changed | implementation status/remaining/traceability/evidence docs as applicable |
| source/artifact recovery status changed | `SOURCE_IMPORT_STATUS.md` + state/task docs |
| finding/validation failure changed | correct review/validation artifact + state |
| milestone or gate transition | new immutable checkpoint MD + JSON |

**No silent knowledge:** if a fresh chat would lose information that prevents duplicated work, a wrong decision, a repeated failure, wasted investigation, or safety/reproducibility regression, documentation sync is incomplete.

## 5. Evidence discipline

Every persistent claim must remain classified as one of:

- observed/tested fact;
- reviewed/approved decision;
- inference/hypothesis;
- proposed optimization;
- unresolved blocker.

Writing a claim into Markdown does not make it evidence. Author workspace tests are not Windows/WSL/LAB/SITE proof.

## 6. Commit/delivery sequence

1. Verify current `main` and canonical state.
2. Verify exact current source/artifact identity.
3. Work only in the active mode/work-item scope.
4. Run targeted author tests/evidence collection.
5. At a delivery boundary run full required author regression/static checks.
6. Run Documentation Sync Gate.
7. Review diff for unrelated changes or reviewed-contract drift.
8. Secret-scan all material intended for Git/artifact persistence.
9. If producing a binary delivery package, upload through a byte-preserving file-reference/raw-file action and raw-re-download/hash-verify it.
10. Commit/push GitHub source/state/docs/diffs that can be verified reliably.
11. Re-fetch/verify remote commit and relevant files.
12. Record external artifact identity in Git state/checkpoint.
13. Only then begin the next coherent increment.

## 7. Binary/tooling safety

Do not send a large binary archive through model-rendered text and call it exact. GitHub `create_blob(base64)` can be used only with per-blob identity verification; small 4 KiB chunks were proven exact during bootstrap, while larger/model-rendered payloads were not consistently safe. Prefer file-native connector operations.

Unreferenced experimental Git blobs are not project state. Never attach an unverified blob/tree to the canonical branch.

## 8. Branch and history policy

Current workflow uses `main` directly because this is a single-user implementation flow. Do not force-push or rewrite published history by default.

If parallel contributors, protected branches, CI requirements, or mandatory PRs are introduced later, record that as an explicit workflow change and update this file plus `PROJECT_MEMORY.md`.

## 9. CODE_REVIEW boundary

`CODE_REVIEW_PASS` may only be produced in CODE_REVIEW mode against the exact committed/addressable candidate. Before `CODE_REVIEW_HANDOFF_READY=true`:

- exact candidate source/diff must be reviewable;
- exact binary package, if used, must have a verified artifact identity;
- state/traceability/tests must refer to the same candidate;
- no hidden source-materialization blocker may prevent independent review.

Implementation commits/artifact uploads never self-approve code.

## 10. Cross-chat bootstrap

A new chat should:

1. read `PROJECT_STATE.md`;
2. read `NEXT_WORK_ITEM.md`;
3. read Active Memory Index/relevant `PROJECT_MEMORY.md` entries;
4. verify current GitHub `main` head;
5. read this workflow before persistent changes;
6. use `SOURCE_IMPORT_STATUS.md` to recover the exact binary/source baseline when needed;
7. verify artifact hashes before extraction/modification;
8. read current approved contracts/source docs needed by the work item.

Do not reconstruct an exact baseline from conversation prose when a verified artifact exists.
