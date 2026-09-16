# Documentation R9 detailed review criteria

1. `learning/LEARNING_STATE.json` is the single current lifecycle owner; immutable `learning/LEARNING-*.md` files are provenance, not mutable status authority.
2. Every durable active learning record is represented exactly once in the lifecycle register; no orphan or duplicate entry exists.
3. `tools/check_learning_lifecycle.py` validates register schema, record identity, review/activation/effectiveness transitions, successor requirements and project aggregate equality.
4. Current-release learnings cannot remain silently `PENDING_ACTIVATION`/`BLOCKED`; promotion-conditional states are allowed only with predeclared final review record paths.
5. `EFFECTIVE` requires evidence; `INEFFECTIVE` requires a successor/meta-review path; pending measurement is explicit rather than silently counted as effective.
6. `PROJECT_STATE` owns only derived learning aggregates and they machine-match the register.
7. Fresh-session bootstrap runs learning lifecycle reconciliation before final routing; lifecycle drift or unresolved learning debt reaches `WORKFLOW_HEALTH`/DOC-DESIGN.
8. Guarded automation may detect/propose/route, but cannot self-review, self-audit or self-promote a policy/design correction.
9. Existing R8 lessons are reconciled: CONTROL, CONTINUITY and SOURCE_VISIBILITY are effective; DOCSYS_ACTIVATION is historically ineffective with successor `LEARNING-LIFECYCLE-CONSISTENCY-002`.
10. `POL-LEARN-001` is superseded by `POL-LEARN-002`; active guidance has one learning-policy owner.
11. Documentation/audit governance checker runs the dedicated lifecycle checker; lifecycle inconsistency cannot PASS because policy prose merely contains activation keywords.
12. No Phase00 source/product test/native validation authority changes are introduced.
13. Current `RUN-P00-VALIDATION-001/V02` continuity and validation blocker are preserved exactly; documentation work does not restart or advance the native run.
14. Promotion-ready state/checkpoint predeclare exact final R9 detailed-review/audit IDs and immutable record paths; after final audit only those verdict records may be added before main promotion.
15. Source IMPLEMENT/REVIEW/VALIDATION worktrees and runtime/LAB authority state remain unmodified by documentation review.
