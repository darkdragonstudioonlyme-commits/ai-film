# HEALTH_REVIEW-DOCSYS-R9-V41-FORENSIC-012

```yaml
HEALTH_REVIEW_ID: DOCSYS-R9-V41-FORENSIC-012
TRIGGER: "Independent forensic audit of self-learning, continuous-improvement, cross-run reuse, PASS integrity and evidence semantics"
WORKFLOW: DOCSYS-V2-R9
STATE_BEFORE: "main V40; V41 recovery-effectiveness design exists; R9/A9 verdict branches exist but verdict-bearing CI is structurally red"
HEALTH_STATE: META_REVIEW_REQUIRED
ROOT_CAUSE_CLASS: PROCESS_TOOLING_GOVERNANCE
RETURN_TO: "independent DOC-REVIEW R10 of lane/docs-v2-r9-v41-forensic-design"
RESULT: SYSTEMIC_CORRECTION_AUTHORED_PENDING_INDEPENDENT_REVIEW
```

## Independently reproduced strengths

- Exact dev21 source identity and code-review evidence were rechecked: 760 tests and 101 static checks reproduce cleanly on the detached exact review commit.
- Learning lifecycle is not documentation-only: prior failures produced durable learning, policy/checker changes, successors for ineffective learning, and cross-run continuity reuse.
- V41 recovery-effectiveness design target had green exact-target governance CI before verdict artifacts were added.

## Forensic findings requiring hardening

1. **Semantic effectiveness gap.** `tools/check_learning_lifecycle.py` currently proves lifecycle structure and evidence-path existence, but not that effectiveness evidence proves the declared success metric, scope or sample cardinality. An unrelated existing evidence path can therefore satisfy the structural checker.
2. **Metric-definition drift risk.** Immutable learning records own `SUCCESS_METRIC`, while the lifecycle register repeats a mutable `success_metric`. The two can diverge without current checker failure; the continuity learning already demonstrates wording/sample-requirement drift.
3. **Verdict-branch CI contradiction.** Review/audit branches can self-declare PASS while their verdict-bearing GitHub Actions run fails `partial-promotion-verdict-set`. This is a branch-role/tooling mismatch, not evidence that the exact design target itself failed, but it makes PASS signaling noisy and unsafe to interpret automatically.
4. **Test-governance provenance gap.** `TEST_REVIEW-P00-DEV20-FACTORY-003` is canonical while its referenced `TEST_CHANGE-P00-DEV20-FACTORY-003` existed only on the producer lane. The proposal is canonicalized byte-identically in this candidate.
5. **Root metadata authority ambiguity.** Control-plane root `pyproject.toml` still contains old dev6 package/review metadata. It is not a canonical current-state owner and must be explicitly treated as non-authoritative unless PROJECT_STATE delegates that role.
6. **Automation/enforcement coverage gap.** CI path filters and repository settings are separate from policy. The documentation system must not describe review/CI as platform-enforced unless current rules actually enforce it, and lifecycle-domain path coverage must be audited.
7. **Improvement measurement gap.** Workflow-health lists useful efficiency metrics but lacks a stable longitudinal measurement artifact contract that can prove more work produces less rework/higher correctness over time.

## Systemic correction in this design

- `SELF_LEARNING.md` now distinguishes structural lifecycle evidence from semantic effectiveness proof and defines a measurement-receipt contract.
- Success metrics are immutable learning meaning; register copies must match rather than silently weaken metrics.
- `WORKFLOW_HEALTH.md` routes semantic-evidence mismatch, metric drift, verdict/CI contradiction and unresolved test-governance provenance into meta-review.
- `TEST_STRATEGY.md` requires every canonical TEST_REVIEW to resolve its exact proposal/gap; the dev20 proposal is restored byte-identically from immutable IMPLEMENT history.
- `GIT_WORKFLOW.md` separates project policy from platform enforcement and defines verdict-branch/CI-role and lifecycle-domain coverage requirements.
- `DOCUMENTATION_MAP.md` explicitly classifies root package metadata as non-authoritative for current candidate truth and adds semantic measurement receipts to the source-of-truth model.
- `POLICY_REGISTRY.md` hardens existing learning/test/persistence policy wording without claiming new checker implementation.

## Effectiveness reclassification

Strict reconciliation found that the mutable register had paraphrased all immutable metrics. The register is corrected to the immutable meanings. `LEARNING-CONTROL-001`, `LEARNING-SOURCE-VISIBILITY-001` and `LEARNING-WORKFLOW-CONTINUITY-001` are returned from structural `EFFECTIVE` to `PENDING_MEASUREMENT`; the continuity metric again requires three interrupted/resumed workflows. 004/005/006 retain `EFFECTIVE` only through explicit metric-bound receipts. New `LEARNING-EVIDENCE-SEMANTICS-007` captures the systemic correction and remains pending measurement.

## Unresolved implementation debt

The candidate now implements immutable metric equality, receipt hash/evidence binding, branch-role-aware verdict checking, canonical TEST_REVIEW provenance checking, expanded CI lifecycle-domain triggers, and server-side workflow-continuity execution. It still does **not** claim fully automatic semantic interpretation of observations or GitHub branch/ruleset enforcement. R10/A10 must independently review receipt semantics and keep platform enforcement debt explicit.

No product source, native procedure, LAB authority, qualification, SITE result or HOST_READY state is changed by this health review.
