# Workflow run ledgers

The **live mutable** record for an active run lives only on the owning lane branch at `workflow-runs/<RUN_ID>.md`; `LANE_STATE.md` points to it. `main` may hold immutable milestone/migration snapshots under `workflow-runs/snapshots/`, but those never override the fresh lane record.

Each live run record binds `RUN_ID`, `WORKFLOW_ID`, owner lane, base identity, current step, step states, exact outputs, idempotency/replay policy and return route. One active run per workflow/base is allowed. Git history preserves prior updates; a completed run may be summarized on `main`.
