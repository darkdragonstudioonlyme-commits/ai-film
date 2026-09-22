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

Documentation governance uses three release-scoped lanes selected by `PROJECT_STATE.md:DOCUMENTATION_GOVERNANCE`:

```text
DOC-DESIGN-V2
  branch/worktree: selected DESIGN identity from canonical governance state
        │ exact commit
        ▼
DOC-REVIEW-V2
  branch/worktree: selected REVIEW identity
  detailed/file-level acceptance review of exact design commit
        │ reviewed exact commit
        ▼
DOC-AUDIT-V2
  branch/worktree: selected AUDIT identity
  holistic audit of the entire active control plane
        │ PASS only
        ▼
main promotion of exact audited tree + predeclared immutable verdict records
```

Standing guidance must never hard-code one documentation revision's branch/worktree names. A fresh chat resolves the active governance release, stage branches, worktrees and final record paths from canonical state or the explicit governance run.

DOC-REVIEW cannot edit DOC-DESIGN. DOC-AUDIT reviews the whole active system, not merely changed files, and specializes in drift, duplicates, obsolete policy, circular trust, code-driven tests, recovery gaps, learning activation gaps and checker brittleness. Findings return to DOC-DESIGN and require another review/audit cycle.

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

For source/code handoffs, `KNOWN_LIMITATIONS` includes remote source addressability/visibility when the full source tree is not materialized in Git.

Review findings bind exact target identity and close only on a later independently reviewed output.

## Independence requirements

1. separate mutable worktree or detached immutable checkout;
2. exact input/output identity;
3. separate evidence namespace;
4. no shared mutable PASS flag;
5. consumer rechecks critical invariants;
6. producer cannot close its own findings;
7. global gate transitions only on canonical `main`.

## Assurance disclosure

The Blueprint's same-chat review discipline remains applicable. When the same assistant performs sequential roles, every verdict declares `ASSURANCE_CLASS: SAME_CHAT_ROLE_SEPARATED`, its exact target, separate checkout/evidence, and the checks actually rerun. This provides procedural separation, not an independent human, external organization or context-isolated agent. Changing branch names cannot manufacture independence.

A reviewer does not patch the consumed candidate. A finding returns to the producer and invalidates the old target for that correction; the next review binds a new immutable target. Higher-assurance reviews may be requested for material risks, but do not retroactively relabel same-chat records as externally independent.

## Review claim-to-evidence contract

For every load-bearing PASS claim, persist the requirement, exact target, inspected evidence or executed command, actual result, counterexample and limitation. Check coverage totals against source, then challenge whether the objects and transitions are constructible under TEST_STRATEGY §12. A repeated later gap in a previously accepted design is an escaped review finding, not evidence that the earlier review was effective. Record a consolidated correction against that exact design; do not generate unrelated new approvals for each symptom. No reviewer may treat a green documentation audit script as the holistic semantic audit it is supposed to perform.

## Cross-model acceptance

For material dual-actor work, the actual candidate author and accepting reviewer must
differ. Use CROSS_MODEL_PROCEDURAL_REVIEW only for an actually executed other-model
review; independent contexts are not independent organizations or guaranteed accuracy.
A same-model technical review/audit may report findings, but cannot replace a required
Claude verdict when Claude is unavailable. One non-author actor may run REVIEW and
AUDIT as separate passes with that limitation declared. No mixed-author candidate
self-acceptance: partition responsibility or keep the affected acceptance blocked.
Each actor follows shared learning/health gates. Worker output is RESULT_UNREVIEWED
until its designated consumer verifies identity, scope and evidence.
## Review result and evidence classes

Separate AUTOMATED_CHECK, HOST_COMMAND, AUTHOR_REPORT, STATIC_MODEL_REVIEW,
CROSS_MODEL_REVIEW and NATIVE_VALIDATION evidence. A reviewer may challenge another
actor's result; it may not relabel host logs as its own rerun. CLAIMED_PASS,
INPUT_COMPLETE, SCOPE_REVIEWED, CANDIDATE_ACCEPTED, DEPLOYED and EFFECTIVE are distinct.
The reviewer lists acceptance IDs actually covered, omissions and findings. Required
omissions or open blocking/high findings preclude PASS even if the process exits zero.

The host computes the digest of exact report-body bytes after receipt. A tool-less
model is not asked to compute the hash of its own future serialized answer. Metadata
(task/context/actor/usage, report hash) is a separate collector envelope; it does not
participate in the report-body hash. Preserve raw output locally and validate the
normalized artifact before acceptance. A schema-valid result is still unreviewed.

On disagreement, use one findings record per causal family: exact requirement and
candidate, each position, falsifiable counterexample, evidence owner and disposition.
FACT/CONTRACT conflicts hold the affected task immediately. PREFERENCE conflicts use
the frozen criteria, not coordinator rank or majority vote. Fixes return to the actual
author. Resolve mixed authorship by review scope; a same-author audit never replaces
the required other-model verdict. No fabricated cross-model sign-off is allowed.
