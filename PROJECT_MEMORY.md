# AI-FILM-SERVER — Active Project Memory Index

Reusable knowledge only. Learning process: `SELF_LEARNING.md`. Active operating rules: `POLICY_REGISTRY.md`. Current state is not stored here. Detailed historical reasoning remains in Git/review records.

## Active reusable lessons

| ID | Type | Active lesson | Promoted to |
|---|---|---|---|
| MEM-20260915-002 | TOOLING | Exact baselines require byte-preserving transfer + independent identity verification. | `GIT_WORKFLOW.md` |
| MEM-20260915-003 | TESTING | Author/review tests are not native LAB/SITE proof. | `TEST_STRATEGY.md` |
| MEM-20260915-015 | TESTING | Keep run evidence outside candidate source; restore generated tracked evidence. | workspace/test policy |
| MEM-20260915-021 | SECURITY | Re-authorize before durable recovery-state mutation after observation. | implementation rule |
| MEM-20260915-024 | PROCESS | Producer/reviewer require separate mutable/immutable workspaces. | `EXECUTION_LANES.md` |
| MEM-20260915-025 | REVIEW | Review target identity must never float. | `EXECUTION_LANES.md` |
| MEM-20260915-028 | TOOLING | Fresh-fetch refs before trusting remote lane state. | `GIT_WORKFLOW.md` |
| MEM-20260915-029 | PROCESS | Durable candidate, WIP and review target are distinct state. | `DOCUMENTATION_MAP.md` |
| MEM-20260915-033 | TOOLING | Preserve Git porcelain XY columns; whole-output strip can corrupt paths. | checker/tooling rule |
| MEM-20260915-034 | PROCESS | State/lane/worktree mismatch is `STATE_DRIFT`, never a tie to guess. | router/recovery checker |
| MEM-20260915-035 | TESTING | Reviewed business behavior owns test oracle; current code never does. | `TEST_STRATEGY.md` |
| MEM-20260915-036 | PROCESS | Repeated ineffective patch loops are workflow-health evidence and trigger meta-review. | `WORKFLOW_HEALTH.md` |
| MEM-20260915-037 | GOVERNANCE | Obsolete policy must be retired/superseded out of active guidance, not accumulated forever. | `POLICY_REGISTRY.md` |
| MEM-20260915-038 | ENVIRONMENT | Model/performance claims bind an exact observed environment; NOT_VISIBLE is not absence. | `SERVER_ENVIRONMENT.md`, `MODEL_EVALUATION.md` |
| MEM-20260915-039 | LEARNING | Learning is complete only when future behavior/detection improves and recurrence is measured. | `SELF_LEARNING.md` |
| MEM-20260915-040 | RECOVERY | Preserve WIP/evidence before repair; recovery returns to a verified decision point. | `RECOVERY_PLAYBOOK.md` |
| MEM-20260915-041 | TOOLING | Checkers must parse current identity from canonical state; hard-coded delivery versions become drift bugs. | checker policy |
| MEM-20260915-042 | PROCESS | Workspace/tool docs must not duplicate mutable candidate/version/test state owned by PROJECT_STATE/NEXT_WORK_ITEM. | documentation audit/checker |
| MEM-20260915-043 | ENVIRONMENT | Environment digest inputs must be explicit and exclude the digest itself; preserve the canonical payload. | environment record schema/checker |
| MEM-20260915-044 | GOVERNANCE | Immutable environment/model results need separate record domains; methodology files must not become history logs. | `environments/`, `model-evaluations/` |
| MEM-20260915-045 | LEARNING | Compact active memory requires durable standalone learning records when no review/health record already owns provenance. | `learning/` |
| MEM-20260915-046 | PROCESS | Worktree existence must not be described as current workflow activity; mutable activity belongs to PROJECT_STATE/lane state. | workspace audit/checker |
| MEM-20260915-047 | GOVERNANCE | Promotion state/checkpoint must be inside the exact reviewed/audited tree; post-audit policy/state edits reopen review. | documentation promotion policy/checker |
| MEM-20260915-048 | REVIEW | Causal controller action→route binding belongs to the reviewed procedure authority/digest; post-run evidence may prove the mapping but must never choose it. | native harness procedure/review rule |

## Compaction rule

This file stays an active index. When entries are superseded or detailed prose becomes redundant, remove obsolete instructions from the active file after recording successor/provenance in Git or an immutable review/health record. Do not preserve stale guidance just to keep the file large.

New learning uses the record/score/promotion lifecycle in `SELF_LEARNING.md`.
