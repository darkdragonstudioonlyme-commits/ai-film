# LEARNING-EXTERNAL-AUTHORITY-AUTHENTICITY-009 — External authority requires provenance outside the constrained operator boundary

```yaml
LEARNING_ID: LEARNING-EXTERNAL-AUTHORITY-AUTHENTICITY-009
DISCOVERED_IN: RUN-P00-VALIDATION-001/V02_LAB_EXECUTION_AUTHORITY
CLASS: SECURITY
OBSERVATION: "The protected LAB approved inbox had inheritance disabled and content-addressed objects, but the constrained Windows operator still had FullControl. Those controls proved local integrity and limited ambient writers; they did not prove that an external owner/controller authored the approval package."
ROOT_CAUSE: "The workflow conflated filesystem protection plus content integrity with independent authority provenance. A principal able to author the trusted store could satisfy structural assertions without proving an external decision."
EVIDENCE: "lane/validation-p00@9a3854d80b7e4c35c5d2ec933709280ce0baa7fa: workflow-health/HEALTH_REVIEW-WF-P00-V02-AUTHENTICITY-003.md; validation/V02_EXTERNAL_AUTHENTICITY_DEPLOYMENT-P00-DEV21.md; reviews/VALIDATION-V02-AUTHENTICITY-REVIEW-001_PASS.md; reviews/VALIDATION-V02-AUTHENTICITY-AUDIT-001_PASS.md; reviews/VALIDATION-V02-AUTHENTICITY-DEPLOYMENT-REVIEW-001_PASS.md"
REUSABLE_RULE: "When a workflow claims authority is external to the operator it constrains, authenticity must root in a credential/provenance boundary the operator cannot self-issue. Local ACLs and hashes remain integrity controls; require a separately reviewed external trust anchor and cryptographic signature, fail closed while the anchor is pending, and never generate the external private key inside the constrained environment."
SCORE: 10
CURRENT_ACTION: "Keep V02 trust config PENDING_EXTERNAL_KEY; obtain external Ed25519 public-key provenance; review activation separately; require exact-envelope signature before any protected object graph can authorize V03."
POLICY_OR_TOOL_PROMOTION: "validation V02 tooling/contract; PROJECT_STATE.md; NEXT_WORK_ITEM.md; PROJECT_MEMORY.md"
SUCCESS_METRIC: "Future external-authority activation/approval workflows reject operator-authored, unsigned, wrong-key or trust-anchor-drifted authority; only independently provenance-rooted signatures can authorize the exact envelope, and no native stage advances while the external anchor is pending."
STATUS: CANDIDATE_PENDING_R13_A13
```

This learning does not claim effectiveness yet. The current deployment proves only that the pending-anchor path fails closed. Effectiveness requires a future qualifying external-key activation or signed-approval attempt and independently reviewed evidence against the immutable metric.
