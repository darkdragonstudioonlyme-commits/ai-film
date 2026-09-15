# Documentation System V2 R8 — Workflow Continuity Design

## Effectiveness finding

V2 R6 was effective at state-drift detection, independent producer/reviewer separation, business-first test authority, policy pruning and self-learning. Recent work exposed three remaining process weaknesses:

1. continuity was synchronized mainly at workflow/chat boundaries, so an interruption after useful local progress but before lane/main sync could hide newer exact producer output;
2. documentation governance standing prose pinned branch/worktree names even though governed revisions are release-scoped;
3. a learning could be correctly persisted/reviewed yet remain operationally inactive while promotion is incomplete, creating a learned-but-not-active backlog.

The motivating continuity incident left canonical `main`/IMPLEMENT state on dev19 while the IMPLEMENT worktree was clean at dev20 commit `51c9d3f...` with author tests/static checks already complete. Subsequent continuation proved the continuity design useful: the same run resumed at S06, produced and verified the exact dev20 package, then advanced to S07 without repeating S01–S05.

A second observed friction was source visibility: exact local source + verified package preserved identity, but GitHub still did not expose the implementation tree to a reader. A partial review snapshot improved browseability but is not a full source mirror and must never be represented as one.

## R8 correction

R8 introduces `WORKFLOW_CONTINUITY.md` and lane-owned write-ahead run ledgers. One logical `RUN_ID` owns a workflow/base. Material steps persist `INTENT` before execution and `COMPLETE` with exact output identity afterward. Hard timeout therefore leaves a machine-readable recovery boundary. New chats reconcile and adopt the same run instead of creating a replacement workflow.

R8 also:

- distinguishes `IN_FLIGHT_AHEAD_OF_CANONICAL` from unbound `STATE_DRIFT`;
- defines idempotency/replay policies and exact-output reuse;
- machine-enforces the router's `NEXT_WORK_ITEM` workflow-instance contract;
- promotes R7's useful lifecycle-neutral checker lesson without activating the unpromoted R7 release;
- makes documentation governance branch/worktree identity release-selected from `PROJECT_STATE`, not hard-coded in standing policy;
- predeclares final review/audit IDs and immutable record paths in the promotion-ready state tree; after audit only those verdict records may be added before promotion;
- adds self-learning activation closure: reviewed learning is not counted as applied until its policy/tool/checker release is active, or it is explicitly blocked with an owner/return path;
- adds source-visibility status to delivery/handoff reasoning: partial snapshots are labeled non-authoritative, while exact source/package identity remains explicit;
- adds duplicate-run, interruption, learning-activation-lag and visibility-friction metrics/meta-review triggers.

## Non-goals and authority boundaries

R8 changes project workflow/documentation governance only. It does not change Phase00 product contracts, source behavior, native validation status, code-review verdicts or host-readiness gates. Producer source visibility never grants review authority; a browse snapshot cannot substitute for an exact immutable candidate identity.

## Promotion contract

The exact final R8 design commit must contain the intended post-promotion `PROJECT_STATE`, checkpoint, policy and checker state. The canonical state predeclares the final detailed-review and holistic-audit record IDs/paths. After the final audit, promotion may add only those predeclared immutable verdict records; any other policy/state/checkpoint change reopens detailed review and holistic audit.
