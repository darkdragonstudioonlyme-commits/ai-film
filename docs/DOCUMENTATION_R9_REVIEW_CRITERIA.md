# Documentation R9 detailed review criteria

1. `learning/LEARNING_STATE.json` is the single current lifecycle owner; immutable `learning/LEARNING-*.md` files are provenance, not mutable status authority.
2. Every durable active learning record is represented exactly once in the lifecycle register; no orphan or duplicate entry exists.
3. `tools/check_learning_lifecycle.py` validates register schema, record identity, documentation-release binding, review/activation/effectiveness transitions, successor requirements and project aggregate equality.
4. Current-release learnings cannot remain silently `PENDING_ACTIVATION`/`BLOCKED`; promotion-conditional states are allowed only with predeclared final review/audit evidence paths.
5. `ACTIVE` requires activation evidence. `EFFECTIVE` requires effectiveness evidence. `INEFFECTIVE` requires a successor/meta-review path.
6. Pending effectiveness measurement uses a structured machine-readable gate; pending is distinct from overdue and `OVERDUE_EFFECTIVENESS_MEASUREMENT` is derived from current state version.
7. `PROJECT_STATE` owns only derived learning aggregates and they machine-match the register: pending activation, unresolved ineffective, pending measurement and overdue measurement.
8. Fresh-session bootstrap runs learning lifecycle reconciliation before final routing; lifecycle drift, unresolved ineffectiveness or overdue measurement reaches `WORKFLOW_HEALTH`/DOC-DESIGN.
9. Guarded automation may detect/propose/route, but cannot self-review, self-audit or self-promote a policy/design correction.
10. Existing R8 lessons are reconciled: CONTROL, CONTINUITY and SOURCE_VISIBILITY are effective; DOCSYS_ACTIVATION is historically ineffective with successor `LEARNING-LIFECYCLE-CONSISTENCY-002`.
11. The R9 successor is `PENDING_MEASUREMENT` with a structured V36 gate and `OVERDUE_EFFECTIVENESS_MEASUREMENT=0` in promotion-ready V33.
12. `POL-LEARN-001` is superseded by `POL-LEARN-002`; active guidance has one learning-policy owner.
13. Documentation governance/audit invokes the dedicated lifecycle checker; lifecycle inconsistency cannot PASS because policy prose merely contains activation keywords.
14. Adversarial checker tests reject stale current-release activation, ineffective-without-successor, aggregate drift, effective-without-evidence, missing activation evidence and overdue-measurement aggregate drift.
15. No Phase00 source/product test/native validation authority changes are introduced.
16. Current `RUN-P00-VALIDATION-001/V02` continuity and validation blocker are preserved exactly; documentation work does not restart or advance the native run.
17. Promotion-ready state/checkpoint predeclare exact final R9 detailed-review/audit IDs and immutable record paths; after final audit only those verdict records may be added before main promotion.
18. Source IMPLEMENT/REVIEW/VALIDATION worktrees and runtime/LAB authority state remain unmodified by documentation review.
