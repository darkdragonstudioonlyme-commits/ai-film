# Documentation System V2 R7 — Lifecycle-Aware Reconciliation Design

## Trigger

V26 was a valid reviewed-clean residual-audit state, but R6 checkers still required V22-specific WIP/promotion markers and Markdown fields. The verifier generated false `DOCS_CHECK_FAIL` / `STATE_DRIFT` despite matching source/lane identities.

## Design correction

1. `PROJECT_STATE.md` keeps concise human current truth and a stable `RUNTIME_RECONCILIATION` summary.
2. `STATE_VERSION` selects `AI_FILM_PROJECT_STATE_Vn.json`, which contains structured `runtime_reconciliation`.
3. Runtime reconciliation schema binds `state_kind`, IMPLEMENT/REVIEW HEADs, exact dirty set, optional package identity and required freshly fetched lane tokens.
4. Checkers dynamically select the current versioned JSON/checkpoint and no longer require one WIP/review/package version.
5. `STATE_DRIFT` means real identity disagreement; `CHECKER_DRIFT` means verifier/schema assumptions do not model an otherwise valid state.
6. Every state update writes Markdown + matching JSON atomically.

## Promotion-ready state

R7 candidate already contains V27 human state, JSON state and checkpoint. Promotion is allowed only after exact `DOC-V2-R7-REVIEW-001` and `DOC-V2-R7-AUDIT-001` PASS records. Final main promotion may add those verdict artifacts but no post-audit state/policy/checker edit.

## Non-goals

R7 changes no Phase00 FD/D00/public behavior, closes no source finding, and does not turn checker PASS into implementation/native evidence. After promotion, routing returns to `WF-P00-IMPL-CR001-RESIDUAL-AUDIT`.
