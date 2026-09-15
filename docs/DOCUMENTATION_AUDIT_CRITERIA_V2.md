# Documentation System V2 — Holistic Audit Criteria

DOC-AUDIT-V2 runs only after DOC-REVIEW-V2 PASS. It reviews the entire active project-control documentation set, not just changed files.

Audit categories:

1. **Truth conflicts** — multiple active owners for one mutable fact.
2. **Version drift** — stale dev/version/commit/path references in active guidance.
3. **Dead policy** — obsolete rules still presented as active.
4. **Bloat/duplication** — repeated explanations that reduce discoverability.
5. **Circular trust** — producer output accepted because producer labels it PASS.
6. **Code-driven tests** — expected behavior sourced from current implementation.
7. **Environment ambiguity** — benchmark/model claims without exact environment identity.
8. **Learning without effect** — memory entries with no future detector/policy/action when recurrence warrants one.
9. **Recovery gaps** — a fresh chat cannot preserve or resume WIP after common failures.
10. **Workflow deadlock** — return paths ambiguous or two workflows wait on each other.
11. **Checker brittleness** — hard-coded versions/artifact names that will become stale.
12. **Historical leakage** — snapshot/history text accidentally used as current truth.

Audit must cold-start from repository + prepared workspace, fresh-fetch refs, run checkers, search active Markdown for stale version/commit patterns, verify policy ownership, and confirm implementation/review source worktrees remain unchanged.

PASS means no BLOCKER/HIGH audit findings and any MEDIUM findings have an explicit accepted remediation or are fixed and re-audited.
