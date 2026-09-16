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
BLOCK_REASON_CLASS: EXTERNAL_AUTHORITY_ONLY
INPUT_IDENTITY: {"block_id":"BLOCK-P00-VAL-LAB-AUTH-001","code_review_record":"reviews/CODE-REVIEW-P00-001_DEV21_DELTA.md","contract_digest":"f259656c48ed24c15bd48da2bb040950ed94d8edcf1473cf6456b96578c933ee","inventory_sha256":"2ab5944390d33e1f26476d68c2c742247eaf313fa4f9351650308f5127dbf4a6","package_sha256":"f6ee158a318614f8bbef28be7af82549e0a268425da28147a2fa7b14c7b3d3e3","source_commit":"934659f535d81d9a4a07389531acc2b9c304fa6d"}
IDEMPOTENCY_KEY: b3a1a06122656189f43fb566e19441f6c05127b1f0129bc5fc0eda2f30b6cefe
DONE_WHEN: {"execution_class":"LAB","kind":"LAB_EXECUTION_AUTHORITY_VERIFIED","registration_disposable":true,"source_commit":"934659f535d81d9a4a07389531acc2b9c304fa6d","suite_approved":true}
OUTPUT_IDENTITY: null
REPLAY_POLICY: SAFE_REEXECUTE
```

## Current preparation evidence

- Code review PASS and exact validation procedure remain bound to dev21 source `934659f...`.
- External authority request/handoff and packaging map remain: `validation/LAB_REGISTRATION_REQUEST-P00-DEV21.md`, `validation/LAB_EXTERNAL_APPROVAL_HANDOFF-P00-DEV21.md`, `validation/LAB_APPROVAL_ENVELOPE_MAPPING-P00-DEV21.md`.
- Disposable candidate `336b12af-cada-4968-8083-8a5b41e479a2` remains stopped, isolated, restore-probed and exact-build verified. Its LAB artifact seal is `97051c1e9286e5d65cbc78feef1943ed3e312e45638cd2f256df2ef62000e6ec`.
- Protected pending authority bundle remains `fa38540df54df9ebb87929c43e9fe8fbcd09e290e93d8c5d53d7af991df8f615`, deliberately `approved=false` and non-consumable.
- V02 authority intake remains fail-closed: watcher reports `BLOCKED / APPROVAL_ENVELOPE_MISSING`, `ready_to_advance=false`; READY flag is absent; HKLM trust anchor is absent.
- `validation/WSL_PRODLIKE_RUNTIME-P00-DEV21.md` records immutable exact-dev21 runtime deployment and periodic byte/inventory verification.
- `validation/WSL_PRODLIKE_OPERATIONS-P00-DEV21.md` records seven enabled/active supervised timers: integrity 15m, authority watch 5m, health 10m, control backup 24h, recovery boot+6h, host mirror 2h, and rebuild cold verification boot+12h. All supervised jobs have bounded execution and current last result `success`.
- Current safe control backup contains 39 whitelisted files, is retained for 14 generations, and passes local hash/member verification, NTFS mirror verification, restore probe and secret/protected-domain scan. It excludes native authority and protected identity.
- `validation/WSL_PRODLIKE_HOST_MIRROR-P00-DEV21.md` records the ACL-protected Windows NTFS second-filesystem copy of verified control backups.
- `validation/WSL_PRODLIKE_REBUILD_SET-P00-DEV21.md` records the ACL-protected Windows NTFS exact-runtime rebuild set. The set binds V21 package SHA `f6ee158a...`, wheel SHA `9b565b24...`, app/runtime manifests and rebuild index; its cold probe reverified 283/283 app bytes and reconstructed `0.1.0.dev21` with `86 NOT_RUN` and `host_ready=false` using only the NTFS set as source.
- Production-like controls remain outside native authority: no LAB result, qualification, SITE result or HOST_READY claim has been created.

## Validation steps

| Step | State | Purpose |
|---|---|---|
| V01_CODE_REVIEW_GATE | COMPLETE | exact dev21 CODE_REVIEW_PASS |
| V02_LAB_EXECUTION_AUTHORITY | BLOCKED | external-authority-only: protected registration/attestation + fixture/plan refs + approved <=24h exact-dev21 suite |
| V03_NATIVE_LAB_REGRESSION | NOT_STARTED | mandatory reviewed 86-case inventory only after V02 |
| V04_QUALIFICATION_RECEIPT | NOT_STARTED | qualification from actual mandatory LAB results |
| V05_SITE_VALIDATION | NOT_STARTED | qualified SITE active validation only after V04 |
| V06_GATE_ASSESSMENT | NOT_STARTED | terminal gate assessment; HOST_READY only from exact evidence formula |

V02 is deliberately resumable. Technical LAB preparation and non-native production-like runtime/operations/recovery/rebuild readiness are complete. The remaining block is external authority only; none of the monitoring, backup, mirror or rebuild controls can self-issue or install that authority.