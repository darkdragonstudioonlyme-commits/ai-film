# Continue Protocol v2

1. Read RESUME.md, BACKLOG.yaml and MILESTONES.md. Do not cold-start from historical P00 state.
2. Fetch refs and preserve unrelated worktrees/WIP.
3. Review any unreviewed product diff/test result first; fix once if needed.
4. Select a small batch of READY tasks that advances the earliest incomplete milestone.
5. Execute independent tasks in parallel when safe. Prefer code/artifact deltas over process documents.
6. If one task blocks, record the blocker and continue another READY task. Do not create a recursive governance loop.
7. Heavy gates apply only to destructive cleanup, publication, secrets/rights changes, schema migrations, or bounded paid-resource approval.
8. End the turn by updating BACKLOG, RESUME, milestone checkboxes and one PROGRESS_LOG.jsonl record.
9. A normal turn should produce product/code/test/benchmark delta. Two consecutive no-delta turns trigger a workflow correction.
10. Every 10 turns compute task/turn, no-delta turns, cost/task and recurring blockers; keep only changes that improve a measured KPI.
11. If a paid Pod is RUNNING, end the turn with a useful batch running or with media synced and an explicit stop/keep decision.
12. Budget guard uses paid RUNNING intervals plus known storage/transfer; execution cost is a secondary metric, not the cap basis.
13. Binary media is available only after sync off an ephemeral/root-only Pod; blind mapping must not be committed publicly before scoring.
14. Review prose by batch, not by individual runner/job; keep per-job evidence in machine-readable receipts.

Historical Phase00 material remains evidence at archive ref archive/p00-governance-2026-09-24 and is not the active router.
