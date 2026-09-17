# RUN-P00-VALIDATION-001 — Phase00 native validation

```yaml
RUN_ID: RUN-P00-VALIDATION-001
WORKFLOW_ID: WF-P00-VALIDATION-ENTRY
OWNER_LANE: VALIDATION
WORKTREE_REL: NONE
BASE_IDENTITY: 934659f535d81d9a4a07389531acc2b9c304fa6d
STATUS: BLOCKED
CONTINUITY_POLICY: DOCSYS-V2-R9_ACTIVE
CURRENT_STEP: V02_LAB_EXECUTION_AUTHORITY
RETURN_TO: V02_LAB_EXECUTION_AUTHORITY
```

## Current step contract

```yaml
STEP_ID: V02_LAB_EXECUTION_AUTHORITY
STATE: BLOCKED
BLOCK_REASON_CLASS: EXTERNAL_AUTHENTICITY_AND_AUTHORITY
INPUT_IDENTITY: {"block_id":"BLOCK-P00-VAL-LAB-AUTH-001","code_review_record":"reviews/CODE-REVIEW-P00-001_DEV21_DELTA.md","contract_digest":"f259656c48ed24c15bd48da2bb040950ed94d8edcf1473cf6456b96578c933ee","inventory_sha256":"2ab5944390d33e1f26476d68c2c742247eaf313fa4f9351650308f5127dbf4a6","package_sha256":"f6ee158a318614f8bbef28be7af82549e0a268425da28147a2fa7b14c7b3d3e3","source_commit":"934659f535d81d9a4a07389531acc2b9c304fa6d"}
IDEMPOTENCY_KEY: b3a1a06122656189f43fb566e19441f6c05127b1f0129bc5fc0eda2f30b6cefe
DONE_WHEN: {"execution_class":"LAB","external_authority_key_provenance_verified":true,"external_authority_signature_verified":true,"kind":"LAB_EXECUTION_AUTHORITY_VERIFIED","registration_disposable":true,"source_commit":"934659f535d81d9a4a07389531acc2b9c304fa6d","suite_approved":true}
OUTPUT_IDENTITY: null
REPLAY_POLICY: SAFE_REEXECUTE
```

## Current preparation evidence

- Exact dev21 identities remain unchanged and all 86 native cases remain `NOT_RUN`.
- V02 remains BLOCKED and `AI-FILM-P00-LAB` remains stopped. The real inbox still has no approval envelope, and forensic review additionally found that the operator-writable approved inbox cannot by itself prove external provenance; finding `V02-AUTHENTICITY-001` requires external-key/signature hardening before any future APPROVE package can close V02.
- `validation/PRODLIKE_EXECUTION_SLA_RETENTION-P00-DEV21.md` records N1–N6 execution-SLA, retention and rotating-state work.
- Runtime health now checks monotonic last-completion freshness for all eleven services in addition to timer enabled/active state and previous job result. Production-function negative tests reject both stale completion and never-completed-after-boot-grace states.
- Real producer retention overflow tests prove control backup retention=14 and evidence-ledger retention=30; pruned ledger history preserves predecessor continuity through the chain anchor.
- Kernel cgroup probe verified systemd resource values are materialized to `memory.max` and `pids.max`; live AI-FILM services remain bounded at `MemoryMax=256M`, `TasksMax=128`.
- Current producer-first recovery refresh passes. At the latest observation, backup/mirror sample contained 87 files at SHA `c213efff4aeff5585bf14efea172889dffe3b33af815dabaf30f3b5e14c887d2`; deterministic transfer-export sample SHA was `023eb0d5275eeb1b27974c908664f17b46a4bbe11a12376d4e085602a7135d11`.
- Those backup/export identities are rotating operational samples because bounded ledger history advances. They are not exact candidate/release identities. Stable invariants remain exact dev21 identity, verifier PASS, freshness/retention limits, 11 timer/resource definitions, chain validity and producer-before-consumer migration.
- Full DR currently restores the sampled control state plus 11 timer definitions and 11 resource drop-ins before exact-dev21 reconstruction; fail-closed campaign remains 8/8 PASS.
- Private Drive metadata anchors only stable exact-candidate/rebuild identities; binary off-host payload remains absent and `OFF_HOST_DR_CLAIMED=false`.

## Validation steps

| Step | State | Purpose |
|---|---|---|
| V01_CODE_REVIEW_GATE | COMPLETE | exact dev21 CODE_REVIEW_PASS |
| V02_LAB_EXECUTION_AUTHORITY | BLOCKED | independently authenticated external LAB authority: external key provenance + signed exact envelope + protected object graph |
| V03_NATIVE_LAB_REGRESSION | NOT_STARTED | reviewed 86-case native LAB inventory only after V02 |
| V04_QUALIFICATION_RECEIPT | NOT_STARTED | qualification from actual LAB results |
| V05_SITE_VALIDATION | NOT_STARTED | qualified SITE active validation only after V04 |
| V06_GATE_ASSESSMENT | NOT_STARTED | terminal evidence-based HOST_READY assessment |

The same run remains resumable at V02. No SLA, retention, recovery or rotating-state control can satisfy V02 `DONE_WHEN` or self-issue protected authority.