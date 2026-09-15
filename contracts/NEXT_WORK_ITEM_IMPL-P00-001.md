# NEXT_WORK_ITEM

```yaml
WORK_ITEM_ID: IMPL-P00-001
MODE: IMPLEMENTATION
PHASE: "00 — Host / WSL"
STATUS: READY_TO_START
TARGET_GATE: CODE_REVIEW_PASS
PHASE_GATE: HOST_READY
GOAL:
  "Author Phase00 implementation package from exact approved V2 contracts,
   with tests/evidence contracts and handoff for independent code review."
ENTRY_CONDITION:
  - "REVIEW-P00-002: PASS for exact V2 contract-set."
  - "DR-P00-001…006: REVIEW_PASS at design scope; no required design revision."
  - "Verify source contract hashes against DESIGN_REVIEW_APPROVAL_V2.json."
INPUTS:
  - Blueprint_V2
  - AI_FILM_PROJECT_STATE_V5
  - PHASE00_INFRA_DESIGN_V2
  - PHASE00_ACCEPTANCE_MATRIX_V2
  - PHASE00_FAILURE_RECOVERY_PLAN_V2
  - PHASE00_EVIDENCE_AND_RESEARCH_REGISTER_V2
  - PHASE00_DESIGN_REVIEW_V2
  - DESIGN_REVIEW_APPROVAL_V2
  - FINDING_DISPOSITIONS_V2
APPROVED_CONTRACT_SET_DIGEST: "f259656c48ed24c15bd48da2bb040950ed94d8edcf1473cf6456b96578c933ee"
SCOPE:
  - "preflight / dry-run / apply / verify / support-bundle / recovery-runbook contracts."
  - "CREATE_NEW, ADOPT_EXISTING, ENGINE_BOOTSTRAP and explicit restore purposes."
  - "Host admission/fence/capacity, plan/identity/trust, qualification/actor checks."
  - "Pre-C3 protection, terminal evidence and pre-boot restore envelope enforcement."
  - "Evidence E00-01…17, scoped bundle redaction/caps/exits and nonrecursive manifests."
  - "Traceability to AC00-01…08, T00-01…14, F00-01…16 and expanded subcases."
ALLOWED:
  - "Write source/config schemas/test fixtures/docs in a separate implementation workspace."
  - "Run safe workspace/unit/fixture tests; label actual environment and limitations."
  - "Prepare native Windows/WSL test harness/plans without executing them on user host."
  - "Record unbound execution values honestly; no sample value becomes SITE observation."
FORBIDDEN:
  - "Overwrite Blueprint or historical design/review packages."
  - "Change public contracts, acceptance, routes, phase boundary or architecture without review."
  - "Install/configure/restart Windows/WSL, provision lab or import checkpoint on a real host in this work item."
  - "Forge qualification, approvals, observed facts or test results."
  - "Self-approve code or claim HOST_READY/production readiness."
  - "Expand into Phase01, Docker, GPU, model selection or later architecture."
DESIGN_GAP_RULE:
  "If a required contract is missing or cannot be implemented as approved,
   create DESIGN_GAP with evidence/affected scope and transition to design;
   do not silently replace or waive the contract."
OUTPUT:
  - "Versioned Phase00 source package with implementation/dependency manifest."
  - "Schemas/config templates and clearly labeled synthetic fixtures."
  - "Requirement-to-code-to-test matrix; implemented and not-implemented items explicit."
  - "Actual workspace test report plus native LAB/SITE NOT_RUN or BLOCKED inventory."
  - "Recovery/operator docs and CODE_REVIEW handoff with source/diff hashes."
ACCEPTANCE_FOR_AUTHOR_HANDOFF:
  - "Source implements approved scope without hidden bypass or unrelated changes."
  - "Defined negative cases have concrete test fixtures/oracles; execution status truthful."
  - "No untracked design deviation; unmet work remains PARTIAL, not COMPLETE."
  - "Code-review package identifies exact build/config/test content and all limitations."
EXIT_CONDITION:
  "Author-complete implementation candidate ready for CODE_REVIEW, not self-approved."
NEXT_MODE: CODE_REVIEW
NEXT_WORK_ITEM: CODE-REVIEW-P00-001
TRANSITION_STATUS: PLANNED_NOT_EXECUTED
```

DESIGN_REVIEW_PASS permits code authoring, not target rollout. Native LAB execution requires the reviewed build and registered/approved lab route; SITE active entry additionally requires valid actual qualification plus stage-specific host/owner/protection evidence. These prerequisites are distinct from safe workspace tests during implementation.
