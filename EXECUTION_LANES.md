# AI-FILM-SERVER — Independent Workflow Lanes

## Trust invariant

Producer workflows never authorize their own outputs. Consumers receive immutable identities and independently verify what matters. `main` alone records global project gates.

```text
PRODUCER → immutable handoff → REVIEW/CONSUMER
   ↑                            │
   └──── findings/result ───────┘
```

## Source workflows

### IMPLEMENT
Writable source/test/config/docs worktree. May implement, run author tests, commit, package and hand off. Cannot issue CODE_REVIEW verdict or native validation.

### REVIEW
Detached exact candidate. May reread requirements, independently test, run negative scenarios and issue findings/verdicts. Must not patch candidate source or auto-follow IMPLEMENT head.

## Test-authority workflows

Material oracle changes use TEST-DESIGN → TEST-REVIEW. Production implementation is evidence under test, not authority for expected behavior. Harness-only fixes may be authored separately but must prove the business oracle did not weaken. See `TEST_STRATEGY.md`.

## Documentation System V2 governance — three independent stages

Every material documentation-system release uses release-scoped independent lanes:

```text
DOC-DESIGN-<release>
  writable proposal worktree/branch
        │ exact immutable commit
        ▼
DOC-REVIEW-<release>
  detached exact detailed review
        │ PASS only
        ▼
DOC-AUDIT-<release>
  detached holistic audit of the full active control plane
        │ PASS only
        ▼
main promotion
```

Standing policy does not pin one historical docs branch as current. Exact release ID, branch/worktree identity and predeclared verdict records belong to `PROJECT_STATE.md`, the release checkpoint and workspace map. DOC-REVIEW never edits the design candidate; DOC-AUDIT reviews the exact reviewed tree plus consumer verdict binding. Findings return to DOC-DESIGN and require a new immutable candidate/review/audit cycle.

## Model-evaluation workflow

MODEL-EVAL consumes an immutable environment ID, model identity, test-set identity and parameter identity. Independent evaluation review checks recommendation and reproducibility. A missing GPU/runtime measurement blocks dependent performance claims rather than being inferred.

## Workflow-health review

`WORKFLOW_REVIEW` is activated by `WORKFLOW_HEALTH.md`. It may change process/test/documentation policy but cannot silently change product requirements. Systemic corrections require the appropriate independent reviewer before the original workflow resumes.

## Handoff contract

Every material producer→consumer handoff binds at least:

```yaml
OUTPUT_ID:
PRODUCER_WORKFLOW:
SOURCE_OR_DOC_COMMIT:
ARTIFACT_IDENTITY:
REQUIREMENT_OR_POLICY_BASELINE:
TEST_OR_CHECK_RESULT:
KNOWN_LIMITATIONS:
READINESS_FLAGS:
```

Review findings bind exact target identity and close only on a later independently reviewed output.

## Independence requirements

1. separate mutable worktree or detached immutable checkout;
2. exact input/output identity;
3. separate evidence namespace;
4. no shared mutable PASS flag;
5. consumer rechecks critical invariants;
6. producer cannot close its own findings;
7. global gate transitions only on canonical `main`.
