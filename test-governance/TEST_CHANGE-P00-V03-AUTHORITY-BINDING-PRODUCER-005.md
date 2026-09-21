# TEST_CHANGE-P00-V03-AUTHORITY-BINDING-PRODUCER-005

~~~yaml
TEST_CHANGE_ID: TEST_CHANGE-P00-V03-AUTHORITY-BINDING-PRODUCER-005
RUN_ID: RUN-P00-VALIDATION-002
WORK_ITEM: TEST-DESIGN-P00-V03-AUTHORITY-BINDING-PRODUCER-001
TARGET_SOURCE_COMMIT: 86bb64938a136e3f8d6cfd0266685a01cb832b77
TARGET_PACKAGE_SHA256: c2ea52087039f4c7b98c53a7cc0eaf1a4a0f931645f86491bf2eb8ef12956aae
SOURCE_DIGEST: 69fdc1840472a96bce8f8841e4d780543827e3cefdd3fe3bc8445f8a1fb4a0d6
TEST_DIGEST: 47d4ae767b26b05ef16d6809ea9377ef4e1b21bfbc4c44093dbd1cc158b75698
CONTRACT_DIGEST: f259656c48ed24c15bd48da2bb040950ed94d8edcf1473cf6456b96578c933ee
VALIDATION_EVIDENCE_HEAD: 932dd8e05dd96996433d83dd2171e3f176a1b000
CHANGE_CLASS: INFRASTRUCTURE_ONLY_TEST_PRODUCER_CONTRACT
ORACLE_CHANGED: false
EXPECTED_BUSINESS_BEHAVIOR_CHANGED: false
PRODUCT_SOURCE_CHANGE_AUTHORIZED: false
NATIVE_EXECUTION_AUTHORIZED: false
AUTHORITY_GRAPH_SIGNING_AUTHORIZED: false
RECIPE_CATALOG: test-governance/P00_V03_AUTHORITY_BINDING_PRODUCER_RECIPE_CATALOG_V1.json
RECIPE_CATALOG_SHA256: 5d321d4b6b8f8c47bbd257324a51af7d0bb564ec73d1e2532c2dba2b6645c2b5
COVERAGE_EVIDENCE: test-governance/design-evidence/TEST-DESIGN-P00-V03-AUTHORITY-BINDING-PRODUCER-005-COVERAGE.json
COVERAGE_EVIDENCE_SHA256: 3aadec58f279005c4dbc29c11b55679f02d11593ad90d6fb6e4868f0749f4fc7
TEST_REVIEW_STATUS: PENDING
STATUS: PENDING_INDEPENDENT_REVIEW
UPSTREAM_AUTHORITY:
  - contracts/PHASE00_INFRA_DESIGN_V2.md
  - contracts/PHASE00_ACCEPTANCE_MATRIX_V2.md
  - contracts/PHASE00_FAILURE_RECOVERY_PLAN_V2.md
  - test-governance/TEST_GAP-P00-V03-AUTHORITY-BINDING-001.md
  - workflow-health/HEALTH_REVIEW-WF-P00-V02B-BINDING-PRODUCER-018.md
  - reviews/WORKFLOW-REVIEW-P00-V02B-BINDING-PRODUCER-001.md
~~~

## 1. Purpose and unchanged test authority

This TEST_CHANGE defines the missing validation/test infrastructure producer. It does not change a required PASS/FAIL outcome, accepted normalized exit, business requirement, authority model, containment rule, qualification rule, evidence oracle or HOST_READY rule.

The four approved Phase00 contracts remain business authority. Exact accepted `aifilm_p00.native.harness_cases.PROCEDURES` remains case/route/exit/oracle/evidence authority. The reviewed recipe catalog added by this change is infrastructure authority only: it freezes how the existing 78 native preparation tokens and 133 native stages are produced so implementation cannot infer fixtures from current implementation behavior.

The document-only T00-01 preparation `EXACT_REVIEW_SET` remains document review and is deliberately outside the 78 native preparation recipes. Coverage evidence records 86 total cases, 85 native cases, one document-only case, 133 native requests, 65 ARRANGE and 13 OBSERVE native preparation types.

## 2. Component A — V02B authority graph compiler

The compiler is validation-only and staging-only. It may consume only:

- exact source/package/build/test/contract/candidate/candidate-binding identities;
- exact reviewed `PROCEDURES`, this TEST_CHANGE and the pinned recipe-catalog SHA;
- fresh same-trust local observations collected after compiler INTENT: local identity, host boot/principal, Windows/runtime/package/config/distro/volume facts and executable byte identities;
- exact sealed dev22 LAB technical/recovery facts and artifact seal;
- reviewed design/code authority and current local trust-anchor/public-key metadata;
- protected raw identity fields already required by current local-authority schema.

It must use existing pure product builders/validators (`make_plan`, `check_plan`, `interface_check`, `authorize`) for product-shaped objects wherever their positive-authority semantics apply. It must not sign, read private signing-key bytes, modify the canonical authority inbox, write HKLM, start the LAB, issue qualification, create native PASS evidence or assess HOST_READY.

### 2.1 Staging output

The compiler creates a private staging tree only. Output consists of canonical content-addressed JSON objects, unsigned envelope candidate, role-pin manifest, request index and compiler receipt. File/object hashes are computed from canonical bytes. Identical bytes may deduplicate only within the same role; role or byte differences never deduplicate.

The graph must contain exactly 86 suite case rows, 85 native fixture specs and 133 native request stages. Every object reachable from a plan or native binding must exist and be content-addressed. No document may self-pin or learn a trust digest from the same byte stream it is about to authorize.

For every non-ENTRY_ONLY stage the route/interface/purpose mapping is fixed by the recipe catalog. Every such execution plan resolves an authenticated `native_binding`; that binding resolves `profile_catalog` and `executable_policy`; and purpose-specific payload, release-metadata, checkpoint, support, verification, endpoint and proof refs required by accepted product consumers are present and pinned.

### 2.2 Freshness and drift

All mutable observations belong to one compiler transaction. The compiler receipt binds at minimum host boot identity, execution principal, source/test digests, runtime/package identity, config digest, distro registration set, physical volume identities and every executable byte identity used by executable policy.

Immediately before a staged graph can be reviewed or signed, the static verifier re-observes sign-critical mutable identities. Any material difference invalidates the staged graph as a whole; the graph is recompiled rather than edited in place. The existing approval/suite lifetime of at most 24 hours is unchanged and cannot be extended by a stale compiler receipt.

## 3. ENTRY_ONLY contract

`ENTRY_ONLY` is a harness route, not a product purpose. No implementation may silently map it to the easiest passing interface.

The native inventory has ten ENTRY_ONLY stages. T00-14 uses the catalog profile `LAB_POSITIVE_ENTRY_BASELINE`: a bounded PASSIVE/preflight LAB carrier proves that a correctly registered disposable LAB may enter without a prior qualification receipt.

The remaining nine stages are `NEGATIVE_ENTRY_PROBE`. The signed execution-plan document acts as a carrier and binds a content-addressed `entry_probe_set_ref`. The referenced probe-set object contains the actual product entry plans, isolated policy/role overlay refs, expected exit/reason predicates and required evidence for that case. Probe-only registration/qualification/trust objects are not added to the primary LAB registration selection merely to make V02 pure authorization pass.

T14-A, T14-B and T14-C each require an actual probe matrix covering all four contract classes: active preflight, apply, active verify, and recovery/reconciliation. A single shared `authorize()` unit call cannot satisfy that requirement. The catalog also freezes fault variants: T14-B covers FAIL, withdrawn, gate-blocker and >30-day expiry; T14-C covers design/contract, build, test-set, profile and payload mismatch. For T14-A/B/C the reviewed contract is the Cartesian product of each fault variant with all four entry classes.

### 3.1 Pre-V02 handling

During V02 construction, negative entry probes are only validated statically. The primary LAB authority partition stays unchanged. Static validation builds each probe overlay in memory, confirms the intended first violated predicate belongs to the case's reviewed exit/reason family, confirms no positive native admission is accidentally created, and performs zero native action.

### 3.2 V03 actual entry probe

After V02 closes, the V03 controller may run a negative ENTRY_ONLY probe only under the global host guard. It preserves the exact primary policy bytes/hash, installs the exact reviewed content-addressed test overlay, invokes the real production entrypoint, requires the expected rejection before any prohibited native child starts, restores the exact primary policy, verifies the restored hash/generation, and only then releases the guard.

An overlay restore failure, unexpected positive admission, unexpected native-child start, or authority-partition mismatch terminates the campaign. Entry-probe overlays remain disposable/non-production and may not introduce production mappings or credentials.

## 4. Component B — static native-resolvability verifier

The verifier is a no-execution tool. Its PASS label is exactly `STATIC_NATIVE_RESOLVABLE`; it is not V02 READY and not native test evidence.

It must fail closed unless all of the following are true:

1. exact source/test/contract/candidate/procedure/recipe identities match reviewed inputs;
2. coverage is exactly 86 total cases, 85 native cases, 133 native stages and all 78 native preparation tokens, without duplicate or unknown rows;
3. the primary `registration`, `design` and `code` authority selection is unambiguous and primary registration remains the contained local-operator LAB;
4. every non-ENTRY_ONLY stage passes existing interface/plan/pure-authority checks under the primary LAB graph;
5. every execution stage that can reach native composition resolves a schema-valid `native_binding`, its exact plan profile appears in authenticated `profile_catalog`, and `executable_policy` is exact host/build/contract scoped;
6. every transitive payload/release metadata/support document/checkpoint/verification/proof ref needed by the selected purpose exists, hashes correctly, has the expected role and is pinned in the appropriate graph/overlay;
7. T00-14 positive ENTRY_ONLY resolves its explicit positive LAB carrier;
8. each negative ENTRY_ONLY probe set builds an isolated in-memory overlay and satisfies its reviewed negative predicate while leaving the primary authority partition unchanged;
9. graph manifest, object inventory, role pins, request index and compiler receipt are complete, deterministic and mutually consistent.

### 4.1 Mandatory negative self-tests

Implementation must include no-execution negative self-tests for at least: missing native binding; missing profile catalog; missing executable policy; unpinned transitive ref; wrong role/hash; route/interface/purpose drift; procedure digest drift; recipe-catalog hash drift; missing/duplicate preparation token; missing/duplicate request stage; stale or mutated sign-critical observation; ENTRY_ONLY without explicit profile; negative entry probe that unexpectedly authorizes; T14 qualification probe matrix missing any active entry class; evidence/probe data mutating primary authority partition; and any attempt by compiler/verifier to access the private signing key.

## 5. Component C — V03 fixture-preparation controller

This component is unavailable until V02 has accepted the exact signed graph and native policy. It runs one case transaction at a time under the project host guard and disposable LAB containment.

Every preparation token resolves through one exact reviewed recipe row. An OBSERVE recipe must prove an existing condition and must not materially mutate it. An ARRANGE recipe must persist a before witness, perform only the bounded action authorized by its recipe family/token, persist an after witness and prove causal effect. Missing token mapping is `PREPARATION_RECIPE_MISSING`; parsing the token name or falling back to current product behavior is forbidden.

Case-state carryover is forbidden unless an exact recipe says otherwise. Destructive/fault cases must return to the reviewed pristine LAB or an explicitly reviewed reconciled state before a later case. If reset/recovery identity cannot be proven, the campaign blocks rather than skipping the case.

The controller emits the existing `lab_case_preparation_action`, `lab_fixture_measurement` and `lab_case_fixture_result` schemas consumed by accepted harness code. Standard route stages continue to invoke the real accepted production request path. The controller cannot mark a parent case PASS; stage/result evidence remains subject to existing accepted harness oracles and finalization.

### 5.1 Evidence augmentation generations

Post-V02 observed evidence may be appended to a new monotonic NativeStore policy generation only when the primary authority partition is byte-identical to the V02-installed partition. Each generated policy records its parent-policy digest and authority-partition digest.

Evidence augmentation may add only observed preparation/measurement/fixture/stage/result evidence roles. It may never alter or replace primary registration, design, code, suite, approvals, execution plans, native bindings, profile catalogs, executable policies or the signed authority envelope. A mismatch is `AUTHORITY_PARTITION_DRIFT` and blocks the campaign.

## 6. Recipe catalog rules

The reviewed companion catalog maps all 78 native preparation tokens to explicit OBSERVE/ARRANGE mode, recipe family, authority case IDs, routes, existing expected-exit sets, oracles and required evidence. Families share safety mechanics only; the token remains the semantic selector.

`OBSERVE_BASELINE` is non-mutating. Evidence/privacy recipes use synthetic canaries and bounded outputs. Restore/isolation and C3/protection recipes use only disposable/non-production LAB resources with pre-existing recovery. Concurrency/journal recipes retain durable fences. Path/collision recipes cannot escape approved LAB surfaces. Resource/network recipes cannot relax firewall, TLS or trust policy.

A handler may serve more than one token only if the reviewed catalog explicitly places those tokens in that family and the handler receives token-specific reviewed parameters. Catch-all handlers, token-name parsing and implementation-derived expectation synthesis are forbidden.

## 7. Fixed lifecycle

The order is fixed:

`compile unsigned staging graph -> static verifier -> independent graph review -> re-observe sign-critical identities -> static verifier -> existing approved local signing transaction -> canonical inbox -> current V02 preflight/intake/artifact-seal/pre-V03 -> V03 preparation/execution`.

Any graph/object mutation after graph review invalidates that review. No TEST-DESIGN output, compiler/verifier self-test, static verifier PASS or TEST_REVIEW PASS may be counted as a native procedure result.

## 8. Implementation and independent review boundary

Expected implementation scope after TEST_REVIEW is validation/test tooling plus its tests. This TEST_CHANGE does not authorize accepted product source changes. If implementation demonstrates that accepted product code or accepted harness schema must change, stop and return to WORKFLOW_REVIEW and the applicable product code/test review path instead of silently widening this record.

Independent TEST_REVIEW must verify:

- `ORACLE_CHANGED=false` and no expected business behavior moved;
- exact source/procedure and coverage identities, including 78 native preparations plus document-only T00-01;
- explicit handling of all ten native ENTRY_ONLY stages and the T14 active-entry qualification matrices;
- primary authority immutability across probe/evidence generations;
- static resolution of native binding/profile/executable/transitive refs;
- compiler/verifier cannot sign, access private-key material, write HKLM or run native actions;
- V03 controller causality/reset/fail-closed rules preserve the reviewed oracles;
- required negative self-tests would detect the previously demonstrated pure-authorize PASS / native-binding-missing false green.
