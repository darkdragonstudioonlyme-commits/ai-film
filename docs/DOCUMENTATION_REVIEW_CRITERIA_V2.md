# Documentation System V2 — Detailed Review Criteria

DOC-REVIEW-V2 reviews an immutable DOC-DESIGN-V2 commit and must not edit it.

| ID | Requirement |
|---|---|
| D2R-01 | Cold-start identifies global state, WIP, review target, current governance workflow and exact next action without transcript history. |
| D2R-02 | `continue` routing preserves WIP and deterministically selects the owning workflow. |
| D2R-03 | Test oracles are explicitly business/contract/review-derived; source code is never the oracle. |
| D2R-04 | Test expectation changes require classification and cannot be justified by “make tests pass”. |
| D2R-05 | Test wrapper checks policy/runtime identity before low-level execution and never adds native execution implicitly. |
| D2R-06 | Deadlock/inefficiency/repeated-error/user-correction triggers cause retrospective before blind retry. |
| D2R-07 | Learning has a promotion path to policy/tooling and a pruning path for superseded/promoted detail. |
| D2R-08 | Policy/know-how/architecture/state/history classes have distinct owners and authority. |
| D2R-09 | Server environment is measured, timestamped/fingerprinted, tool provenance is explicit, and model readiness fails closed. |
| D2R-10 | Mutable dev/version identifiers do not appear in version-agnostic policy/router/roadmap docs. |
| D2R-11 | IMPLEMENT/REVIEW and DOC-DESIGN/DOC-REVIEW/DOC-AUDIT boundaries use immutable handoffs and independent permissions. |
| D2R-12 | Governance scripts/checkers pass and review worktree stays unchanged. |

PASS requires all D2R-01…12. Findings return to DOC-DESIGN-V2 and require a new immutable candidate.
