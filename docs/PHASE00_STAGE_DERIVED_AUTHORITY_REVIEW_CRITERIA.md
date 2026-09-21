# Phase00 stage-derived authority — DESIGN_REVIEW criteria

REVIEW_TARGET: PHASE00-STAGE-DERIVED-LAB-AUTHORITY-001
DESIGN_GAP: DESIGN_GAP-P00-V03-STAGE-DERIVED-AUTHORITY-001
ORACLE_CHANGED_EXPECTED: false
NATIVE_EXECUTION_ALLOWED: false

Independent DESIGN_REVIEW must consume the exact design commit and verify all of the following.

1. Normative Phase00 contracts and every existing PROCEDURES route/exit/oracle/evidence requirement are unchanged.
2. The dependency catalog is regenerated from exact source and contains 86 procedures, 85 native procedures and 133 stages with identical procedure digests.
3. Exact authority-mode totals are independently reproduced: 94 CONCRETE_PRE_V03, 15 STAGE_DERIVED, 10 ENTRY_PROBE_AUTHORITY and 14 FENCE_BOUND_RECONCILIATION. Reviewer must reproduce TEMP-01…TEMP-05 and reject any unclassified temporal input.
4. T05-D CREATE (and the catalogued F00-10/F00-11 successors) rebind current material/profile after ENGINE rather than using a stale pre-engine plan.
5. All six RESTORE_VERIFY-after-import rows bind actual destination material/registration; T00-09/T09-A verify uses both export checkpoint and import material producer lineage.
6. The signed suite authorizes bounded derivation/probe/reconciliation rules rather than guessed future values; no generic caller-selected plan path exists.
7. Each derived producer is earlier, same suite/case/procedure and satisfies the slot-required terminal/current-material state. Process exit, awaiting or uncertain state cannot impersonate committed producer evidence.
8. Derived native binding, plan, approval, checkpoint payload and restore-envelope bindings are recomputable from immutable templates + selector-authorized evidence, and approval cannot extend the suite window.
9. Policy updates are monotonic and preserve byte-identical immutable authority partition; stage-state handoffs and derived lineages are content-addressed and parent generation/digest drift fails closed.
10. execute_stage and finalizer bind concrete/derived/entry-probe/fence-bound execution to the signed request mode and authority lineage; a wrapper-created unbound plan cannot yield accepted case evidence.
11. Late-bound proof roles are exhaustive against current ProofReader/_receipt consumers and cannot mutate execution authority except through an explicitly signed derivation slot.
12. Concrete restore stages without a declared same-case checkpoint producer require pre-V03 sealed checkpoint fixture identity; missing fixtures cannot be reclassified at runtime.
13. Proposed source changes are limited to authority/harness/reconciliation infrastructure; expected business behavior, normative contracts and PROCEDURES outcomes remain unchanged.
14. The five catalogued concrete temporal exceptions are independently justified: T07-B stages 1/2 and T07-C stages 2/3 are lock-contention exit-21 paths with no prior mutation; F00-16 stage 1 has no positive continuation and must fail closed as 16/18 if prior CREATE changed material.
15. Design specifies a future dev23-or-later TEST_CHANGE/CODE_REVIEW and candidate-specific validation reconciliation; it does not treat design review as code approval or V03 authority.

Any missing temporal dependency, mutable authority ambiguity, oracle change or source-scope widening is a DESIGN_REVIEW failure and returns to DESIGN.
