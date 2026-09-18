# RUN-P00-VALIDATION-002 — Phase00 dev22 native validation

```yaml
RUN_ID: RUN-P00-VALIDATION-002
WORKFLOW_ID: WF-P00-VALIDATION-ENTRY
OWNER_LANE: VALIDATION
WORKTREE_REL: NONE
BASE_IDENTITY: 86bb64938a136e3f8d6cfd0266685a01cb832b77
STATUS: BLOCKED
CONTINUITY_POLICY: DOCSYS-V2-R9_ACTIVE
CURRENT_STEP: V02_LOCAL_OPERATOR_LAB_AUTHORITY
RETURN_TO: V02_LOCAL_OPERATOR_LAB_AUTHORITY
```

## Current step contract

```yaml
STEP_ID: V02_LOCAL_OPERATOR_LAB_AUTHORITY
STATE: BLOCKED
BLOCK_REASON_CLASS: LOCAL_AUTHORITY_PACKAGE_MISSING
INPUT_IDENTITY: {"authority_model":"LOCAL_OPERATOR_SAME_WSL_TRUST_DOMAIN","candidate_binding_sha256":"4aaf09ec2ef8618a5680e147cd2eeac695f940d45ae5cb0446c7b7e5c2483384","candidate_id":"6f895394-e0b4-5434-bebc-79ee4e576282","code_review_record":"reviews/CODE-REVIEW-P00-001_DEV22_LOCAL_AUTHORITY.md","contract_digest":"f259656c48ed24c15bd48da2bb040950ed94d8edcf1473cf6456b96578c933ee","inventory_sha256":"2ab5944390d33e1f26476d68c2c742247eaf313fa4f9351650308f5127dbf4a6","package_sha256":"c2ea52087039f4c7b98c53a7cc0eaf1a4a0f931645f86491bf2eb8ef12956aae","source_commit":"86bb64938a136e3f8d6cfd0266685a01cb832b77"}
IDEMPOTENCY_KEY: 048c70614f2779a0ec675aebdc2565dab0c19bb56eb57447717fe884c15f49e5
DONE_WHEN: {"authority_model":"LOCAL_OPERATOR_SAME_WSL_TRUST_DOMAIN","candidate_id":"6f895394-e0b4-5434-bebc-79ee4e576282","controller_external":false,"execution_class":"LAB","kind":"LAB_LOCAL_OPERATOR_AUTHORITY_VERIFIED","local_authority_signature_verified":true,"registration_disposable":true,"source_commit":"86bb64938a136e3f8d6cfd0266685a01cb832b77","suite_approved":true}
OUTPUT_IDENTITY: null
REPLAY_POLICY: SAFE_REEXECUTE
```

## Current preparation evidence

- V01 code-review gate is COMPLETE for exact dev22 source `86bb64938a136e3f8d6cfd0266685a01cb832b77`, package `c2ea5208...`, independent 766 PASS / 101 static PASS, corrected TEST_REVIEW and CODE_REVIEW PASS.
- Authority model is owner-selected `LOCAL_OPERATOR_SAME_WSL_TRUST_DOMAIN`. `controller_external=false` is required by the local V02 intake and product/harness accepts it without relaxing disposable/no-real-credential/no-production-mapping containment.
- Candidate ID is `6f895394-e0b4-5434-bebc-79ee4e576282` and candidate-binding SHA is `4aaf09ec...`. Dev21 candidate IDs/bundles/snapshots/approval objects are historical and rejected for this run.
- V02 tooling has hard-cut local schema source under `validation/tooling/`: old external envelope kind is rejected; local Ed25519 signature verifies exact envelope bytes; role pins/content hashes/current-evaluation invalidation remain fail-closed.
- The prior local-key activation design `8760fd8...`, review `804df8a...`, audit/promoted head `9673283...`, promotion-finalization records and CI `35315862290` remain historical evidence, but V02-LOCAL-KEY-PARITY-001 supersedes that key identity because no durable private key derives public SHA `5d595732...`; it cannot sign the current envelope and is not silently regenerated/substituted.
- Prodlike dev22 migration design/review/audit is canonical. The live deployment is receipt-bound at `validation/PRODLIKE_DEV22_MIGRATION_DEPLOYMENT-P00.md`: `current -> dev22`, runtime manifest `ef19d1bb...`, 64/64 control bytes, 46 user-systemd files, 11 enabled/active timers, fresh backup parity and runtime-health PASS. Deployment receipt SHA is `dcd7bb01...`.
- Corrected reactivation design/review/audit is promoted at `665d349...` with canonical CI `35319634603` SUCCESS. Exact 20-file audited tooling/trust bytes were then deployed to `validation-ops`: manifest parity 20/20, durable-key live parity PASS, full deployed regressions PASS, local identity context unchanged, watcher success, preflight/intake/pre-V03 remain `10/12/12`, READY/native-policy absent and LAB stopped. Deployment evidence is review/audit-gated by `V02_LOCAL_KEY_REACTIVATION_DEPLOYMENT-P00-DEV22.md` before canonical claim.
- Current prodlike runtime/control plane is exact dev22 and READY for non-native operations. The stopped LAB is also exact dev22, candidate-bound and artifact-sealed; pristine export restore-probe PASS, 86 procedures remain NOT_RUN. V02 still requires a fresh signed local-authority object graph before it can close or V03 can start.
- LAB technical rebuild deployment is receipt-bound at `validation/V02_LAB_DEV22_REBUILD_DEPLOYMENT-P00.md`: app tar `4205d836...`, inventory `7ef70d5c...`, pristine raw `e1d0af02...`, sealed pristine `08cff85b...`, facts `9ae25227...`, seal `326718e7...`, restore probe PASS, LAB Stopped and native=false.
- All 86 native procedures remain NOT_RUN. No qualification, SITE activation or HOST_READY assessment exists.

## Validation steps

| Step | State | Purpose |
|---|---|---|
| V01_CODE_REVIEW_GATE | COMPLETE | exact dev22 CODE_REVIEW_PASS |
| V02_LOCAL_OPERATOR_LAB_AUTHORITY | BLOCKED | build/sign and verify the exact current local-authority object graph from sealed dev22 LAB evidence |
| V03_NATIVE_LAB_REGRESSION | NOT_STARTED | reviewed 86-case native LAB inventory only after V02 |
| V04_QUALIFICATION_RECEIPT | NOT_STARTED | qualification from actual LAB results |
| V05_SITE_VALIDATION | NOT_STARTED | qualified SITE active validation only after V04 |
| V06_GATE_ASSESSMENT | NOT_STARTED | terminal evidence-based HOST_READY assessment |

Local cryptographic approval is intentionally lower assurance than external authority. It proves possession of the reviewed WSL-local key and integrity of the signed graph, not independent provenance. No native stage may start while V02 remains BLOCKED.
