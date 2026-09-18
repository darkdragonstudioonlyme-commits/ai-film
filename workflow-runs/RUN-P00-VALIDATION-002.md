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
BLOCK_REASON_CLASS: LOCAL_KEY_ACTIVATION_REVIEW_AND_DEV22_LAB_PREPARATION
INPUT_IDENTITY: {"authority_model":"LOCAL_OPERATOR_SAME_WSL_TRUST_DOMAIN","candidate_binding_sha256":"4aaf09ec2ef8618a5680e147cd2eeac695f940d45ae5cb0446c7b7e5c2483384","candidate_id":"6f895394-e0b4-5434-bebc-79ee4e576282","code_review_record":"reviews/CODE-REVIEW-P00-001_DEV22_LOCAL_AUTHORITY.md","contract_digest":"f259656c48ed24c15bd48da2bb040950ed94d8edcf1473cf6456b96578c933ee","inventory_sha256":"2ab5944390d33e1f26476d68c2c742247eaf313fa4f9351650308f5127dbf4a6","package_sha256":"c2ea52087039f4c7b98c53a7cc0eaf1a4a0f931645f86491bf2eb8ef12956aae","source_commit":"86bb64938a136e3f8d6cfd0266685a01cb832b77"}
IDEMPOTENCY_KEY: 048c70614f2779a0ec675aebdc2565dab0c19bb56eb57447717fe884c15f49e5
DONE_WHEN: {"authority_model":"LOCAL_OPERATOR_SAME_WSL_TRUST_DOMAIN","candidate_id":"6f895394-e0b4-5434-bebc-79ee4e576282","controller_external":false,"execution_class":"LAB","kind":"LAB_LOCAL_OPERATOR_AUTHORITY_VERIFIED","local_authority_signature_verified":true,"registration_disposable":true,"source_commit":"86bb64938a136e3f8d6cfd0266685a01cb832b77","suite_approved":true}
OUTPUT_IDENTITY: null
REPLAY_POLICY: SAFE_REEXECUTE
```

## Current preparation evidence

- V01 code-review gate is COMPLETE for exact dev22 source `86bb64938a136e3f8d6cfd0266685a01cb832b77`, package `c2ea52087039f4c7b98c53a7cc0eaf1a4a0f931645f86491bf2eb8ef12956aae`, independent 766 PASS / 101 static PASS, corrected TEST_REVIEW and CODE_REVIEW PASS.
- Authority model is owner-selected `LOCAL_OPERATOR_SAME_WSL_TRUST_DOMAIN`. `controller_external=false` is required by the local V02 intake and product/harness accepts it without relaxing disposable/no-real-credential/no-production-mapping containment.
- Candidate ID is `6f895394-e0b4-5434-bebc-79ee4e576282` and candidate-binding SHA is `4aaf09ec2ef8618a5680e147cd2eeac695f940d45ae5cb0446c7b7e5c2483384`. Dev21 candidate IDs/bundles/snapshots/approval objects are historical and rejected for this run.
- V02 tooling has hard-cut local schema source under `validation/tooling/`: old external envelope kind is rejected; local Ed25519 signature verifies exact envelope bytes; role pins/content hashes/current-evaluation invalidation remain fail-closed.
- The audited tooling transaction authorized a separate local-key activation. A WSL-local Ed25519 key now exists outside Git with owner-only mode 0600; the activation design commits only its public identity and remains pending independent review/audit/deployment.
- Current prodlike runtime and stopped LAB still contain dev21 product bytes. They must be rebuilt/rebound to exact dev22 before V02 can close or V03 can start.
- All 86 native procedures remain NOT_RUN. No qualification, SITE activation or HOST_READY assessment exists.

## Validation steps

| Step | State | Purpose |
|---|---|---|
| V01_CODE_REVIEW_GATE | COMPLETE | exact dev22 CODE_REVIEW_PASS |
| V02_LOCAL_OPERATOR_LAB_AUTHORITY | BLOCKED | reviewed same-WSL local key + signed exact dev22 authority graph + sealed stopped dev22 LAB |
| V03_NATIVE_LAB_REGRESSION | NOT_STARTED | reviewed 86-case native LAB inventory only after V02 |
| V04_QUALIFICATION_RECEIPT | NOT_STARTED | qualification from actual LAB results |
| V05_SITE_VALIDATION | NOT_STARTED | qualified SITE active validation only after V04 |
| V06_GATE_ASSESSMENT | NOT_STARTED | terminal evidence-based HOST_READY assessment |

Local cryptographic approval is intentionally lower assurance than external authority. It proves possession of the reviewed WSL-local key and integrity of the signed graph, not independent provenance. No native stage may start while V02 remains BLOCKED.
