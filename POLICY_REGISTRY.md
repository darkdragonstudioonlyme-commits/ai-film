# AI-FILM-SERVER — Active Policy Registry and Lifecycle

## Goal

Current guidance stays concise and authoritative. Obsolete rules do not remain mixed with active policy merely because they were once useful.

## Policy lifecycle

`PROPOSED → ACTIVE → DEPRECATED → RETIRED` or `ACTIVE → SUPERSEDED`.

- **ACTIVE**: normative project operating policy.
- **DEPRECATED**: still temporarily applicable; replacement and removal condition required.
- **SUPERSEDED**: not current; successor ID required.
- **RETIRED**: no longer part of active guidance.

Git history and immutable review records preserve history. Active docs should remove obsolete detailed instructions after retirement; do not keep pages of crossed-out policy in current bootstrap files.

## Active registry

| Policy ID | Scope | Owner | Effective from | Review trigger | Active rule | Canonical document |
|---|---|---|---|---|---|---|
| POL-STATE-001 | state | project-control | 2026-09-15 | state schema/drift incident | distinguish durable candidate, WIP and review target | `PROJECT_STATE.md` / `DOCUMENTATION_MAP.md` |
| POL-ROUTE-001 | workflow | project-control | 2026-09-15 | routing ambiguity/deadlock | `continue` routes deterministically from verified state | `WORKFLOW_ROUTER.md` |
| POL-LANE-001 | trust | governance | 2026-09-15 | workflow/lane model changes | producer/reviewer are independent; immutable handoff | `EXECUTION_LANES.md` |
| POL-TEST-001 | testing | test-governance | 2026-09-15 | business/test authority change or repeated test debt | reviewed business behavior, not code, owns the oracle | `TEST_STRATEGY.md` |
| POL-LEARN-001 | learning | governance | 2026-09-15 | learning loop fails to reduce recurrence | reusable discoveries promote to reviewed policy/checkers | `SELF_LEARNING.md` |
| POL-HEALTH-001 | process | governance | 2026-09-15 | repeated inefficient/deadlocked cycles | workflow health triggers meta-review | `WORKFLOW_HEALTH.md` |
| POL-ENV-001 | environment | model-evaluation | 2026-09-15 | material benchmark environment change | benchmark/model claims bind an exact environment snapshot | `SERVER_ENVIRONMENT.md` / `MODEL_EVALUATION.md` |
| POL-GIT-001 | persistence | project-control | 2026-09-15 | persistence/remote tooling changes | exact identity + remote/artifact verification before durability | `GIT_WORKFLOW.md` |
| POL-RECOVERY-001 | recovery | project-control | 2026-09-15 | recovery failure/state-loss incident | preserve WIP/evidence before repair; never guess current truth | `RECOVERY_PLAYBOOK.md` |

For non-ACTIVE policies, registry rows additionally identify `STATUS`, `SUCCESSOR`, and removal/migration condition. Review dates may be event-driven; when a calendar review is required add `REVIEW_DUE` explicitly.

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

Review a policy when its assumptions change, it causes repeated exceptions/workarounds, a newer rule covers the same scope better, it references stale versions/paths, or a health review shows it contributes to rework.

## Historical-guidance placement

Superseded system-design/how-to files move out of active discovery paths into `history/` or remain retrievable from Git. Immutable review/checkpoint records may stay in their evidence locations, but active bootstrap files must not tell a new chat to follow retired instructions.
