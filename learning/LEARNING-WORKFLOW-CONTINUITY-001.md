# LEARNING-WORKFLOW-CONTINUITY-001 — Write-ahead workflow continuation

```yaml
LEARNING_ID: LEARNING-WORKFLOW-CONTINUITY-001
DISCOVERED_IN: HEALTH_REVIEW-WF-CONTINUITY-001
CLASS: RECOVERY
OBSERVATION: "End-of-chat documentation sync is insufficient when interruption occurs after useful work but before the final sync."
ROOT_CAUSE: "The control plane tracked coarse workflow state but not a durable logical RUN_ID, step cursor, write-ahead intent or idempotent output contract."
EVIDENCE: "main and remote IMPLEMENT lane remained on dev19 while local IMPLEMENT had clean dev20 commit 51c9d3f7373a2922c1ea6a3e973d817bb4e16523; runtime checker returned STATE_DRIFT. Owner reports duplicate-work timeout pattern twice."
REUSABLE_RULE: "Persist a run/step intent before duplicate-prone work; after interruption reconcile and resume the same RUN_ID, adopting exact existing outputs instead of starting a second workflow."
SCORE: 10
CURRENT_ACTION: "Promote to POL-CONTINUITY-001, WORKFLOW_CONTINUITY.md, router/recovery/git/checker rules and workflow-runs domain."
POLICY_OR_TOOL_PROMOTION: "WORKFLOW_CONTINUITY.md; WORKFLOW_ROUTER.md; RECOVERY_PLAYBOOK.md; GIT_WORKFLOW.md; check_workflow_continuity.py"
SUCCESS_METRIC: "Next three interrupted/resumed workflows continue from the last verified step with zero duplicate logical runs and zero repeated completed expensive steps unless identity changed."
REVIEW_STATUS: PENDING_DOC_REVIEW_AUDIT
STATUS: ACTIVE
```
