# AI-FILM-SERVER — Self-Learning and Continuous Workflow Improvement

## Objective

Every meaningful failure or improvement should make future work cheaper, safer or more accurate. Logging history without changing future behavior is not sufficient learning.

## Learning loop

```text
OBSERVE
→ EXPLAIN
→ GENERALIZE
→ SCORE REUSABILITY
→ PERSIST
→ PROPOSE POLICY/TOOL/CHECKER CHANGE WHEN WARRANTED
→ INDEPENDENTLY REVIEW
→ ACTIVATE THE REVIEWED CHANGE
→ APPLY
→ MEASURE WHETHER RECURRENCE/FRICTION DECREASES
→ RETIRE/SUPERSEDE WHEN NO LONGER TRUE
```

A reviewed learning is **not yet operational learning** until its successor policy/tool/checker is active in the canonical control plane, or the activation is explicitly blocked with an owner and return path.

## Discovery classes

`DEFECT | TOOLING | TEST | PROCESS | SECURITY | RECOVERY | PERFORMANCE | ENVIRONMENT | ARCHITECTURE | BUSINESS_CLARIFICATION`.

## Learning score

Score 0–2 for each: recurrence likelihood, impact, generality, safety relevance, cost avoided. Total guides action:

- 0–3: candidate-specific note/finding only;
- 4–6: memory entry;
- 7–10: memory + proposed policy/checker/workflow change, independently reviewed and activated.

Critical security/correctness lessons may be promoted regardless of score.

## Learning record

```yaml
LEARNING_ID:
DISCOVERED_IN:
CLASS:
OBSERVATION:
ROOT_CAUSE:
EVIDENCE:
REUSABLE_RULE:
SCORE:
CURRENT_ACTION:
POLICY_OR_TOOL_PROMOTION:
ACTIVATION_TARGET:
ACTIVATION_STATUS: NOT_REQUIRED|PENDING_REVIEW|PENDING_ACTIVATION|ACTIVE|BLOCKED
ACTIVATION_BLOCKER:
ACTIVATED_IN:
SUCCESS_METRIC:
REVIEW_STATUS:
STATUS: ACTIVE|SUPERSEDED|RETIRED
```

## Proof of learning

A promoted learning defines a future detector or behavior change, for example a checker, router rule, test, schema, policy or recovery step. The learning is counted as **applied** only after that change is active in the canonical workflow. Later workflow-health reviews ask whether recurrence or friction decreased. If not, the learning was incomplete and is reviewed again.

Two failure modes are explicitly tracked:

- **LEARNED_BUT_NOT_ACTIVE** — useful correction exists/reviewed but promotion/activation has not completed;
- **ACTIVE_BUT_NOT_EFFECTIVE** — correction is active but recurrence/friction did not improve.

## Activation backlog

`PROJECT_MEMORY.md` remains an active index, but any promoted learning with `PENDING_ACTIVATION`/`BLOCKED` must point to its activation target and blocker. `WORKFLOW_HEALTH.md` treats an accumulating learned-but-not-active backlog as process debt when affected workflows continue to incur the same friction.

## Durable learning records

Persist standalone reusable learning under `learning/LEARNING-<scope>-<nnn>.md`. If the complete learning is already captured by an immutable review/health record, the memory index may point there instead of duplicating it. Follow-up evidence updates the learning lifecycle through a new reviewed record/commit; do not erase the original observation.

## Memory compaction

`PROJECT_MEMORY.md` is an active index, not an ever-growing diary.

- keep active reusable rules and short provenance;
- move detailed historical reasoning to immutable review/health records or Git history;
- mark superseded entries and remove their obsolete instructions from active guidance;
- DOC-AUDIT periodically consolidates duplicates and verifies successors;
- never delete evidence needed to understand why an active safety policy exists.

## Anti-overfitting

Do not create global policy from one accidental tool quirk unless the rule generalizes or materially improves safety. Conversely, repeated mistakes that share a root cause should become one systemic rule, not many near-duplicate memory entries.
