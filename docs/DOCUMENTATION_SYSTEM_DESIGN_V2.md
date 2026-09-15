# Documentation System V2 — Design

V2 extends reviewed Documentation System V1 with business-first testing, workflow-health meta-review, active policy lifecycle/pruning, exact server/model-evaluation environments, explicit recovery, and a stronger self-learning feedback loop.

## New canonical operating documents

- `TEST_STRATEGY.md`
- `WORKFLOW_HEALTH.md`
- `POLICY_REGISTRY.md`
- `SERVER_ENVIRONMENT.md`
- `MODEL_EVALUATION.md`
- `SELF_LEARNING.md`
- `RECOVERY_PLAYBOOK.md`
- `OPERATING_ARCHITECTURE.md`

## Three-stage governance

Material Documentation System V2 changes use:

```text
DOC-DESIGN-V2
→ immutable commit
→ DOC-REVIEW-V2 (detailed/file-level)
→ immutable reviewed commit
→ DOC-AUDIT-V2 (holistic/contradiction/drift/bloat/trust audit)
→ promotion to main only if both PASS
```

Review and audit do not edit design material in place.

## Design goals

1. Test expectations derive from reviewed business behavior, never current code.
2. Ineffective/deadlocked workflows detect themselves and route to meta-review.
3. Active policy stays concise; obsolete policy is superseded/retired from active guidance.
4. Server/model claims bind exact environment snapshots.
5. Self-learning changes future workflow and measures recurrence, not just logs history.
6. Recovery is deterministic and preserves WIP/evidence.
7. Version/path drift and stale assumptions are first-class audit targets.
