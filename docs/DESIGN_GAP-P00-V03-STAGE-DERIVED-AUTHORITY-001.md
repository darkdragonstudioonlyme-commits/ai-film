# DESIGN_GAP-P00-V03-STAGE-DERIVED-AUTHORITY-001

DESIGN_GAP_ID: DESIGN_GAP-P00-V03-STAGE-DERIVED-AUTHORITY-001
MODE: DESIGN
PHASE: 00 — Host / WSL
PRESERVED_RUN: RUN-P00-VALIDATION-002
BASE_SOURCE_COMMIT: 86bb64938a136e3f8d6cfd0266685a01cb832b77
BASE_VALIDATION_HEAD: 197627470480b6718e8d0326b35f853b7369d7d8
BASE_CANONICAL_MAIN: 2834341da40d45471109d83c6c68376b43251151
ORACLE_CHANGED: false
EXPECTED_BUSINESS_BEHAVIOR_CHANGED: false
PRODUCT_SOURCE_CHANGE_REQUIRED: true
NATIVE_EXECUTION_AUTHORIZED: false
STATUS: DESIGN_CANDIDATE

## Gap

The reviewed Phase00 restore contract requires a source checkpoint to be exported and sealed before the exact checkpoint is transferred/imported into a destination. T00-09, T07-I and T09-A contain ordered RESTORE_EXPORT → RESTORE_IMPORT flows.

Accepted dev22 LAB authority fixes one concrete content-addressed execution_plan per native suite stage before V03. RESTORE_IMPORT authority must already contain semantic.expected_checkpoint and a checkpoint_payload ref whose payload digest equals that exact checkpoint. The value is not knowable until the earlier RESTORE_EXPORT finishes and its checkpoint SHA is observed.

A guessed digest, placeholder, unrelated pre-existing checkpoint, pre-V02 native export, or post-sign replacement of the suite's plan_ref would weaken or bypass reviewed authority. Validation-only proof augmentation cannot solve this because the late value is part of execution authority, not merely evidence.

WORKFLOW-REVIEW-P00-V03-LATE-BOUND-EXECUTION-003 independently concluded that accepted product/harness source must change while Phase00 business/test oracles remain unchanged.

## Required design outcome

Define a bounded LAB authority model in which every one of the 133 native stages has an explicit temporal authority class. The signed suite must authorize exact concrete, stage-derived, entry-probe or fence-bound reconciliation rules before V03; later materialization may consume only selector-authorized facts from exact earlier stage/fence/proof lineage.

The design must support multi-producer derivation where required: checkpoint identity can come from RESTORE_EXPORT while current destination material comes from RESTORE_IMPORT. It must also enforce the normative rebind-after-ENGINE behavior and derive material-dependent native bindings rather than only replacing checkpoint fields.

The model must incorporate the already reviewed late-bound proof-slot requirement and keep ENTRY_ONLY/reconciliation semantics explicit so the correction does not special-case one checkpoint while leaving another temporal dependency hidden.

Machine-readable inventory: docs/PHASE00_STAGE_DERIVED_AUTHORITY_DEPENDENCY_CATALOG_V1.json, SHA256 fac26f07965257a75eee93c61f9861bf2a0e24f033008bd366cf5478849f54a0.

## Non-goals

This design does not change expected exits, procedure oracles, required evidence IDs, local-authority assurance, containment, qualification, SITE or HOST_READY rules. It does not authorize native execution, authority signing, or implementation before DESIGN_REVIEW.
