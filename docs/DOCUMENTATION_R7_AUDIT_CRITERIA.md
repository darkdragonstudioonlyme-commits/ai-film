# Documentation System V2 R7 — Holistic Audit Criteria

Run only after detailed R7 review PASS. Audit the full active control plane, not just R7 diff.

Audit must verify:
- no active standing doc/checker pins a stale dev package, checkpoint version, review ID or transient WIP marker as universal schema;
- current V27 state/snapshot/checkpoint and freshly fetched lane/worktree identities reconcile;
- state kinds can transition WIP → handed-off → reviewed-fail → reviewed-clean residual audit without checker source edits while reconciliation schema remains unchanged;
- branch/worktree policy is release-scoped rather than pointing fresh chats at retired governance lanes;
- `CHECKER_DRIFT` recovery cannot mutate valid source state just to make tools green;
- R7 review verdict binds exact target and review source was unchanged;
- final promotion tree is already V27/R7 and only predeclared verdict records may be added after audit;
- source dev19 review result and CR-P00-001 remain unchanged.
