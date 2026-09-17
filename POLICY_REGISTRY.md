# AI-FILM-SERVER — Active Policy Registry and Lifecycle

## Goal

Current guidance stays concise and authoritative. Obsolete rules do not remain mixed with active policy merely because they were once useful.

## Policy lifecycle

`PROPOSED → ACTIVE → DEPRECATED → RETIRED` or `ACTIVE → SUPERSEDED`.

- **ACTIVE**: normative project operating policy.
- **DEPRECATED**: still temporarily applicable; replacement and removal condition required.
- **SUPERSEDED**: not current; successor ID required.
- **RETIRED**: no longer part of active guidance.

Git history and immutable review records preserve history. Active docs remove obsolete detailed instructions after retirement.

## Active registry

| Policy ID | Scope | Owner | Effective from | Review trigger | Active rule | Canonical document |
|---|---|---|---|---|---|---|
| POL-STATE-001 | state | project-control | 2026-09-15 | state schema/drift incident | distinguish durable candidate, WIP and review target | `PROJECT_STATE.md` / `DOCUMENTATION_MAP.md` |
| POL-ROUTE-001 | workflow | project-control | 2026-09-15 | routing ambiguity/deadlock | `continue` routes deterministically from verified state | `WORKFLOW_ROUTER.md` |
| POL-LANE-001 | trust | governance | 2026-09-15 | workflow/lane model changes | producer/reviewer are independent; immutable handoff | `EXECUTION_LANES.md` |
| POL-TEST-001 | testing | test-governance | 2026-09-15 | business/test authority change, provenance gap or repeated test debt | reviewed business behavior owns the oracle; every canonical TEST_REVIEW must resolve its exact TEST_CHANGE/TEST_GAP provenance | `TEST_STRATEGY.md` |
| POL-LEARN-002 | learning | governance | DOCSYS-V2-R9 | lifecycle/metric drift, activation backlog, ineffectiveness or measurement debt | immutable learning evidence is separate from machine-owned lifecycle state; EFFECTIVE requires semantic proof of the immutable metric, not evidence-path existence; automation detects/routes but cannot self-review/promote | `SELF_LEARNING.md` / `learning/LEARNING_STATE.json` |
| POL-HEALTH-001 | process | governance | 2026-09-15 | repeated inefficient/deadlocked cycles or learning debt | workflow health triggers meta-review and activation/effectiveness follow-through | `WORKFLOW_HEALTH.md` |
| POL-ENV-001 | environment | model-evaluation | 2026-09-15 | material benchmark environment change | benchmark/model claims bind an exact environment snapshot | `SERVER_ENVIRONMENT.md` / `MODEL_EVALUATION.md` |
| POL-GIT-001 | persistence | project-control | 2026-09-15 | persistence/remote tooling/source-visibility or platform-enforcement changes | exact identity + remote/artifact verification before durability; partial snapshots never masquerade as full source; procedural review/CI is not called platform-enforced without verified repository rules | `GIT_WORKFLOW.md` |
| POL-RECOVERY-001 | recovery | project-control | 2026-09-15 | recovery failure/state-loss incident | preserve WIP/evidence before repair; never guess current truth | `RECOVERY_PLAYBOOK.md` |
| POL-CONTINUITY-001 | continuity | project-control | 2026-09-15 | interruption/duplicate-work incident | one logical RUN_ID; write-ahead INTENT/COMPLETE; reconcile and reuse exact outputs | `WORKFLOW_CONTINUITY.md` |

## Superseded registry

| Policy ID | Status | Successor | Reason |
|---|---|---|---|
| POL-LEARN-001 | SUPERSEDED | POL-LEARN-002 | R8 defined activation/effectiveness semantics but did not provide a single machine-readable current lifecycle owner; stale learning records could disagree with project aggregates without checker failure. |

For non-ACTIVE policies, successor/removal conditions are explicit. Review dates may be event-driven; when calendar review is required add `REVIEW_DUE`.

## Policy change record

Every material policy change records:

```yaml
POLICY_ID:
OLD_STATUS:
NEW_STATUS:
REASON:
EVIDENCE_OR_LEARNING:
REPLACED_BY:
AFFECTED_DOCS:
MIGRATION_REQUIRED:
REVIEW_ID:
OWNER:
EFFECTIVE_FROM:
REVIEW_TRIGGER_OR_DUE:
```

R9 policy change:

```yaml
POLICY_ID: POL-LEARN-001
OLD_STATUS: ACTIVE
NEW_STATUS: SUPERSEDED
REASON: "Cross-session review found lifecycle-state drift between immutable learning records and canonical aggregate state."
EVIDENCE_OR_LEARNING: LEARNING-LIFECYCLE-CONSISTENCY-002
REPLACED_BY: POL-LEARN-002
AFFECTED_DOCS: "SELF_LEARNING.md; WORKFLOW_HEALTH.md; WORKFLOW_ROUTER.md; DOCUMENTATION_MAP.md; learning/*; learning/LEARNING_STATE.json; checkers"
MIGRATION_REQUIRED: true
REVIEW_ID: DOC-V2-R9-REVIEW-001
OWNER: governance
EFFECTIVE_FROM: DOCSYS-V2-R9
REVIEW_TRIGGER_OR_DUE: "any lifecycle drift, ineffective learning without successor, or aggregate mismatch"
```

## Pruning rule

During DOC-AUDIT:

1. find duplicated or contradictory active rules;
2. choose one canonical owner;
3. remove obsolete copies from active docs;
4. retain only a short successor/history pointer when needed;
5. rely on Git history/immutable reviews for detailed retired content;
6. update links/checkers so no bootstrap path depends on retired policy.

A larger documentation corpus is not automatically better. The target is maximum decision quality per active instruction.

## Review triggers

Review a policy when assumptions change, it causes repeated exceptions/workarounds, a newer rule covers the same scope better, it references stale versions/paths, or a health review shows it contributes to rework. A reviewed policy change that remains unactivated while affected work proceeds is itself a review trigger.

## Historical-guidance placement

Superseded system-design/how-to files move out of active discovery paths into `history/` or remain retrievable from Git. Immutable review/checkpoint records may stay in evidence locations, but active bootstrap files must not tell a new chat to follow retired instructions.
