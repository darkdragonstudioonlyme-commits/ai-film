# Documentation R8 detailed review criteria

1. One active RUN_ID per workflow/base; no timeout TTL abandonment.
2. Write-ahead INTENT/COMPLETE semantics make hard timeout observable.
3. Resume probes exact outputs and reuses completed steps.
4. `NEXT_WORK_ITEM` includes full workflow-instance contract and explicit step cursor.
5. Current dev20 interruption resumes at S06 and does not claim review/native PASS.
6. Continuity state cannot grant global gate authority.
7. Runtime/continuity checker distinguishes bound in-flight-ahead output from unknown STATE_DRIFT.
8. Source IMPLEMENT/REVIEW worktrees remain unmodified by documentation review.
