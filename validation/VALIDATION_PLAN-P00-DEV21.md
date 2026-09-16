# Phase00 Validation Plan — exact dev21

```yaml
PLAN_ID: VALPLAN-P00-DEV21-001
STATUS: APPROVED_PROCEDURE_PENDING_EXTERNAL_LAB_AUTHORITY
SOURCE_COMMIT: 934659f535d81d9a4a07389531acc2b9c304fa6d
PACKAGE_SHA256: f6ee158a318614f8bbef28be7af82549e0a268425da28147a2fa7b14c7b3d3e3
SOURCE_DIGEST: a284645e9eb60661f27eba1ea436d7ff7bbe60d6cd3e312850f1b108d32b1c62
TEST_DIGEST: c645f3d9f88fcb716f78fcff9cd9b4144b320dc4f0c8c7082346a5cfbe6d9383
CONTRACT_DIGEST: f259656c48ed24c15bd48da2bb040950ed94d8edcf1473cf6456b96578c933ee
INVENTORY_SHA256: 2ab5944390d33e1f26476d68c2c742247eaf313fa4f9351650308f5127dbf4a6
CASE_COUNT: 86
CODE_REVIEW_PASS: true
CODE_REVIEW_RECORD: reviews/CODE-REVIEW-P00-001_DEV21_DELTA.md
NATIVE_EXECUTION_STARTED: false
```

## Purpose

Create the actual Phase00 LAB regression evidence required for qualification without circular trust. This plan does not itself authorize execution and does not convert any current `NOT_RUN` case to PASS.

## V02 entry contract — required before any native LAB stage

External authority must establish all of the following for the exact disposable Windows/WSL LAB:

- independently registered host/machine identity and operator SID(s);
- `execution_class=LAB`, registration not withdrawn;
- `controller_external=true`, `disposable=true`, `no_real_credentials=true`, `no_production_mappings=true`;
- fixture/snapshot refs and management-plane recovery/isolation references external to the guest;
- approved LAB test plan for exact reviewed dev21;
- trusted code-review record and exact source/test/contract digests above;
- exact `lab_acceptance_suite` authority: schema 1, approved/not-withdrawn, source_kind LAB, host ID + owner SID, exact build/test/contract digests, unique execution ID, validity window <=24h, and approved cases bound to exact procedure digests/fixture specs/requests.

If any field is missing, ambiguous, stale or mismatched, V02 remains BLOCKED. The development/SITE host is never reclassified as LAB by convenience or a CLI flag.

## Preparation evidence already completed (non-native)

On exact dev21, metadata-only inventory inspection reports:

- 86 unique cases, all `NOT_RUN` and `acceptance_closed=false`;
- all 86 have `AUTHOR_CONTROLLER_IMPLEMENTED` and exact procedure digests/bindings;
- inventory groups: T00=14, F00=16, T05=6, T07=10, T08=14, T09=10, T13=7, T14=9;
- metadata-only `run_native_acceptance_tests.py --list` executed zero parent cases, issued no qualification and reported `host_ready=false`.

## V03 execution sequence (only after V02 PASS)

1. Reverify exact dev21 package SHA and source/build/test/contract identities on the registered LAB.
2. Verify external registration/containment and approved suite authority before each executable stage.
3. Execute the reviewed procedure for every approved mandatory inventory case; negative/destructive fault injection remains LAB-only.
4. Keep fixture expected values separate from actual observations; process exit alone never proves a case.
5. Persist exact execution/suite/case/stage/plan/run identities, journal/raw evidence bindings, controller steps and final results.
6. A case PASS requires actual expected rejection/success plus no unapproved mutation where required; missing permission/environment is BLOCKED, unexpected actual is VALIDATION_FAILURE with root cause initially UNKNOWN.
7. Never remove CREATE/ADOPT/ENGINE/restore coverage to obtain a green receipt.

## V04 qualification rule

E00-13 may be created only from actual reviewed LAB regression records and an independent/MASTER ledger decision. It must bind exact contract/build/profile/fixture/payload/trust/test-list identities, mandatory T00-01…14 and F00-01…16 results plus required supported subcases, finding dispositions, LAB identity/actor, issuance time and withdrawal state. The build cannot self-write qualification PASS.

## V05/V06 boundary

SITE active C1/C2/C3 remains forbidden until exact qualification exists and matches the observed SITE profile/purpose. HOST_READY remains NOT_EVALUATED until applicable SITE lifecycle/restore tests, terminal sweep, evidence/bundle and gate assessment all satisfy the reviewed formula.