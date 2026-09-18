# Phase00 dev22 — V02 LAB technical rebuild deployment

DEPLOYMENT_ID: V02-LAB-DEV22-REBUILD-DEPLOYMENT-P00-001
RUN_ID: RUN-P00-VALIDATION-002
STEP_ID: V02_LOCAL_OPERATOR_LAB_AUTHORITY
SOURCE_CANONICAL_VALIDATION_HEAD: 2baac962f8736df5b4347dcc16113147e2659e44
SOURCE_DESIGN_COMMIT: 65988f3234c5bd58d9c5cbb91e9466bd56f6d47e
SOURCE_REVIEW_COMMIT: 352610bef07d24b420dcbbda7336f6007a79e9de
SOURCE_AUDIT_COMMIT: 2baac962f8736df5b4347dcc16113147e2659e44
SOURCE_PROMOTED_CI_RUN: 35347581968
STATUS: PASS_ON_AUDIT_PROMOTION
LOCAL_EVIDENCE_DIR: /home/dragon/ai-film-dev/run-evidence/validation/lab-dev22-deployment/20260918T130228Z
DEPLOYMENT_RECEIPT: validation/V02_LAB_DEV22_REBUILD_DEPLOYMENT_RECEIPT-P00.json
DEPLOYMENT_RECEIPT_SHA256: df3652621d71d13efebcab50fcb8743b4c203b08c0e28f27a5360f00a6321f97
APP_TAR_SHA256: 4205d83634bae063786cac198d7b066deef94156d403755b5bf65cfa640d644a
APP_MANIFEST_SHA256: 8f31bb6359387257f00388e12f05e2cb6014867ebb90295d1684d3b6fab00471
PRE_V03_INVENTORY_SHA256: 7ef70d5cb5134b3328dee96747a7a7d4b26c5b8e7f2dcaffa39aa96e0556851a
PRE_MIGRATION_EXPORT_SHA256: 0b5b181898636398c3764a95c884ebfb0180cd5b83348e92be1c1f12241de4af
PRISTINE_RAW_SHA256: e1d0af02c41318c628faa21aba545435a9516b59f319ad2ebb13e35433a8d0e1
PRISTINE_SEALED_SHA256: 08cff85babf4e8733bffbd56423ebaee3f7f85c67944d86a32172f39d53541b6
TECHNICAL_FACTS_SHA256: 9ae252272f2a1090afa708b877570891661cb393f21b59626fe2526c8bd5d64a
ARTIFACT_SEAL_SHA256: 326718e74673d390750f691e9b319df344de58a2d8e8f296384caf716e2ce461
RESTORE_PROBE: PASS
LAB_STATE: STOPPED
V02_STATUS: BLOCKED
V02_REASON: APPROVAL_ENVELOPE_MISSING
NATIVE_EXECUTION_STARTED: false
AUTHORITY_ENVELOPE_CREATED: false
REVIEW_RECORD: reviews/VALIDATION-V02-LAB-DEV22-DEPLOYMENT-REVIEW-001_PASS.md
AUDIT_RECORD: reviews/VALIDATION-V02-LAB-DEV22-DEPLOYMENT-AUDIT-001_PASS.md

## Deployment result

Exact dev22 was installed side-by-side under `/opt/ai-film-lab/runtime/dev22` from the audited deterministic payload. The existing dev21 runtime was retained as rollback evidence. The guest created its own venv and source binding; no host venv or network dependency installation was used.

Metadata-only verification under locked user `aifilmlab` returned version `0.1.0.dev22`, workspace preflight `host_ready=false`, and exact 86-case native inventory with `NOT_RUN`, zero parent cases, no qualification and no HOST_READY. No native route/test runner executed.

A fresh stopped pre-migration WSL export was captured before mutation. After preparation the LAB was terminated, pristine dev22 was exported, imported under an isolated temporary probe, exact app bytes/modes/venv binding/isolation/inventory were reverified, the probe was stopped and unregistered, and the original LAB remained Stopped.

Host technical facts and `LAB_ARTIFACT_SEAL_V1.json` were replaced only after restore-probe PASS; original dev21 facts/seal bytes were copied to immutable historical filenames. Canonical seal verifier passes 8 immutable candidate-bound artifacts at seal SHA `326718e7...`.

Key parity remains PASS for durable key `AI-FILM-P00-DEV22-LOCAL-001`; prodlike remains exact dev22 READY for non-native operations. V02 deliberately remains BLOCKED on `APPROVAL_ENVELOPE_MISSING`. This transaction creates no approval envelope, signature, READY flag, native policy, native result, qualification, SITE activation or HOST_READY assessment.

## Boundary

The LAB technical substrate is now ready for the next separate reviewed authority-object transaction. This deployment itself does not close V02 or authorize V03.
