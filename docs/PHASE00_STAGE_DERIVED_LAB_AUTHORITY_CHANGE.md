# Phase00 — stage-derived LAB authority change

DESIGN_ID: PHASE00-STAGE-DERIVED-LAB-AUTHORITY-001
DESIGN_GAP_ID: DESIGN_GAP-P00-V03-STAGE-DERIVED-AUTHORITY-001
MODE: DESIGN
TARGET_SOURCE_BASE: 86bb64938a136e3f8d6cfd0266685a01cb832b77
TARGET_FUTURE_CANDIDATE_CLASS: DEV23_OR_LATER
CONTRACT_DIGEST_PRESERVED: f259656c48ed24c15bd48da2bb040950ed94d8edcf1473cf6456b96578c933ee
DEPENDENCY_CATALOG: docs/PHASE00_STAGE_DERIVED_AUTHORITY_DEPENDENCY_CATALOG_V1.json
DEPENDENCY_CATALOG_SHA256: fac26f07965257a75eee93c61f9861bf2a0e24f033008bd366cf5478849f54a0
ORACLE_CHANGED: false
EXPECTED_BUSINESS_BEHAVIOR_CHANGED: false
PRODUCT_SOURCE_CHANGE_REQUIRED: true
NATIVE_EXECUTION_AUTHORIZED: false
STATUS: DESIGN_CANDIDATE_PENDING_REVIEW

## 1. Preserved authority and acceptance

The four approved Phase00 normative contracts remain authoritative and unchanged. Existing PROCEDURES case IDs, procedure digests, route order, expected exits, oracles and required evidence remain unchanged. Local authority remains LOCAL_OPERATOR_SAME_WSL_TRUST_DOMAIN with the same disposable/no-real-credentials/no-production-mappings barriers.

This design changes only how LAB test authority represents values that cannot exist before an earlier native stage completes. It must never become a generic dynamic-plan API.

## 2. Dependency inventory

The exact dev22 procedure catalog contains 86 procedures, 85 native procedures and 133 native stages. Every native stage now has an explicit temporal-authority class in the machine catalog: 94 `CONCRETE_PRE_V03`, 15 `STAGE_DERIVED`, 10 `ENTRY_PROBE_AUTHORITY`, and 14 `FENCE_BOUND_RECONCILIATION`.

`STAGE_DERIVED` is not limited to checkpoint hashes. It covers the three import stages whose exact checkpoint comes from an earlier RESTORE_EXPORT; all six RESTORE_VERIFY stages whose plan/native binding must bind actual destination material after RESTORE_IMPORT; T05-D and F00-10 CREATE after ENGINE; F00-11 HOST_RESTART after ENGINE; and T00-14 positive continuation stages whose current material/profile comes from an earlier stage.

ENTRY_ONLY is never treated as a product purpose: those ten native stages retain the reviewed entry-probe authority model. RECONCILIATION_ONLY is explicitly fence/read-state bound rather than mislabelled as ordinary concrete execution authority.

Concrete restore import/verify stages without a same-case producer must use exact sealed pre-V03 checkpoint fixtures. A concrete successor is permitted only when the reviewed case does not require a late execution input; runtime fallback from CONCRETE to DERIVED is forbidden.

## 3. Signed suite request model

A `lab_acceptance_suite` native request has exactly one catalog-authorized authority mode.

- `CONCRETE_PRE_V03`: route, interface, plan_ref. Semantics remain dev22-compatible.
- `STAGE_DERIVED`: route, interface, derivation_slot_ref. It contains no future concrete plan_ref; the signed slot is the sole authority for later materialization.
- `ENTRY_PROBE_AUTHORITY`: route `ENTRY_ONLY` plus exact reviewed entry-probe profile/set ref. It is not converted into a fake product purpose.
- `FENCE_BOUND_RECONCILIATION`: route `RECONCILIATION_ONLY` plus exact reconciliation-slot/ref authority. Concrete recovery authority must bind the actual original fence or reviewed detached-read state before consumption.

The request mode must exactly match the dependency catalog for the same case/stage. Dual specification, runtime mode switching, an extra derived stage, a missing slot, or a caller-supplied plan ref outside the selected mode fails before V03.

T00-01 remains document-only. The previously reviewed ENTRY_ONLY qualification/trust matrices remain test authority and must be carried into TEST_CHANGE 006 without changing expected behavior.

## 4. Stage derivation slot

Each `lab_stage_derivation_slot` is content-addressed and immutable before V03. It binds at least: schema version; candidate/source/build/test/contract identities; suite execution_id; case_id; procedure_digest; stage_index; route; interface; plan_template_ref; native_binding_template_ref when required; an ordered `producer_dependencies` list; per-producer selectors; allowed late semantic paths; allowed derived object roles; immutable authority partition digest; maximum approval lifetime; and withdrawn=false.

A slot may consume more than one earlier producer, but every producer is individually fixed by stage index, route, required terminal state and selector allowlist. Current restore-verify slots can therefore take checkpoint identity from RESTORE_EXPORT and destination material/registration from RESTORE_IMPORT without allowing either producer to supply unrelated plan fields.

The fifteen current STAGE_DERIVED rows are exactly those enumerated by the dependency catalog. In addition to checkpoint derivation, the catalog requires post-ENGINE rebinding for T05-D/F00-10/F00-11 and current-material rebinding for the T00-14 positive continuation. All six verify-after-import rows bind actual destination material rather than a guessed registration/before state.

A slot cannot name an arbitrary producer result. Every producer must be earlier in the same case, same suite execution_id, same procedure digest and same fixture/result lineage. Required `COMMITTED_TERMINAL` producers cannot be replaced by process exit, an awaiting/uncertain fence or a caller observation. A wait/uncertain producer must be reconciled to the slot's required state before a successor can be derived.

## 5. Plan template

`lab_stage_plan_template` is immutable pre-V03 authority. It carries the complete reviewed plan intent except explicitly allowlisted late paths. Static host/owner/candidate/content/target/budget/purpose/route choices are fixed; a late profile may only be selected from a signed profile-catalog allowlist by the existing profile matcher using trusted producer material.

When current material affects native after-state checks, the slot also references an immutable `lab_native_binding_template`. The derived native binding may fill only reviewed material/profile-dependent fields (for example `after_by_action` and the exact profile-related binding) from signed producer selectors. It cannot change executable policy, volume/path authority, timeout ceilings, payload authority or action set.

Materialization fills only slot-authorized values, derives the concrete native binding first when applicable, then calls the existing pure plan builder/checker. The product resolver recomputes semantic plan bytes and plan_digest; it never accepts caller-supplied plan or native-binding bytes as authority. `semantic.before` must equal the trusted stage-state handoff when that path is late-bound, and expected_after must be produced by the signed transition template rather than copied from an untrusted caller.

The concrete approval is deterministic from the derived plan plus immutable slot bounds. It must use the suite owner, exact interface/purpose/classes, a maintenance window contained by the signed suite window, and expiry no later than the suite expiry. Derived approval cannot extend authority lifetime.

## 6. Checkpoint derivation

For RESTORE_IMPORT, checkpoint_sha256 and checkpoint bytes come only from the committed NATIVE_OPERATION_AFTER evidence of the slot's producer RESTORE_EXPORT stage. The source export plan and its native_binding export_path are immutable authority; the derived checkpoint_payload path must equal that export_path and its bytes/hash must equal the committed checkpoint observation.

A checkpoint value from another case, execution_id, uncommitted process exit, untrusted file scan or caller argument is rejected.

For RESTORE_VERIFY, checkpoint identity comes from the applicable export or sealed pre-V03 fixture, while `semantic.before`, target registration and material-dependent native binding come from the immediately preceding RESTORE_IMPORT stage-state handoff. For T00-09/T09-A this is an explicit multi-producer derivation: stage 0 supplies checkpoint identity and stage 1 supplies destination material. The current restore_envelope proof is materialized only after exact checkpoint identity and destination isolation facts exist; its claim digest supplies expected_envelope.

For verify-after-import cases with a pre-V03 checkpoint fixture (F00-12, T09-D, T09-H and T09-I), the checkpoint authority remains static but destination material is still derived after import. A stale pre-import `before` state is never accepted merely because the checkpoint was known.

The resulting import/verify plan is therefore linked to exact producer outputs without predicting checkpoint, registration or current material before they exist.

## 7. Policy generations and partitions

Generation 1 remains the V02-installed base policy. It contains the signed immutable authority partition, including registration/design/code/lab plan/suite, concrete plans and approvals, native bindings/profile/executable policy, plan templates and derivation slots.

Later generations are monotonic. Each generation records parent policy digest, previous generation number, immutable_partition_digest, added object refs grouped by role, and the reason/event identity. Generation must increase exactly by one for a committed augmentation.

A trusted `lab_stage_state_handoff` is a content-addressed normalization of an earlier stage's accepted current/terminal material and selected outputs. It binds the exact suite/case/procedure/stage/plan, normalized exit/state, protected evidence digest and whether the stage reached the slot-required committed state. It cannot be synthesized from process exit alone. Derived stages may consume only selectors authorized by their signed slot.

The immutable partition is the exact signed set of base refs, not the entire future namespace of a role. It is byte-identical across all generations: no base ref may be removed, withdrawn, replaced or repointed. A signed slot may authorize an additional ref under an existing multi-valued role such as `native_binding`, `execution_plan` or `approval`; that addition is outside the immutable base-ref set and is accepted only through verified lineage. Single-selection registration/design/code authority cannot gain additional refs. Other derived/evidence additions may only add content-addressed refs under roles authorized by the signed slot or reviewed evidence controller.

Before replacing the Windows trust Policy value, validation tooling must read and hash the current value, require exact expected parent generation/digest, construct the next full policy, validate it as NativeStore, write the complete new value under the existing protected anchor, reread it and require exact hash/generation. A concurrent or unexpected parent blocks; no force overwrite.

Private signing key bytes are never involved in a runtime policy generation update. Authority for a derived plan comes from the already signed suite slot plus exact producer evidence, not a new ad-hoc signature.

## 8. Derived authority lineage object

Before a DERIVED stage can execute, the controller creates `lab_derived_stage_authority` containing: slot_ref; base suite ref/execution_id; case/stage/procedure identity; an ordered list of producer stage refs/state-handoff refs/evidence digests; materialized selector values; plan_template_ref; native_binding_template_ref when applicable; concrete native_binding_ref; concrete execution_plan_ref; concrete approval_ref; checkpoint_payload_ref when applicable; restore_envelope_ref when applicable; immutable_partition_digest; parent/new policy generation; created_at; expires_at; withdrawn=false.

The lineage object and all derived objects are added in one validated policy generation before execute_stage resolves the request.

Product harness resolution selects exactly one unwithdrawn lineage object for the requested slot/current suite/case/stage. It recomputes every late value and the concrete plan/approval from base authority plus producer evidence. Multiple matches, absent match, digest drift, producer evidence not committed, wrong generation lineage or a value outside the slot allowlist blocks before native execution.

## 9. Harness execution and finalization

`harness_controller.authorize_suite` must accept the four catalog-authorized request modes and statically validate the corresponding concrete ref, derivation slot, entry-probe authority or reconciliation authority. It must not require future concrete objects for STAGE_DERIVED/FENCE_BOUND rows during V02 static validation.

`execute_stage` for CONCRETE remains the existing product path. For STAGE_DERIVED it resolves and verifies `lab_derived_stage_authority`, obtains the exact concrete plan ref from verified lineage, then enters the same production request path. ENTRY_PROBE uses only the reviewed probe profile; FENCE_BOUND_RECONCILIATION binds the current durable fence/detached-read state through the accepted reconciliation machinery. There is no public CLI argument for an arbitrary plan or slot override.

Each `lab_case_stage` record gains an `authority_lineage_ref` and explicit authority mode. CONCRETE uses null lineage; STAGE_DERIVED requires the exact derived lineage; ENTRY_PROBE and FENCE_BOUND_RECONCILIATION bind their corresponding authority refs. `validate_stage`/`finalize_case` verify that the stage plan_digest and lineage match the signed suite request. Finalization therefore cannot accept a dynamically composed plan merely because its output looks valid.

The existing execute_stage path remains the only accepted native stage executor. A validation wrapper that calls prepare_execution with an unbound plan cannot produce accepted stage evidence.

## 10. Late-bound proof slots

The same design formalizes current-policy proof augmentation for source_manifest, protection, restore_envelope, user_init_receipt, c3_postchecks, operation_postcheck, run_revocation, read_absence_observation and restore_result.

Each slot binds role, accepted consumer, exact scope fields, materialization boundary, owner/native evidence class, freshness/not-before rule and permitted policy-generation transition. A proof may be added only after every scope fact exists. Proof additions cannot alter execution authority unless a stage derivation slot explicitly consumes the proof ref/value as an allowlisted late field.

ProofReader continues exact role/scope/freshness selection. Placeholder scopes are forbidden.

## 11. V02 intake and static resolvability

V02 validation tooling must validate all four authority classes against the exact dependency catalog. CONCRETE rows require their full current object graph. STAGE_DERIVED rows require complete signed plan/native-binding templates, producer selectors and immutable dependencies. ENTRY_PROBE rows require the reviewed probe profile/set. FENCE_BOUND_RECONCILIATION rows require an exact signed original-plan/fence-selection rule without inventing a future fence.

Static status distinguishes `CONCRETE_RESOLVABLE`, `SLOT_RESOLVABLE`, `ENTRY_PROBE_RESOLVABLE` and `RECONCILIATION_SLOT_RESOLVABLE`. A slot-resolvable status means only that the signed rule is complete; it never claims the future checkpoint, current material, fence or concrete plan already exists.

For every concrete restore request without a prior successful export dependency, required checkpoint fixture bytes/digest must already exist and be sealed before signing. A missing pre-V03 fixture cannot be silently converted to a derived request.

## 12. Full dependency audit rule

The machine catalog is normative for this design candidate and covers all 133 native stages. Future changes to PROCEDURES or any consumer that introduces a new late semantic dependency invalidate this catalog and require design/test review before V02 signing.

Implementation must include a static analyzer/test that recomputes stage count, route order/procedure digests and the exact authority-mode totals (94 concrete, 15 stage-derived, 10 entry-probe, 14 fence-bound reconciliation). It must reproduce the TEMP-01…TEMP-05 challenges recorded in the catalog and reject any stage whose temporal authority class is missing or inconsistent with reviewed procedure/test authority.

DESIGN_REVIEW must independently inspect temporal dependencies beyond checkpoint. In particular it must verify T05-D rebind-after-engine, all six verify-after-import destination-material dependencies, T00-14 positive continuation, reconciliation fence binding, target identity, reboot epoch and proof receipts. Runtime facts that affect only proof scope belong in proof slots; facts that alter plan semantics/native binding/approval/payload authority require a derivation slot.

## 13. Product/source change scope

Expected product source changes are limited to the LAB acceptance authority path: harness_controller request parsing/resolution/finalization, explicit stage-state/lineage schemas, a new internal stage-authority resolver, and narrowly scoped trust/reconciliation helpers needed to validate immutable partitions and exact fence lineage. Derived native-binding materialization is internal to this authority path and must still pass the existing `validate_binding`/plan/authority predicates. Core business plan semantics, ordinary SITE admission, normative contracts and PROCEDURES outcomes remain unchanged unless DESIGN_REVIEW finds an unavoidable conflict.

Validation tooling changes include the graph compiler/static verifier, V02 intake/materializer, a monotonic policy updater, late-proof materializer and fixture/preparation controller. These are separately test-reviewed and cannot weaken product checks.

A future implementation produces a new code candidate (dev23 or later), new source/test digests and formal CODE_REVIEW. Dev22 remains accepted historical code but cannot continue V03; candidate-specific V02/prodlike/LAB bindings must be reconciled for the new reviewed source before validation resumes.

## 14. Required negative coverage

At minimum reject: authority mode inconsistent with the 133-stage catalog; derived mode on an unlisted stage; producer stage not earlier; missing or foreign stage-state handoff; wrong case/suite/execution/procedure; producer process exit without slot-required committed/current-material evidence; wrong checkpoint hash/path/bytes; stale or foreign restore envelope; stale pre-ENGINE material/profile; derived native binding outside its template; added late field not in slot; changed immutable field; approval outside suite window; duplicate lineage; policy generation skip/rollback/concurrent parent drift; immutable partition mutation; derived object not content-addressed; concrete restore missing pre-V03 fixture; ENTRY_ONLY mapped to a product purpose; reconciliation not bound to the actual fence/read state; finalizer stage plan not matching lineage; arbitrary prepare_execution bypass; proof materialized before scope exists; and any base authority withdrawal/replacement during V03.

## 15. Review and return sequence

This design is not implementation authority until independent DESIGN_REVIEW PASS. After DESIGN_REVIEW, author TEST_CHANGE 006 / independent TEST_REVIEW with ORACLE_CHANGED=false for the exact source/tooling delta. Only then implement a new product candidate, run author tests, formal CODE_REVIEW, rebuild/reconcile candidate-specific validation prerequisites and return to V02B.

No native case, authority signing, qualification, SITE action or HOST_READY assessment occurs in DESIGN or DESIGN_REVIEW.
