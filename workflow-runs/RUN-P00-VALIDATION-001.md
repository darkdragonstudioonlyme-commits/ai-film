# RUN-P00-VALIDATION-001 — Phase00 native validation

```yaml
RUN_ID: RUN-P00-VALIDATION-001
WORKFLOW_ID: WF-P00-VALIDATION-ENTRY
OWNER_LANE: VALIDATION
WORKTREE_REL: NONE
BASE_IDENTITY: 934659f535d81d9a4a07389531acc2b9c304fa6d
STATUS: BLOCKED
CONTINUITY_POLICY: DOCSYS-V2-R8_ACTIVE
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

## Preparation / diagnostic evidence

- Exact validation procedure: `validation/VALIDATION_PLAN-P00-DEV21.md`.
- External authority request: `validation/LAB_REGISTRATION_REQUEST-P00-DEV21.md`.
- Production-like development/runtime preparation remains healthy: 760 tests PASS, 101 static PASS, exact dev21 source clean, monitored runtime integrity PASS.
- Disposable technical LAB candidate: `validation/LAB_CANDIDATE-P00-DEV21.md`, candidate `336b12af-cada-4968-8083-8a5b41e479a2`, status `READY_FOR_EXTERNAL_REGISTRATION`.
- LAB was freshly installed as Ubuntu 24.04.5 WSL2 instead of cloned from development. Default user `aifilmlab` is password-locked; Windows automount and appended Windows PATH are disabled; no development credential/storage mapping was copied into the guest.
- Exact dev21 was controller-streamed into `/opt/ai-film-lab/runtime/dev21`; 283/283 app bytes verify against manifest SHA-256 `2282f89da136ca54838379bdae8d9edc4b8e9c6a66770c732d8b3555eb4276f5`.
- LAB independently reproduced source digest `a284645e...`, test digest `c645f3d9...`, contract digest `f259656c...`, runtime version `0.1.0.dev21`, document preflight with `host_ready=false`, and pre-V03 inventory `86 NOT_RUN` / zero parent cases / no qualification.
- Baseline snapshot SHA-256 `0b91d4947754be40bdb4fd3d07c8eb452dde1b6bc160829923c8e0ef005dfffd` and pristine dev21 snapshot SHA-256 `552d6cf0ec7158ebebc5385f7dfeb7b0b3216f3536d2915877bc9425ad02127d` exist outside the LAB guest.
- The pristine snapshot was imported into temporary distro `AI-FILM-P00-LAB-RP-552d6cf0`; exact app bytes and 86-case `NOT_RUN` inventory passed, then only the probe distro was unregistered. Recovery proof is therefore exercised rather than assumed.
- Windows machine/operator identity is represented publicly only by domain-separated SHA-256 digests in the candidate record; raw identity is not published.
- Exact authority draft summary: `validation/LAB_AUTHORITY_DRAFT-P00-DEV21.md`; local JSON SHA-256 `746a2939d2b8983a952dcedf69ff173cc05f458ac7032a7001aff96c911450b5`; 86 total cases / 85 native fixture templates / 1 document case; self-check PASS; `approved=false`.
- Protected pending authority bundle: `validation/LAB_PENDING_AUTHORITY_BUNDLE-P00-DEV21.md`. Windows store index SHA-256 `fa38540df54df9ebb87929c43e9fe8fbcd09e290e93d8c5d53d7af991df8f615` binds registration candidate `28ec95c3...`, technical facts `bca858e3...`, exact authority draft `746a2939...`, exact build identities and both snapshots. Store ACL inheritance is protected, has two access rules, and contains exactly four files.
- The pending bundle is intentionally `approved=false`, `native_consumable=false`, external approval refs null and is not pinned into Phase00 HKLM trust authority.
- `AI-FILM-P00-LAB` is currently `Stopped` pending authority. Native execution remains zero. No LAB result, qualification, SITE result or HOST_READY claim has been created by preparation.

## Validation steps

| Step | State | Purpose |
|---|---|---|
| V01_CODE_REVIEW_GATE | COMPLETE | exact dev21 CODE_REVIEW_PASS |
| V02_LAB_EXECUTION_AUTHORITY | BLOCKED | external-authority-only: approve protected registration/owner-controller attestation + protected fixture/plan refs + approved <=24h exact-dev21 suite |
| V03_NATIVE_LAB_REGRESSION | NOT_STARTED | execute mandatory reviewed 86-case inventory only after V02 |
| V04_QUALIFICATION_RECEIPT | NOT_STARTED | produce independently ledgered E00-13 from actual mandatory LAB results |
| V05_SITE_VALIDATION | NOT_STARTED | qualified SITE active validation only after V04 |
| V06_GATE_ASSESSMENT | NOT_STARTED | terminal evidence/bundle/assessment; HOST_READY only if exact gate formula is satisfied |

V02 is deliberately resumable. The disposable environment, exact-build deployment, isolation, baseline/pristine snapshots, recovery proof, exact authority draft and protected pending bundle are now complete technical prerequisites. The remaining block is authority, not infrastructure: an external authority must turn the pending candidate into independently approved protected registration/fixture/plan/suite records. Preparation records cannot self-issue that authority.