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

## Preparation / diagnostic evidence

- Exact validation procedure: `validation/VALIDATION_PLAN-P00-DEV21.md`.
- External authority request: `validation/LAB_REGISTRATION_REQUEST-P00-DEV21.md`.
- Final external approval handoff: `validation/LAB_EXTERNAL_APPROVAL_HANDOFF-P00-DEV21.md`.
- Exact envelope/object/role-pin packaging map: `validation/LAB_APPROVAL_ENVELOPE_MAPPING-P00-DEV21.md`; this is packaging guidance only and does not constitute approval.
- Production-like runtime/operations evidence: `validation/WSL_PRODLIKE_RUNTIME-P00-DEV21.md` and `validation/WSL_PRODLIKE_OPERATIONS-P00-DEV21.md`. Exact dev21 app bytes remain immutable/read-only; integrity, health, backup and recovery verification are monitored by user-systemd without granting native authority.
- Production-like operations now include five enabled/active timers: integrity every 15 minutes, V02 authority watch every 5 minutes, health every 10 minutes, control backup every 24 hours, and recovery verification after boot/every 6 hours. Latest health PASS includes verified-fresh backup plus last backup/recovery job `Result=success`.
- Latest sampled control backup contains 25 whitelisted control files only, uses mode `0600`, is retained under a 14-archive policy, and passed archive hash/member verification, restore probe and secret/protected-domain scan. Backup verifier rejects stale age >30 hours. No native authority or protected identity is included.
- Disposable technical LAB candidate: `validation/LAB_CANDIDATE-P00-DEV21.md`, candidate `336b12af-cada-4968-8083-8a5b41e479a2`, status `READY_FOR_EXTERNAL_REGISTRATION`.
- LAB was freshly installed as Ubuntu 24.04.5 WSL2 instead of cloned from development. Default user `aifilmlab` is password-locked; Windows automount and appended Windows PATH are disabled; no development credential/storage mapping was copied into the guest.
- Exact dev21 was controller-streamed into `/opt/ai-film-lab/runtime/dev21`; 283/283 app bytes verify against manifest SHA-256 `2282f89da136ca54838379bdae8d9edc4b8e9c6a66770c732d8b3555eb4276f5`.
- LAB independently reproduced source digest `a284645e...`, test digest `c645f3d9...`, contract digest `f259656c...`, runtime version `0.1.0.dev21`, document preflight with `host_ready=false`, and pre-V03 inventory `86 NOT_RUN` / zero parent cases / no qualification.
- Baseline snapshot SHA-256 `0b91d4947754be40bdb4fd3d07c8eb452dde1b6bc160829923c8e0ef005dfffd` and pristine dev21 snapshot SHA-256 `552d6cf0ec7158ebebc5385f7dfeb7b0b3216f3536d2915877bc9425ad02127d` exist outside the LAB guest.
- The pristine snapshot was imported into temporary distro `AI-FILM-P00-LAB-RP-552d6cf0`; exact app bytes and 86-case `NOT_RUN` inventory passed, then only the probe distro was unregistered. Recovery proof is therefore exercised rather than assumed.
- LAB artifact seal: `validation/LAB_ARTIFACT_SEAL-P00-DEV21.md`. Six recovery/deployment/authority artifacts are mode `0400`, seal SHA-256 `97051c1e9286e5d65cbc78feef1943ed3e312e45638cd2f256df2ef62000e6ec`; streaming verifier SHA-256 `769ec4e3c8c85cd78105c1466d8c854cc87cf362d5c01e80fe4a9d285e09afc8` recomputed sizes/hashes/write bits and PASSed.
- Windows machine/operator identity is represented publicly only by domain-separated SHA-256 digests in the candidate record; raw identity is not published.
- Exact authority draft summary: `validation/LAB_AUTHORITY_DRAFT-P00-DEV21.md`; local JSON SHA-256 `746a2939d2b8983a952dcedf69ff173cc05f458ac7032a7001aff96c911450b5`; 86 total cases / 85 native fixture templates / 1 document case; self-check PASS; `approved=false`.
- Protected pending authority bundle: `validation/LAB_PENDING_AUTHORITY_BUNDLE-P00-DEV21.md`. Windows store index SHA-256 `fa38540df54df9ebb87929c43e9fe8fbcd09e290e93d8c5d53d7af991df8f615` binds registration candidate `28ec95c3...`, technical facts `bca858e3...`, exact authority draft `746a2939...`, exact build identities and both snapshots. Store ACL inheritance is protected, has two access rules, and contains exactly four files.
- The pending bundle is intentionally `approved=false`, `native_consumable=false`, external approval refs null and is not pinned into Phase00 HKLM trust authority.
- Fail-closed authority intake: `validation/V02_AUTHORITY_INTAKE-P00-DEV21.md`. Hardened validator SHA-256 `05143de5f2ba7b6e58c3e9256cfc0c724f7f38aea3d945368506e3cf1180bc89` checks exact candidate/content bindings, protected registration/attestations/recovery, all 86 suite rows, all 85 fixture specs, hash-addressed plans/role pins, single-pin `registration/design/code`, actual pin membership for every execution plan/fixture spec, and pure `authority.authorize()` for every approved plan.
- Windows approval inbox is ACL-protected with exactly current operator + SYSTEM, has empty `objects/`, and deliberately has no `approval-envelope.json`. Current validator result is `BLOCKED / APPROVAL_ENVELOPE_MISSING / exit 12`; `ready_to_advance=false`.
- Negative checks confirm the template-as-approval path is rejected with `EXTERNAL_DECISION_NOT_APPROVE`, and a flags-only fake APPROVE with missing immutable refs is rejected with `ENVELOPE_REF_MISSING`; both exit 12 and produce no `READY_TO_ADVANCE`.
- Stale-signal protection was also tested: a deliberately planted `READY_TO_ADVANCE.flag` was removed by the current BLOCKED watcher. Current watcher SHA-256 is `acb117e22af0a574a0912c3545b75d6d1d3ff6bbf6223408b693f48a863c05e1`.
- Native-policy staging: `validation/V02_NATIVE_POLICY_STAGING-P00-DEV21.md`. Materializer SHA-256 `52083c05fc4fbeab15897a0ae4268f9963a13365909d37c1eca39da00d5c3b74` first requires intake READY, then would build and instantiate an exact dev21 `NativeStore` candidate. Current run is `BLOCKED / AUTHORITY_INTAKE_NOT_READY`; no policy file exists and `hklm_written=false`.
- Pre-V03 staging gate: `validation/V02_PRE_V03_GATE-P00-DEV21.md`. `pre-v03-authority-stage.sh` SHA-256 `f772cd994e73cc7da3e82ded3a7e9a97e4f9f823c33c91668c7a13404e8c25e5` currently exits 12 at the authority step and creates no policy candidate. Trust-anchor installer SHA-256 `34fa9e84a63f54c9164873db99d85aa914b662237714bd945744046e52f96f3c` defaults to dry-run; explicit `-Commit` additionally requires exact policy hash/scope and Windows admin elevation. A nonexistent-policy negative test returned `POLICY_NOT_FOUND` before registry action.
- Read-only Windows checks after all staging confirm `TrustAnchorExists=false` and `ApprovalEnvelopeExists=false`.
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

V02 is deliberately resumable. The disposable environment, exact-build deployment, isolation, restore-probed and sealed snapshots, exact authority draft, protected pending bundle, stale-safe fail-closed authority intake, non-installing native-policy staging and pre-V03 gate are complete technical prerequisites. The remaining block is external authority only. Production-like monitoring/backup/recovery controls cannot self-issue or install that authority.