# Phase00 dev21 — LAB authority draft identity

```yaml
DRAFT_ID: LAB-AUTHORITY-DRAFT-P00-DEV21-001
STATUS: GENERATED_NOT_APPROVED
SOURCE: exact dev21 `aifilm_p00.native.harness_cases.PROCEDURES`
SOURCE_COMMIT: 934659f535d81d9a4a07389531acc2b9c304fa6d
LOCAL_ARTIFACT: /home/dragon/ai-film-dev/artifacts/lab/LAB_AUTHORITY_DRAFT-P00-DEV21.json
DRAFT_SHA256: 746a2939d2b8983a952dcedf69ff173cc05f458ac7032a7001aff96c911450b5
DRAFT_BYTES: 63056
CASE_COUNT: 86
NATIVE_CASE_COUNT: 85
DOCUMENT_CASE_COUNT: 1
SELF_CHECK: PASS
APPROVED: false
NATIVE_EXECUTION_STARTED: false
```

The draft was generated from the reviewed `PROCEDURES` mapping, not hand-copied. For every case it binds the exact `procedure_digest`; for all 85 native cases it carries the exact ordered `preparations` and route list and an exact-schema `lab_case_fixture_spec` template. The one document-only case has `fixture_spec_ref=null` and no native requests, matching the controller invariant.

Every native fixture template targets the reviewed containment assertions (`controller_external`, `disposable`, `no_real_credentials`, `no_production_mappings`) but uses explicit external host/operator placeholders. Every native request contains its exact reviewed route but leaves `interface` and protected `plan_ref` unresolved for the approved external plan. The authority-object template likewise leaves execution ID, issue/expiry timestamps, host/operator binding and protected fixture/plan refs pending.

Self-check re-imported exact dev21 `PROCEDURES` and verified all 86 procedure digests, all 85 fixture preparation lists, route counts/order, containment target fields, and the document-only no-fixture/no-request rule. This record and draft are **preparation only**: external authority must instantiate protected refs and explicitly approve the <=24h suite before it can be pinned or consumed.