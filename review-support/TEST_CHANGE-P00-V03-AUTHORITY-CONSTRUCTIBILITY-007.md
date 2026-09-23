# TEST_CHANGE — V03 stage-authority constructibility witness 007

~~~yaml
TEST_CHANGE_ID: TEST_CHANGE-P00-V03-AUTHORITY-CONSTRUCTIBILITY-007
RUN_ID: RUN-P00-VALIDATION-002
WORK_ITEM: TEST-DESIGN-P00-V03-AUTHORITY-CONSTRUCTIBILITY-007
TARGET_BASE_SOURCE_COMMIT: 86bb64938a136e3f8d6cfd0266685a01cb832b77
PREDECESSOR_TEST_CHANGE: TEST_CHANGE-P00-V03-AUTHORITY-BINDING-PRODUCER-006
PREDECESSOR_TEST_REVIEW: lane/validation-p00:test-governance/TEST_REVIEW-P00-V03-AUTHORITY-BINDING-PRODUCER-006.md
DESIGN_RECORD: docs/PHASE00_STAGE_AUTHORITY_FEASIBILITY_CORRECTION_V2.md
DESIGN_AUTHOR_COMMIT: c16745e994396f2c05e4408dbb909d0c94389e82
DESIGN_REVIEW: reviews/DESIGN-REVIEW-P00-V03-AUTHORITY-FEASIBILITY-003.md
DESIGN_REVIEW_COMMIT: 99730637759c8f2369fda01c8af676bbbf0f22b4
DEPENDENCY_CATALOG_SHA256: fac26f07965257a75eee93c61f9861bf2a0e24f033008bd366cf5478849f54a0
ORACLE_CHANGED: false
EXPECTED_BUSINESS_BEHAVIOR_CHANGED: false
PRODUCT_SOURCE_SCOPE_CHANGED: false
NATIVE_EXECUTION_AUTHORIZED: false
AUTHORITY_SIGNING_AUTHORIZED: false
STATUS: PENDING_NON_AUTHOR_TEST_REVIEW
~~~

## Purpose

TEST_CHANGE 006 remains valid history and owns the original four-mode temporal-authority coverage. The V3 constructibility review did not change expected Phase00 behavior or its source allowlist; it made previously implicit construction/publication/recovery obligations executable. This successor adds tests for those obligations before dev23 authoring resumes.

## Unchanged implementation and test allowlist

Product source remains exactly: ADD `src/aifilm_p00/native/stage_authority.py`; MODIFY `src/aifilm_p00/native/harness_controller.py`. Product tests remain ADD `tests/test_dev23_stage_authority.py`; MODIFY `tests/test_dev15_harness.py`.

`src/aifilm_p00/authority.py`, `src/aifilm_p00/plans.py`, `src/aifilm_p00/native/harness_cases.py`, `src/aifilm_p00/native/request_entry.py`, `src/aifilm_p00/resume.py`, `src/aifilm_p00/recovery.py`, `config/required-native-test-inventory.json` and the four normative Phase00 contracts remain byte-identical.

Validation tooling/test allowlists remain those in TEST_CHANGE 006. No extra production file is authorized by this change.

## Required constructibility coverage

- `TD007-01` — construct descriptor/templates/slots/suite/detached base manifest in acyclic order; reject root/partition self-reference and placeholder/fixed-point hashes.
- `TD007-02` — prove the detached base manifest canonical sort/digest is invariant and that runtime generation/lineage refs are excluded from the signed base set.
- `TD007-03` — external restore selects exactly one signed destination-locator allowlist entry and rejects arbitrary host/volume/path, glob/prefix substitution and bytes above slot max.
- `TD007-04` — offline copy receipt must bind source export evidence + source locator/hash/bytes to destination locator/hash/bytes; reject same-path-as-cross-host-proof and hash/byte drift.
- `TD007-05` — all nine late-proof roles use the exact reviewed scope keys and timing/source rules; reject missing/extra/wrong subject fields, early materialization and disallowed owner assertion.
- `TD007-06` — publisher acquires the existing global guard, validates exact parent policy/generation, builds/validates full next NativeStore, writes/readbacks under that guard, persists publication event, then releases before `prepare_execution`; nested-guard execution is rejected.
- `TD007-07` — generation publication preserves the existing NativeStore outer schema and every immutable base ref; only slot/proof-authorized content-addressed additions are permitted.
- `TD007-08` — publication key `(new_policy_digest,suite_ref,case_id,stage_index,slot_ref)` is idempotent: exact event reuse succeeds; same-key/different-body, duplicate lineage, parent drift, rollback and generation skip fail closed.
- `TD007-09` — interruption matrix covers before-write, ambiguous write/readback, after-readback, after-event, post-release/pre-execution, pre-INTENT, post-INTENT and terminal-clear failure without replaying unknown mutations.
- `TD007-10` — fresh post-publication resolve and existing request/session admission reject withdrawn/drifted derived plan/approval/lineage before native INTENT; revocation cannot leave an orphan usable derived ref.
- `TD007-11` — `request_entry.py`, `trust.py`, SessionRunner/ProofReader semantics are consumed without widening product source scope; source-scope byte-identical checks fail on unauthorized changes.
- `TD007-12` — recompute the normative 133-stage 94/15/10/14 partition and all previous TD006 requirements; this successor cannot hide or replace predecessor coverage.

## Oracle and evidence discipline

All TD007 assertions derive from the reviewed V3 design plus accepted dev22 source behavior; implementation code remains the subject under test. Pure/unit tests may prove construction/state transitions but cannot be labeled native execution. Interruption tests use deterministic test doubles/fault injection around publication boundaries and must demonstrate the protection would fail if serialization/idempotency checks were removed.

Any implementation need to alter a byte-identical-required file, source/test allowlist, procedure outcome, route, oracle or required evidence reopens DESIGN/TEST_REVIEW rather than changing this test expectation.

## Exit gate

Independent TEST_REVIEW must verify `ORACLE_CHANGED=false`, exact allowlist preservation and the 12 new obligations. Only that PASS re-authorizes dev23 implementation. This change does not sign authority, mutate HKLM, run LAB/native cases, issue qualification or set HOST_READY.
