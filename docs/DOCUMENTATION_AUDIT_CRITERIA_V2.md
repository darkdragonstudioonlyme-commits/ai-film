# Documentation System V2 — Holistic Audit Criteria

DOC-AUDIT-V2 starts only after an exact candidate passed DOC-REVIEW-V2. It does not trust that PASS; it audits the **whole active documentation/control system**, including unchanged files and runtime state.

| ID | Audit question |
|---|---|
| D2A-01 | Can a cold chat resume from repository/workspace only, with no hidden transcript dependency? |
| D2A-02 | Are canonical state, fresh lane states, worktrees, dirty WIP and artifact hashes mutually consistent? |
| D2A-03 | Are any current version/dev numbers duplicated into policy/router/roadmap where they can go stale? |
| D2A-04 | Are obsolete/superseded rules still present in active operational docs? |
| D2A-05 | Does the test system remain business-first even when implementation and tests are changed together? |
| D2A-06 | Can a wrong test/harness/environment/design be distinguished from an implementation defect? |
| D2A-07 | Does repeated failure trigger process review and produce a return path instead of endless retry? |
| D2A-08 | Does self-learning actually alter policy/tooling when useful, while preserving contract authority? |
| D2A-09 | Is active memory compact enough to be read and are promoted/superseded details archived/pruned? |
| D2A-10 | Are server/environment claims honest about observation boundaries, freshness and tool provenance? |
| D2A-11 | Would model benchmark results be reproducible/comparable only under bound environment/model identities? |
| D2A-12 | Are all producer/consumer workflows independent, and can final audit find issues despite earlier review PASS? |
| D2A-13 | Are recovery/rollback paths available for state drift, broken governance, failed candidate and cold-chat recovery? |
| D2A-14 | Search for analogous blind spots not explicitly named above: stale caches, shared assumptions, hidden authority, mislabeled evidence, silent defaults, ambiguous ownership. |

The auditor must run the governance checks, inspect active docs for contradictions/duplication, fresh-fetch runtime state, inspect server snapshot, and attempt adversarial/cold-start scenarios. PASS is required before V2 promotion to `main`.
