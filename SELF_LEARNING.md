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
→ APPLY
→ PROMOTE TO POLICY/TOOL/CHECKER WHEN WARRANTED
→ INDEPENDENTLY REVIEW
→ MEASURE WHETHER RECURRENCE DECREASES
→ RETIRE/SUPERSEDE WHEN NO LONGER TRUE
```

## Discovery classes

`DEFECT | TOOLING | TEST | PROCESS | SECURITY | RECOVERY | PERFORMANCE | ENVIRONMENT | ARCHITECTURE | BUSINESS_CLARIFICATION`.

## Learning score

Score 0–2 for each: recurrence likelihood, impact, generality, safety relevance, cost avoided. Total guides action:

- 0–3: candidate-specific note/finding only;
- 4–6: memory entry;
- 7–10: memory + proposed policy/checker/workflow change, independently reviewed.

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
SUCCESS_METRIC:
REVIEW_STATUS:
STATUS: ACTIVE|SUPERSEDED|RETIRED
```

## Proof of learning

A promoted learning defines a future detector or behavior change, for example a checker, router rule, test, schema, policy or recovery step. Later workflow health reviews ask whether recurrence decreased. If not, the learning was incomplete and is reviewed again.

## Memory compaction

`PROJECT_MEMORY.md` is an active index, not an ever-growing diary.

- keep active reusable rules and short provenance;
- move detailed historical reasoning to immutable review/health records or Git history;
- mark superseded entries and remove their obsolete instructions from active guidance;
- DOC-AUDIT periodically consolidates duplicates and verifies successors;
- never delete evidence needed to understand why an active safety policy exists.

## Anti-overfitting

Do not create global policy from one accidental tool quirk unless the rule generalizes or materially improves safety. Conversely, repeated mistakes that share a root cause should become one systemic rule, not many near-duplicate memory entries.
