# Phase00 dev21 — V02 external-authenticity deployment evidence

```yaml
DEPLOYMENT_ID: V02-EXTERNAL-AUTHENTICITY-DEPLOYMENT-P00-DEV21-001
RUN_ID: RUN-P00-VALIDATION-001
STEP_ID: V02_LAB_EXECUTION_AUTHORITY
REVIEWED_TARGET_COMMIT: 74a7cac77de1c8649f538ad808467fffe6a40a7f
REVIEWED_TARGET_TREE: fee473d56fcdadaa89768af2599e775e55b4f0de
REVIEW_COMMIT: bd5385b94f0dad6ff75c9618bb5e880e0c26895b
AUDIT_COMMIT: c579217eb3e5287b8554e35e6104ea8ed29e6f83
DEPLOYMENT_STATUS: PASS_BLOCKED_PENDING_EXTERNAL_KEY
TOOLING_MANIFEST_SHA256: ce816d32a234a5d1c25e3cc5cfc393b609f41094d410d1402a8306cd8cb65805
VALIDATOR_SHA256: 0ff65ddb2d5e01bc04f4857dde46d321c0610826e108fdc3583100a8b2c3b0b9
AUTHENTICITY_MODULE_SHA256: f89d9688ca39795a0c4fcf9b5a33b9c257f2d9dee8e17cfeb24b6df7de56cbcc
LOCAL_IDENTITY_LOADER_SHA256: d1405c2787d22a382408f5401fd6e3a9c0747a1356c1c3436014c704f3f991bc
LOCAL_IDENTITY_CONTEXT_SHA256: c56a13e65ac76f6fe59245a5706ec6270c3c85fd69c81aa50fa2e3ce7165acbc
PENDING_EXTERNAL_TRUST_CONFIG_SHA256: d59292473a58dd87bb9172ed6c8daedbfa6bdf8c4f5edb13ce6d567a904e22cb
WATCHER_SHA256: 2a25159b429e632926f9f40e76190a1e70b25ee5dd16e99b5ce977da736e8490
PREFLIGHT_SHA256: 6518908e72f39fd6ba1200b0066220e94140d88cc927c2d2180c0f8e17408785
MATERIALIZER_SHA256: cd71be5a65dfc90fa6fdf76f2e865a4651fd717c03fbb6b05cc1dad147020b0e
PRE_V03_GATE_SHA256: cbf4e25d7d6a544ca5709f7661f56b927ac766cdbc5bb5292c4475bc410a407a
LATEST_BLOCKED_EVIDENCE_SHA256: 135d310986a3ebec1c90b55dab812b017374fafe1937bba7c666709d06101beb
EXTERNAL_TRUST_STATUS: PENDING_EXTERNAL_KEY
READY_FLAG_PRESENT: false
NATIVE_POLICY_CANDIDATE_PRESENT: false
HKLM_NATIVE_TRUST_PRESENT: false
LAB_STATE: STOPPED
NATIVE_EXECUTION_STARTED: false
V02_ADVANCED: false
```

## Transaction

The periodic V02 watcher was quiesced through the real user systemd bus before runtime files changed. A private backup of the prior `validation-ops` directory was created. Only independently reviewed/audited pending-anchor tooling was installed; the existing native trust installer and unrelated private operations were preserved.

The sensitive local host/operator context was copied only from the private local source, installed mode 600 and verified against the reviewed SHA-256. It is not stored in Git. The Ed25519 trust config was installed exactly as reviewed with `status=PENDING_EXTERNAL_KEY`, null key material and null provenance; deployment therefore cannot authorize an external decision.

## Post-deployment verification

Runtime manifest verification passed all 15 reviewed source/test files. The live runtime then passed:

- external-authenticity regression: 6/6;
- hardened full-validator regression: 6/6;
- watcher fail-closed regression: 3/3;
- Python compile and shell syntax checks;
- real-inbox preflight: `MISSING / APPROVAL_ENVELOPE_MISSING`;
- real watcher: BLOCKED with READY absent;
- pre-V03 stage: `PRE_V03_STAGE_BLOCKED_AUTHORITY`, rc=12;
- external trust config: `PENDING_EXTERNAL_KEY`;
- native policy candidate: absent;
- HKLM Phase00 native trust: absent;
- `AI-FILM-P00-LAB`: Stopped.

The watcher timer was re-enabled only after all checks passed and is `enabled` + `active (waiting)`. No native procedure was executed and no qualification/SITE/HOST_READY claim changed.

## Remaining gate

Deployment closes the local tooling-authenticity defect but does **not** close V02. The external owner/controller must independently establish an Ed25519 public-key identity/provenance. Activating that public key is a separate reviewed transaction that updates the trust config and its pinned hash. Only a subsequently externally signed exact approval envelope plus the fully validated protected object graph can produce `LAB_EXECUTION_AUTHORITY_VERIFIED`.
