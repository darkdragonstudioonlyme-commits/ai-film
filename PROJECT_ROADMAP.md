# AI-FILM-SERVER — Project Roadmap

## Authority

The Blueprint chain is `DESIGN → DESIGN_REVIEW → IMPLEMENTATION → CODE_REVIEW → VALIDATION → QUALITY/PRODUCTION readiness`. Current phase, completed milestones and open blockers are owned by `PROJECT_STATE.md` / `NEXT_WORK_ITEM.md`; this roadmap defines dependencies, not duplicate status.

## Phase 00 dependency graph

```text
Reviewed phase contracts
→ complete source + causal harness + author regression
→ exact durable handoff
→ CODE_REVIEW_PASS
→ authorized LAB validation
→ qualification
→ authorized SITE lifecycle/restore/terminal evidence
→ HOST_READY assessment
```

| Milestone | Exit evidence |
|---|---|
| M-P00-AUTHOR-COMPLETE | reviewed scope implemented, no hidden stubs, exact candidate and author evidence |
| M-P00-CODE-REVIEW | exact independent/role-separated review with assurance declared |
| M-P00-VALIDATION | authorized mandatory LAB/native results and qualification, then applicable SITE evidence |
| M-P00-HOST-READY | all applicable acceptance predicates; no gate-blocking finding; explicit as-of assessment |

A historic author-completeness finding does not reopen an accepted candidate unless current evidence explicitly reopens it. `NOT_RUN` validation is not an author test failure, and a code-review PASS is not validation PASS.

## Downstream phase dependencies

| Phases | Blueprint phase purpose (exact gate authority stays in its phase design) |
|---|---|
| 01–02 | Linux foundation and control plane: API, metadata, queue, assets |
| 03–05 | Job engine, GPU abstraction and remote GPU integration |
| 06 | Basic generation: a bounded vertical slice produces a traceable output |
| 07–09 | Character continuity, shot engine and audio pipeline |
| 10–12 | Episode assembly, novel adaptation and controlled quality improvement |
| 13–14 | Local GPU and scale-out, justified by actual workloads |

`docs/FILM_PIPELINE_DESIGN_BACKLOG.md` records design questions and acceptance proposals for these phases. It is not implementation authorization and does not add prerequisites to HOST_READY. Validate a small end-to-end film workflow before expanding model fleets or distributed infrastructure; this is a planning preference, not a shortcut around phase gates.

## Cross-cutting loops

TEST-DESIGN / TEST-REVIEW governs oracle changes. DOC-DESIGN / DOC-REVIEW / DOC-AUDIT governs material control-plane changes. WORKFLOW_REVIEW addresses ineffective loops. MODEL-EVAL binds experiments to exact environments. SELF-LEARNING measures correction effectiveness rather than counting documents.

Update this roadmap when dependency order or exit criteria change. Ordinary progress belongs in current state and owning run evidence.
