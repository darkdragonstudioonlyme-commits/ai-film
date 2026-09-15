# AI-FILM-SERVER Git Persistence Workflow

This repository is the persistent cross-chat handoff for AI-FILM-SERVER.

## Mandatory rule

A coherent implementation increment is not considered durable until it has been tested, documented, committed, pushed, and the remote commit SHA has been verified.

## Commit sequence

1. Verify current `PROJECT_STATE.md`, `NEXT_WORK_ITEM.md`, approved contracts, branch, and remote head.
2. Implement only the current mode/work-item scope.
3. Run targeted author tests while developing.
4. Before a delivery commit, run the full workspace regression and static checks appropriate to the current authoring environment.
5. Update source, tests, docs, evidence, `PROJECT_STATE.md`, `NEXT_WORK_ITEM.md`, and the latest state/checkpoint files.
6. Inspect the diff for accidental unrelated changes.
7. Run a secret scan. Never commit real credentials, private keys, tokens, private customer material, licensed private assets, or production secrets.
8. Commit with a message that identifies the work item and coherent increment.
9. Push to GitHub.
10. Re-fetch/verify the remote commit SHA and relevant files.
11. Record the verified SHA in `PROJECT_STATE.md` at the next state update.
12. Only then begin the next coherent increment.

## Default branch policy

Current repository initialization uses `main` directly because the project is in a single-user implementation phase. Do not force-push or rewrite published history.

If later work introduces parallel contributors, CI requirements, protected branches or mandatory pull requests, that must be introduced explicitly as a project workflow decision; do not silently change the development model.

## Commit granularity

Prefer one commit per coherent, tested implementation increment. Examples:

- `feat(p00): complete executable trust integration`
- `feat(p00): add pre-C3 checkpoint evidence selection`
- `test(p00): complete causal lifecycle controller cases`
- `docs(state): checkpoint IMPL-P00-001 dev7`

A delivery may contain more than one commit, but the final delivery commit must update the canonical state so a new chat can identify the exact remote head and work status.

## Required state recorded after each delivery

`PROJECT_STATE.md` should include:

- repository and branch;
- latest verified remote commit SHA;
- current mode and phase;
- current work item;
- reviewed design baseline;
- current source/delivery version;
- author-complete boolean;
- test/static results;
- native/LAB/SITE execution status;
- open findings/design gaps/validation failures;
- open implementation REM items/blockers;
- exact next action and next mode;
- snapshot/hash if an exact archive is produced.

## Cross-chat startup

A new chat must not infer state from old conversation history. It should:

1. read `PROJECT_STATE.md`;
2. read `NEXT_WORK_ITEM.md`;
3. inspect latest `main` commit;
4. read authoritative contracts referenced by the state;
5. verify the source/snapshot identity;
6. continue only the recorded active work item and mode.

## Code-review boundary

Implementation commits are not review approval. `CODE_REVIEW_PASS` can only be produced in `CODE_REVIEW` mode after reviewing the exact committed candidate. If fixes are required, use the project mode state machine (`PATCH` or the directed implementation path) and commit/push the fixes before re-review.

## Native evidence boundary

Author workspace tests, fixture controllers and static checks are not Windows/WSL/LAB/SITE validation evidence. Git persistence must preserve this distinction in every state file.
