# Documentation System V2 R8 — Workflow Continuity Design

## Effectiveness finding

V2 R6 was effective at state-drift detection, independent producer/reviewer separation, business-first test authority, policy pruning and self-learning. Recent work showed one material weakness: continuity was synchronized mainly at workflow/chat boundaries, so an interruption after useful local progress but before lane/main sync could leave a newer exact output invisible to the next chat.

Observed incident: canonical `main` and the IMPLEMENT lane still described dev19 at `2ac37ac...`, while the IMPLEMENT worktree was clean at dev20 commit `51c9d3f...` with 760 author tests and 101 static checks already completed. The existing runtime checker correctly failed closed, but it had no run/step identity to prove the newer output was resumable producer progress rather than unknown drift.

## R8 correction

R8 introduces `WORKFLOW_CONTINUITY.md` and lane-owned write-ahead run ledgers. One logical `RUN_ID` owns a workflow/base. Material steps persist `INTENT` before execution and `COMPLETE` with exact output identity afterward. Hard timeout therefore leaves a machine-readable recovery boundary. New chats reconcile and adopt the same run instead of creating a replacement workflow.

R8 also:
- distinguishes `IN_FLIGHT_AHEAD_OF_CANONICAL` from unbound `STATE_DRIFT`;
- defines idempotency/replay policies and exact-output reuse;
- machine-enforces the router's `NEXT_WORK_ITEM` workflow-instance contract;
- promotes R7's useful lifecycle-neutral checker lesson without activating the unpromoted R7 release;
- records the current dev20 interrupted run and resumes at packaging rather than repeating completed residual audit/tests/commit;
- adds duplicate-run/interruption metrics and meta-review triggers.

No Phase00 product contract, source behavior, native test status or review verdict is changed by R8.
