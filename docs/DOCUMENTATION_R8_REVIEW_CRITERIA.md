# Documentation R8 detailed review criteria

1. One active RUN_ID per workflow/base; no timeout TTL abandonment.
2. Write-ahead INTENT/COMPLETE semantics make hard timeout observable.
3. Resume probes exact outputs and reuses completed steps.
4. `NEXT_WORK_ITEM` includes full workflow-instance contract and explicit step cursor.
5. Current dev20 interruption resumes at S07 and does not rebuild verified S06 or claim review/native PASS.
6. Continuity state cannot grant global gate authority.
7. Runtime/continuity checker distinguishes bound in-flight-ahead output from unknown STATE_DRIFT.
8. Documentation governance DESIGN/REVIEW/AUDIT branch/worktree identity is release-selected from canonical state; standing policy contains no stale generic fixed branch/worktree names.
9. Promotion-ready state/checkpoint predeclare exact final detailed-review/audit IDs and record paths; only those immutable records may be added after final audit without reopening review/audit.
10. Self-learning distinguishes persisted/reviewed from canonically activated; activation target/status/blocker are present and workflow health tracks activation lag/backlog.
11. Source durability and source visibility are separate: dev20 partial snapshot is explicitly non-authoritative, full-mirror status is false, exact source/package identity remains primary.
12. `tools/check_documentation_governance.py` enforces release-selection/promotion/activation/source-visibility invariants without hard-coding a future release commit SHA.
13. Source IMPLEMENT/REVIEW worktrees remain unmodified by documentation review.
