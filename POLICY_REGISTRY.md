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

| Policy ID | Scope | Active rule | Canonical document |
|---|---|---|---|
| POL-STATE-001 | state | distinguish durable candidate, WIP and review target | `PROJECT_STATE.md` / `DOCUMENTATION_MAP.md` |
| POL-ROUTE-001 | workflow | `continue` routes deterministically from verified state | `WORKFLOW_ROUTER.md` |
| POL-LANE-001 | trust | producer/reviewer are independent; immutable handoff | `EXECUTION_LANES.md` |
| POL-TEST-001 | testing | reviewed business behavior, not code, owns the oracle | `TEST_STRATEGY.md` |
| POL-LEARN-001 | learning | reusable discoveries enter memory and can promote to policy/checkers | `SELF_LEARNING.md` |
| POL-HEALTH-001 | process | repeated ineffective cycles trigger workflow meta-review | `WORKFLOW_HEALTH.md` |
| POL-ENV-001 | environment | benchmark/model claims bind an exact environment snapshot | `SERVER_ENVIRONMENT.md` / `MODEL_EVALUATION.md` |
| POL-GIT-001 | persistence | exact identity + remote/artifact verification before durability | `GIT_WORKFLOW.md` |
| POL-RECOVERY-001 | recovery | preserve WIP/evidence before repair; never guess current truth | `RECOVERY_PLAYBOOK.md` |

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
