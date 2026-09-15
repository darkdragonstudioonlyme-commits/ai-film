# Documentation System V2 R7 — Detailed Review Criteria

DOC-REVIEW-R7 consumes an immutable design commit and must not edit it. PASS requires all:

1. V27 Markdown and V27 JSON agree on state version, mode, active workflow and documentation release.
2. `runtime_reconciliation` has stable schema and correctly represents reviewed-clean dev19: both heads exact, dirty set empty, package identity exact.
3. `check_project_docs.py` does not require WIP/promotion/review markers from one historical state.
4. `check_runtime_state.py` selects current JSON by `STATE_VERSION`, fresh-fetches lane refs, validates heads/dirty/package/lane tokens, and distinguishes `CHECKER_DRIFT` from `STATE_DRIFT`.
5. holistic audit detects hard-coded package/checkpoint/review IDs and lifecycle-specific WIP markers in checker source.
6. recovery/router/docs-map/Git policy describe `CHECKER_DRIFT` and Markdown+JSON lockstep.
7. source IMPLEMENT/REVIEW worktrees remain exact dev19 and clean.
8. R7 does not alter Phase00 contracts/gates or falsely mark CR-P00-001 closed.
