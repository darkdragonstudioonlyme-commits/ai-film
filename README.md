# AI-FILM-SERVER

Persistent control plane for the single-chat AI film project. Current truth is `PROJECT_STATE.md`, not the newest-looking checkpoint or a previous chat. Product source is addressed by the exact source identity declared there; this branch is not the product runtime.

## Cold-start order

1. Fresh-fetch `main` and the relevant lane refs; preserve local WIP.
2. Read `PROJECT_STATE.md`, `NEXT_WORK_ITEM.md` and `WORKFLOW_ROUTER.md`.
3. Resolve the owning lane and existing run; reconcile before executing. Use the task-specific read profile in `DOCUMENTATION_MAP.md`.

## Minimal requests

```text
Tiếp tục.
```

```text
Review thiết kế MD → chỉnh sửa cần thiết → review → audit toàn bộ.
```

The first resumes verified state. The second is an explicit documentation excursion; it must preserve any blocked product run and its return point. Neither request grants permission to skip gates, change frozen contracts, spend money or perform host-destructive actions.

## Authority and evidence

`DOC-DESIGN → DOC-REVIEW → DOC-AUDIT` governs material documentation changes. Exact commits, evidence and role-specific verdicts determine acceptance. Same-chat role separation is not external independent certification. See `EXECUTION_LANES.md` and `GIT_WORKFLOW.md`.

`CHAT_HANDOFF.md` is the compact continuation entrypoint. `PROJECT_ROADMAP.md` orders gates; it does not own their current status. Historical checkpoints, designs and reviews preserve evidence, not a second mutable state.
