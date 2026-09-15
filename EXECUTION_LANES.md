# AI-FILM-SERVER — Independent Workflow Trust Boundaries

## Principle

Producer and consumer workflows do not trust each other's labels. Trust crosses a boundary only through immutable identity + independently checked evidence. `main` is the single global gate/state ledger.

## Source workflows

### IMPLEMENT
Writable source/tests/docs within approved scope. Produces commits/packages/handoffs. Cannot issue code-review verdicts or native validation.

### REVIEW
Detached exact candidate. Re-reads requirements, runs independent safe tests/negative scenarios and writes findings/verdict. Cannot patch reviewed source.

## Documentation-governance workflows

### DOC-DESIGN
Writable control-plane policy/design proposal. Cannot approve itself.

### DOC-REVIEW
Detached exact DOC-DESIGN commit. Reviews detailed requirements/invariants and may FAIL back to DOC-DESIGN. Cannot edit proposed policy.

### DOC-AUDIT
Detached exact candidate that already passed DOC-REVIEW. Audits the **entire active documentation system**, not just the delta: stale versions, conflicting rules, obsolete know-how, test/business independence, server-environment truth, recovery/self-learning and blind spots analogous to prior failures. It may FAIL back to DOC-DESIGN despite DOC-REVIEW PASS.

A material documentation-system change reaches `main` only after DOC-REVIEW and DOC-AUDIT both pass.

## Immutable handoff minimum

```yaml
WORKFLOW_ID:
TARGET_COMMIT:
ARTIFACT_OR_DOC_SET_ID:
BUSINESS_REQUIREMENT_SET:
TEST_CONTRACT:
CHANGED_SCOPE:
KNOWN_LIMITATIONS:
PRODUCER_EVIDENCE:
READY_FOR_CONSUMER: true
```

Consumer verifies identity before work. Mutable worktrees are never formal review inputs.

## Findings

```yaml
FINDING_ID:
TARGET_COMMIT:
SEVERITY:
CATEGORY:
EVIDENCE:
IMPACT:
REQUIRED_DISPOSITION:
STATUS:
```

Producer fixes; consumer closes on a new immutable candidate.

## Independence rules

- separate worktrees/branches/evidence namespaces;
- consumer does not read uncommitted producer changes as formal input;
- producer cannot edit consumer verdict records;
- PASS of a lower-level workflow never implies a higher gate;
- final audit must actively search for assumptions shared by design and first review.
