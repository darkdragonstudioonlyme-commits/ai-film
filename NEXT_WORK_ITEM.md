# NEXT WORK ITEM — Documentation System V2 governance

```yaml
WORKFLOW_ID: DOC-SYS-V2
LANE: DOC-REVIEW-V2_THEN_DOC-AUDIT-V2
STATUS: HANDED_OFF_FOR_INDEPENDENT_GOVERNANCE
PROJECT_MODE_REMAINS: IMPLEMENTATION
RETURN_TO: WF-P00-IMPL-DEV18
GOAL: "Approve a control plane that is business-test-first, self-learning, compact, recoverable and environment-aware."
SUCCESS_OUTPUT: "Independent DOC-REVIEW PASS plus independent holistic DOC-AUDIT PASS, then promotion to main."
ON_FAIL: "Return findings to DOC-DESIGN-V2; create a new immutable candidate."
ON_BLOCK: "Persist block using WORKFLOW_ROUTER and preserve source WIP."
EXIT_CONDITION: "All V2 review/audit criteria pass and canonical main/runtimes reconcile."
```

## Review scope

Review all proposed V2 policies, scripts, cross-links and the exact `activation/*` payload that will become canonical after PASS. Do not review only the new files. Specifically challenge whether tests are business-derived, learning changes future behavior, obsolete rules are pruned, server/model-evaluation facts are honest/fresh, and three documentation workflows are independent.

## TEST_CONTRACT

```yaml
TEST_CONTRACT:
  BUSINESS_GOAL: "A fresh chat can safely operate and improve the project without inheriting stale rules or code-derived test expectations."
  TEST_BASIS:
    - "Owner requirements in the current documentation-governance request"
    - "Reviewed Documentation System V1 invariants"
    - "docs/DOCUMENTATION_REVIEW_CRITERIA_V2.md"
    - "docs/DOCUMENTATION_AUDIT_CRITERIA_V2.md"
  ACCEPTANCE_IDS: [D2R-01..D2R-12, D2A-01..D2A-14]
  ORACLE_AUTHORITY_CLASS: COMPOSITE_APPROVED_AUTHORITIES
  ORACLE_SOURCE: "owner requirements + reviewed governance policy"
  TEST_CHANGE_CLASS: NONE
  TEST_CHANGE_AUTHORITY: "not applicable; this workflow adds governance checks without redefining product behavior"
  VIEWPOINTS: [business_outcome, negative_failure, recovery, independence, freshness, knowledge_hygiene, environment_provenance]
  POSITIVE_CASES: "cold start, auto-continue, policy promotion, environment capture, test routing"
  NEGATIVE_CASES: "stale version, stale lane cache, code-derived oracle, repeated deadlock, obsolete active rule, wrong tool environment"
  TARGETED_COMMAND: "/usr/bin/python3 tools/run_governance_checks.py"
  FULL_COMMAND: "/usr/bin/python3 tools/run_test_workflow.py docs"
  ENVIRONMENT_CLASS: WSL_DEVELOPMENT_AUTHORING
  TEST_DATA_CLASS: SYNTHETIC_AND_PROJECT_METADATA
  NATIVE_EXECUTION_ALLOWED: false
  PASS_MEANS: "documentation/control-plane V2 criteria are satisfied for the reviewed commit"
  PASS_DOES_NOT_MEAN: "source CODE_REVIEW_PASS, native validation, qualification, model benchmark readiness or HOST_READY"
```

## After V2 governance passes

Resume `WF-P00-IMPL-DEV18` from the preserved four-file WIP. Before editing, fresh-fetch state/lane refs and run runtime-state reconciliation. Do not reset to the last durable package simply because the WIP is uncommitted.
