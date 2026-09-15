# AI-FILM-SERVER — Recovery and Continuity Playbook

## Recovery principle

Preserve exact WIP, durable evidence and immutable history before attempting repair. Recovery must restore a trustworthy decision point, not merely make tools green again.

## Recovery priority

1. protect uncommitted WIP and unresolved durable state;
2. identify last immutable accepted candidate and review result;
3. fresh-fetch canonical/lane refs;
4. run state/documentation/runtime checks;
5. classify failure;
6. choose non-destructive recovery route;
7. verify recovered identity before resuming.

## Common scenarios

### New chat / context loss
Read cold-start docs, fresh-fetch refs, run runtime reconciliation, then use `WORKFLOW_ROUTER.md`. Do not reconstruct current state from conversational memory.

### State/version drift
Create `STATE_DRIFT`; do not pick the highest version string. Compare canonical state, fresh lane state, local HEAD/dirty set and artifact identity. Update the control plane through reviewed documentation governance.

### Checker drift
When canonical state + lane/worktree identities are internally valid but a checker fails because it expects an old state shape/version/lifecycle marker, classify `CHECKER_DRIFT`. Preserve source state and WIP, capture the failed checker assumption, route a Documentation System correction through DOC-DESIGN → DOC-REVIEW → DOC-AUDIT, then return to the original workflow. Never mutate valid project state merely to satisfy an obsolete checker.

`CHECKER_DRIFT` differs from `STATE_DRIFT`: the former is a defect in the verifier/schema assumptions; the latter is a real disagreement between authoritative/current identities.

### Dirty WIP with older durable package
Resume documented WIP in its owning lane. Do not reset merely because the last package is older.

### Partial/failed commit or package
Keep source commit identity separate from package generation. Rebuild package from exact commit; never edit source under the same candidate identity after handoff.

### Missing artifact
If exact source commit exists, regenerate only when package format permits and record a new artifact identity. If neither exact source nor verified artifact exists, mark recovery blocker; do not synthesize from prose.

### Tool unavailable
Use a functionally equivalent safe path only if it preserves evidence/identity semantics. Persist reusable tooling limitation when it affects future work.

### Repeated failed recovery
Trigger `WORKFLOW_HEALTH.md` meta-review instead of repeating the same operation.

## Recovery record

```yaml
RECOVERY_ID:
FAILURE_CLASS:
STATE_BEFORE:
PRESERVED_ASSETS:
LAST_TRUSTED_IDENTITY:
ACTIONS:
STATE_AFTER:
EVIDENCE:
LESSON_ID:
RETURN_TO:
```
