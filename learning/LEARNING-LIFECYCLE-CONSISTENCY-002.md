# LEARNING-LIFECYCLE-CONSISTENCY-002 — Current lifecycle must be machine-owned

```yaml
LEARNING_ID: LEARNING-LIFECYCLE-CONSISTENCY-002
DISCOVERED_IN: "Cross-session DOCSYS R8 self-learning review after State V32"
CLASS: PROCESS
OBSERVATION: "Canonical PROJECT_STATE reported learned-but-not-active backlog 0 and R8 learning controls ACTIVE, while several durable learning records still contained stale PENDING_ACTIVATION/PENDING_REVIEW snapshots or lacked activation fields entirely. Existing documentation checkers still PASSed."
ROOT_CAUSE: "Immutable learning evidence and current lifecycle status were mixed in the same record shape, while aggregate state was maintained separately. No checker reconciled per-learning review/activation/effectiveness state with the canonical release and aggregate backlog."
EVIDENCE:
  - learning/LEARNING-DOCSYS-ACTIVATION-001.md
  - learning/LEARNING-SOURCE-VISIBILITY-001.md
  - learning/LEARNING-WORKFLOW-CONTINUITY-001.md
  - learning/LEARNING-CONTROL-001.md
  - PROJECT_STATE.md:LEARNING_ACTIVATION
  - tools/check_documentation_governance.py
  - tools/audit_documentation_v2.py
REUSABLE_RULE: "Immutable learning records own observation/provenance; one machine-readable lifecycle register owns current review, activation and effectiveness state. Project-level learning metrics are derived from that register and machine-checked."
SCORE: 10
CURRENT_ACTION: "Introduce learning/LEARNING_STATE.json, lifecycle checker, bootstrap routing check and ineffective/measurement-debt meta-review triggers in DOCSYS-V2-R9."
POLICY_OR_TOOL_PROMOTION: "SELF_LEARNING.md; WORKFLOW_HEALTH.md; WORKFLOW_ROUTER.md; DOCUMENTATION_MAP.md; tools/check_learning_lifecycle.py; documentation governance/audit checkers"
SUCCESS_METRIC: "Across subsequent state/session transitions: zero stale active-release learning entries, project learning backlog equals checker-derived backlog, ineffective learnings trigger an explicit successor/meta-review, and no unreviewed correction is auto-promoted."
STATUS: ACTIVE
```

Current lifecycle is intentionally **not** owned by this immutable record; see `learning/LEARNING_STATE.json`.