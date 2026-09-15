# Documentation System V2 — Detailed Review Criteria

DOC-REVIEW-V2 reviews an immutable DOC-DESIGN-V2 commit and must not edit it.

| ID | Acceptance criterion |
|---|---|
| V2-R01 | Test authority is business/contract-first and explicitly independent of implementation code. |
| V2-R02 | Test-script changes distinguish business change from harness bug and cannot weaken oracles silently. |
| V2-R03 | Workflow health/deadlock triggers and deterministic meta-review route exist. |
| V2-R04 | Policy lifecycle supports deprecation/supersession/retirement and active-doc pruning. |
| V2-R05 | Server environment facts distinguish observed/unknown/not-visible and bind benchmarks. |
| V2-R06 | Model evaluation defines reproducible environment/model/test identities and resource/quality metrics. |
| V2-R07 | Self-learning has observe→generalize→promote→review→measure→retire lifecycle. |
| V2-R08 | Recovery covers context loss, state drift, dirty WIP, missing artifacts and repeated failures. |
| V2-R09 | Documentation map/router/git/lane docs integrate the new policies without duplicate authority. |
| V2-R10 | Automated docs checks detect missing/stale/version-pinned active guidance where possible. |
| V2-R11 | Existing implementation/review WIP is preserved; documentation work does not mutate source candidate. |

PASS requires all criteria pass.
