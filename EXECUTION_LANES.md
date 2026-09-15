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

```text
DOC-DESIGN-V2
  branch: lane/docs-v2-design
  worktree: /home/dragon/ai-film-dev/docs-v2-design
        │ exact commit
        ▼
DOC-REVIEW-V2
  branch: lane/docs-v2-review
  worktree: /home/dragon/ai-film-dev/docs-v2-review
  detailed/file-level acceptance review
        │ reviewed exact commit
        ▼
DOC-AUDIT-V2
  branch: lane/docs-v2-audit
  worktree: /home/dragon/ai-film-dev/docs-v2-audit
  holistic audit of the entire active control plane
        │ PASS only
        ▼
main promotion
```

DOC-REVIEW cannot edit DOC-DESIGN. DOC-AUDIT reviews the whole active system, not merely changed files, and specializes in drift, duplicates, obsolete policy, circular trust, code-driven tests, recovery gaps and checker brittleness. Findings return to DOC-DESIGN and require another review/audit cycle.

## Model-evaluation workflow

MODEL-EVAL consumes an immutable environment ID, model identity, test-set identity and parameter identity. Independent evaluation review checks recommendation and reproducibility. A missing GPU/runtime measurement blocks dependent performance claims rather than being inferred.

## Workflow-health review

`WORKFLOW_REVIEW` is activated by `WORKFLOW_HEALTH.md`. It may change process/test/documentation policy but cannot silently change product requirements. Systemic corrections require the appropriate independent reviewer before the original workflow resumes.

## Active-run independence

Each lane may own work independently, but each `(WORKFLOW_ID, BASE_IDENTITY)` has at most one active `RUN_ID`. `LANE_STATE.md` points to its lane-local `workflow-runs/<RUN_ID>.md`. A new chat takes over the same run after reconciliation; it never creates a second run because the previous chat ended.

Review lanes never consume an IMPLEMENT step that is merely `INTENT`/local WIP. Only the immutable handoff step moves REVIEW to a new exact candidate.

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
