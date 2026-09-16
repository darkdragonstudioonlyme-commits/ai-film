# LEARNING-ADVERSARIAL-FIXTURE-ISOLATION-003 — Negative tests must normalize their own baseline

```yaml
LEARNING_ID: LEARNING-ADVERSARIAL-FIXTURE-ISOLATION-003
DISCOVERED_IN: "DOCSYS-V2-R9 first promotion CI run 35089621367"
CLASS: TOOLING
OBSERVATION: "The production lifecycle checker resolved the promoted review+audit evidence correctly, but the adversarial `partial_promotion_verdict` test failed after promotion because its copied repository already contained both real verdict files. The same test had passed on the pre-promotion design tree where neither file existed."
ROOT_CAUSE: "The negative test mutated current repository state without first establishing the exact baseline required by the scenario. Its result therefore depended on whether the test ran before or after promotion."
EVIDENCE:
  - "GitHub Actions run 35089621367 / job 104772577496"
  - tools/test_learning_lifecycle_checker.py
  - reviews/DOCUMENTATION_SYSTEM_R9_REVIEW_R1_PASS.md
  - reviews/DOCUMENTATION_SYSTEM_R9_AUDIT_R1_PASS.md
REUSABLE_RULE: "An adversarial/negative test must create or normalize all fixture preconditions it relies on. It must not assume ambient lifecycle state such as absence of promotion artifacts, current branch phase, or current verdict set."
SCORE: 9
CURRENT_ACTION: "Make promotion verdict test fixtures derive current verdict paths from PROJECT_STATE, remove ambient verdict files before simulating partial/mismatched states, and regression-run the same suite both pre- and post-promotion."
POLICY_OR_TOOL_PROMOTION: "tools/test_learning_lifecycle_checker.py; learning lifecycle review/audit criteria"
SUCCESS_METRIC: "The identical adversarial lifecycle regression suite passes on both promotion-ready trees (no final verdicts) and promoted trees (real final verdicts present), while still rejecting partial/mismatched simulated verdict sets."
STATUS: ACTIVE
```

Current lifecycle is owned by `learning/LEARNING_STATE.json`, not by this immutable learning record.
