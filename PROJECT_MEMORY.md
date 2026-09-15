# AI-FILM-SERVER — PROJECT MEMORY

> Living reusable knowledge. Current truth lives in `PROJECT_STATE.md`; next execution lives in `NEXT_WORK_ITEM.md`; lane protocol lives in `EXECUTION_LANES.md`.

## No-silent-knowledge rule

Reusable discoveries, optimizations, tooling limitations, failure patterns, security/test lessons and clarifications must be persisted before the related increment is durable. Memory does not approve architecture or pass gates.

Older detail is preserved in Git history and memory archive pointers.

## Active Memory Index

| ID | Type | Reusable rule |
|---|---|---|
| MEM-20260915-001 | PROCESS | Separate current state, next work, reusable knowledge and immutable history. |
| MEM-20260915-002 | TOOLING | Exact baselines require byte-preserving transport plus independent identity verification. |
| MEM-20260915-003 | TESTING | Author regression/static checks are not Windows/WSL/LAB/SITE proof. |
| MEM-20260915-004 | PROCESS | An increment is durable only after remote artifact/state verification. |
| MEM-20260915-005 | SECURITY | Secret-scan every public-repo delivery; never persist real credentials/private assets. |
| MEM-20260915-006 | TOOLING | Prefer file-reference/raw-file actions for binary delivery artifacts. |
| MEM-20260915-007 | PROCESS | Hybrid persistence is valid when Git state and exact binary artifact roles are explicit. |
| MEM-20260915-008 | LESSON | Explicit missing state is safer than accepting non-identical bytes. |
| MEM-20260915-009 | TOOLING | If chunking is unavoidable, verify every Git blob SHA individually; prefer file-native transfer. |
| MEM-20260915-010 | TESTING | Respect src-layout/official runner; missing `PYTHONPATH=src` is not a source regression. |
| MEM-20260915-011 | SECURITY | Executable trust binds path + exact bytes + policy + pinned handle + witness before resume. |
| MEM-20260915-012 | TOOLING | Use `/home/dragon/ai-film-dev`; verify delivery hash before extraction. |
| MEM-20260915-013 | TOOLING | No-pip venv + `.pth` is valid only while dependencies remain empty. |
| MEM-20260915-014 | PROCESS | Local Git and remote write authentication are separate; avoid hanging interactive helpers. |
| MEM-20260915-015 | TESTING | Save run evidence outside source and restore tracked generated evidence so verification stays clean. |
| MEM-20260915-016 | LIFECYCLE | Native process completion is not lifecycle completion; observed pending reboot retains a durable wait. |
| MEM-20260915-017 | RECOVERY | Reboot resume needs changed boot witness + cleared pending state before commit. |
| MEM-20260915-018 | PROCESS | Missing owner postcheck is an owner wait only from an existing operator-wait fence. |
| MEM-20260915-019 | DESIGN | Keep reviewed final owner-planned restart; engine-required reboot does not satisfy T00-05 alone. |
| MEM-20260915-020 | REVIEW | Early review of explicitly partial candidate must FAIL; tests do not make missing scope reviewable. |
| MEM-20260915-021 | SECURITY | Durable recovery-state change after observation needs renewed authority immediately before persistence. |
| MEM-20260915-022 | OBSERVABILITY | Persist a bounded typed representation/digest of actual observations that cause durable lifecycle waits. |
| MEM-20260915-023 | RESOURCE | Durable wait context needs exact schemas and size/privacy bounds. |
| MEM-20260915-024 | PROCESS | IMPLEMENT and REVIEW must use separate worktrees/permissions; REVIEW never patches candidate source. |
| MEM-20260915-025 | REVIEW | Candidate handoff is an immutable identity tuple; REVIEW never follows IMPLEMENT branch head implicitly. |
| MEM-20260915-026 | TESTING | Separate lane evidence directories prevent review reruns from contaminating implementation evidence/diffs. |

## Current CODE_REVIEW lessons

### MEM-20260915-020 — Passing tests do not make a partial candidate review-ready

Dev8 reproduced 683 PASS + 92 static but declared `AUTHOR_COMPLETE=false` with required source scope open. Full gate review therefore failed. Test success evaluates existing code, not missing code.

### MEM-20260915-021 — Re-authorize immediately before durable recovery-state changes

A potentially long observation can outlive its admitting authority. Before persisting a recovery/fence state change, re-check current authority, generation, actor/request and exact fence identity.

### MEM-20260915-022 — Persist actual cause of derived lifecycle waits

When a durable lifecycle state is derived from actual observations such as pending reboot, persist a safe typed observation/digest sufficient to audit/reconcile the derivation rather than only the conclusion.

### MEM-20260915-023 — Durable wait context is typed/bounded data

Journaled wait metadata requires exact allowed keys/types and canonical size/privacy limits. Raw or sensitive evidence belongs behind protected references/digests.

## Dual-lane execution lessons

### MEM-20260915-024 — Separate mutable implementation from immutable review

```yaml
TYPE: PROCESS
STATUS: ACTIVE
DISCOVERED_IN: {MODE: IMPLEMENTATION, PHASE: "00 — Host / WSL", WORK_ITEM: IMPL-P00-001}
SUMMARY: "Implementation and review lose independence when they share one mutable source worktree."
EVIDENCE: "Created `/home/dragon/ai-film-dev/implement` on writable branch `impl/p00` and `/home/dragon/ai-film-dev/review` detached at exact dev8 commit c44c2f87...; both independently reproduce 683 PASS + 92 static."
REUSABLE_RULE: "IMPLEMENT edits only its writable worktree. REVIEW consumes a detached exact candidate and never patches it. Project gates remain controlled by canonical main state."
ACTION_TAKEN: "Created remote lane branches `lane/implement-p00` and `lane/review-p00`, local worktrees and `EXECUTION_LANES.md`."
```

### MEM-20260915-025 — Review target identity must never float

```yaml
TYPE: REVIEW
STATUS: ACTIVE
DISCOVERED_IN: {MODE: IMPLEMENTATION, PHASE: "00 — Host / WSL", WORK_ITEM: IMPL-P00-001}
SUMMARY: "A reviewer following an implementation branch head can silently review code different from the handed-off candidate."
EVIDENCE: "REVIEW worktree is detached at exact dev8 source commit while IMPLEMENT branch may advance independently."
REUSABLE_RULE: "Handoff binds source commit SHA + package SHA/size/artifact ID + source/test digests + author evidence + contract digest. REVIEW never auto-follows IMPLEMENT branch head."
ACTION_TAKEN: "Defined immutable candidate contract in EXECUTION_LANES.md and lane state files."
```

### MEM-20260915-026 — Evidence output is lane-scoped

```yaml
TYPE: TESTING
STATUS: ACTIVE
DISCOVERED_IN: {MODE: IMPLEMENTATION, PHASE: "00 — Host / WSL", WORK_ITEM: IMPL-P00-001}
SUMMARY: "Implementation and review reruns need separate evidence destinations to avoid overwriting or confusing provenance."
EVIDENCE: "`lane-test.sh implement` and `lane-test.sh review` store outputs under separate `run-evidence/<lane>/<UTC>/` paths and restore tracked generated evidence before final status."
REUSABLE_RULE: "Keep author and reviewer execution evidence in separate lane-scoped directories and bind review claims to the candidate identity."
ACTION_TAKEN: "Added lane-specific environment/test helpers."
```

## Future-chat usage

1. Read `PROJECT_STATE.md`, `NEXT_WORK_ITEM.md`, then `EXECUTION_LANES.md`.
2. Choose one lane from the requested task and read that branch's `LANE_STATE.md`.
3. Read relevant memory entries and `WORKSPACE_WSL.md`.
4. Never mix IMPLEMENT and REVIEW permissions inside one increment.
5. Persist any new reusable lesson automatically before the increment is durable.
