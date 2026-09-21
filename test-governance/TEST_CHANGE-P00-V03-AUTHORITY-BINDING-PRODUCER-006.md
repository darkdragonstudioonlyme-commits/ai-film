# TEST_CHANGE-P00-V03-AUTHORITY-BINDING-PRODUCER-006

~~~yaml
TEST_CHANGE_ID: TEST_CHANGE-P00-V03-AUTHORITY-BINDING-PRODUCER-006
RUN_ID: RUN-P00-VALIDATION-002
WORK_ITEM: TEST-DESIGN-P00-V03-STAGE-DERIVED-AUTHORITY-006
TARGET_BASE_SOURCE_COMMIT: 86bb64938a136e3f8d6cfd0266685a01cb832b77
DESIGN_GAP: docs/DESIGN_GAP-P00-V03-STAGE-DERIVED-AUTHORITY-001.md
DESIGN_RECORD: docs/PHASE00_STAGE_DERIVED_LAB_AUTHORITY_CHANGE.md
DESIGN_REVIEW: reviews/DESIGN-REVIEW-P00-V03-STAGE-DERIVED-AUTHORITY-001.md
DEPENDENCY_CATALOG: docs/PHASE00_STAGE_DERIVED_AUTHORITY_DEPENDENCY_CATALOG_V1.json
DEPENDENCY_CATALOG_SHA256: fac26f07965257a75eee93c61f9861bf2a0e24f033008bd366cf5478849f54a0
COVERAGE_EVIDENCE: test-governance/design-evidence/TEST-DESIGN-P00-V03-STAGE-DERIVED-AUTHORITY-006-COVERAGE.json
CHANGE_CLASS: PRODUCT_HARNESS_AND_VALIDATION_AUTHORITY_INFRASTRUCTURE
ORACLE_CHANGED: false
EXPECTED_BUSINESS_BEHAVIOR_CHANGED: false
PRODUCT_SOURCE_CHANGE_REQUIRED: true
PRODUCT_IMPLEMENTATION_AUTHORIZED: false
NATIVE_EXECUTION_AUTHORIZED: false
AUTHORITY_GRAPH_SIGNING_AUTHORIZED: false
TEST_REVIEW_STATUS: PENDING
STATUS: PENDING_INDEPENDENT_REVIEW
~~~

## Authority and purpose

This TEST_CHANGE implements no code. It binds the exact independently reviewed design to a future product/harness and validation-tooling change set. The approved Phase00 contracts and exact current PROCEDURES remain the behavioral oracle. Expected exits, route order, required evidence and all business gates are unchanged.

The reviewed design replaces the impossible assumption that every future stage input can be concrete before V03 with four explicit temporal authority classes: 94 CONCRETE_PRE_V03, 15 STAGE_DERIVED, 10 ENTRY_PROBE_AUTHORITY and 14 FENCE_BOUND_RECONCILIATION.

## Exact product-source scope

Future implementation is authorized to ADD only `src/aifilm_p00/native/stage_authority.py` and MODIFY only `src/aifilm_p00/native/harness_controller.py`.

The new internal resolver owns signed slot/template validation, stage-state handoff validation, derived native-binding/plan/approval recomputation, authority-lineage verification, immutable signed-base-ref digest validation and exact authority-mode resolution. It is not a public CLI or generic plan factory.

`harness_controller.py` may extend signed suite request parsing, execute-stage resolution and stage/finalizer lineage schemas for the four reviewed modes. After an exact concrete plan ref is resolved, execution still enters the existing accepted production request path.

The following remain byte-identical in the product candidate: `authority.py`, `plans.py`, `native/harness_cases.py`, `native/request_entry.py`, `resume.py`, `recovery.py`, required-native-test inventory and all four normative Phase00 contracts. If implementation cannot satisfy the design within this source scope, it must return to DESIGN/WORKFLOW_REVIEW rather than silently widening the change.

## Temporal authority coverage

All 133 native stages must match the reviewed dependency catalog. The fifteen STAGE_DERIVED stages are exact and closed; no runtime reclassification is permitted. T00-09/T09-A verification is multi-producer: export supplies checkpoint identity and import supplies current destination material. All six verify-after-import paths bind actual destination registration/material. T05-D/F00-10/F00-11 use post-ENGINE rebind. T00-14 positive continuation uses current stage lineage.

ENTRY_ONLY remains the reviewed entry-probe model and is never converted to a product purpose. RECONCILIATION_ONLY binds the actual original fence or reviewed detached-read lineage and cannot use a guessed pre-V03 fence.

The five reviewed concrete temporal exceptions remain exactly T07-B stages 1/2, T07-C stages 2/3 and F00-16 stage 1; implementation may not generalize those exceptions.

## Policy and proof model

Generation 1 is the signed V02 base-ref set. A later policy generation may add only content-addressed objects permitted by an exact signed slot/proof rule, must name the exact parent policy digest/generation and must preserve every signed base ref byte-identically. Registration/design/code remain single-selection.

All nine reviewed late-bound proof roles are covered: source_manifest, protection, restore_envelope, user_init_receipt, c3_postchecks, operation_postcheck, run_revocation, read_absence_observation and restore_result. Concrete proof bytes can be added only after their full scope exists and must still satisfy the accepted ProofReader role/scope/freshness predicates.

## Validation-tooling scope

Future validation tooling may add the compiler/common/static verifier/fixture controller/policy updater/late-proof materializer listed in the coverage artifact, and modify only V02 intake, pre-V03 stage and tooling manifest. The existing local signing implementation remains separate; compiler/verifier author tests cannot access private signing-key material or write the canonical inbox/HKLM/native environment.

V02 static verification must distinguish CONCRETE_RESOLVABLE, SLOT_RESOLVABLE, ENTRY_PROBE_RESOLVABLE and RECONCILIATION_SLOT_RESOLVABLE. A slot status proves the signed rule is complete; it never asserts that a future checkpoint, fence, material state or proof already exists.

## Required adversarial coverage

TD006-01 through TD006-16 in the machine-readable coverage artifact are mandatory. In particular tests must kill the original false-green classes: pure authorization without native binding, future-value placeholders, stale pre-ENGINE material, verify-after-import stale material, foreign producer lineage, mutable signed base refs, incomplete qualification entry matrices, dynamic-plan bypass and process-exit-only producer evidence.

No test may manufacture a new expected outcome from implementation behavior. No skipped/missing stage or preparation may be removed from coverage to make a suite green.

## Review and implementation gate

Independent TEST_REVIEW must consume the exact author commit/tree and independently reconcile the coverage artifact against the reviewed design/catalog and accepted source. It must confirm ORACLE_CHANGED=false and the exact file-scope allowlist above.

Only TEST_REVIEW PASS authorizes a dev23-or-later implementation candidate. That future candidate still requires author regression, formal TEST_REVIEW provenance, formal CODE_REVIEW, candidate-specific V02/prodlike/LAB reconciliation and a fresh authority graph before V03.

This TEST_CHANGE does not sign authority, install policy, execute a native case, issue qualification, enter SITE or assess HOST_READY.
