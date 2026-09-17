# Phase00 dev21 — V02 external authority intake

```yaml
INTAKE_ID: V02-AUTHORITY-INTAKE-P00-DEV21-001
RUN_ID: RUN-P00-VALIDATION-001
STEP_ID: V02_LAB_EXECUTION_AUTHORITY
STATUS: BLOCKED_AWAITING_EXTERNAL_APPROVAL_ENVELOPE
CANDIDATE_ID: 336b12af-cada-4968-8083-8a5b41e479a2
PENDING_BUNDLE_INDEX_SHA256: fa38540df54df9ebb87929c43e9fe8fbcd09e290e93d8c5d53d7af991df8f615
VALIDATOR_SHA256: 0ff65ddb2d5e01bc04f4857dde46d321c0610826e108fdc3583100a8b2c3b0b9
WATCHER_SHA256: 2a25159b429e632926f9f40e76190a1e70b25ee5dd16e99b5ce977da736e8490
ENVELOPE_TEMPLATE_SHA256: 77896f65483a1c3d367daaa9a73d6901ae15dd3c89681ba3a57007ff992015fd
INBOX_README_SHA256: b53a56ee100064c62c1bef98e6494916f019008ba256cd6d712d16b0b9e334d2
LATEST_STATUS_SHA256: 135d310986a3ebec1c90b55dab812b017374fafe1937bba7c666709d06101beb
LATEST_STATUS: BLOCKED
LATEST_REASON: APPROVAL_ENVELOPE_MISSING
READY_TO_ADVANCE: false
NATIVE_EXECUTION_STARTED: false
AUTHENTICITY_FINDING: V02-AUTHENTICITY-001
HARDENING_STATUS: DEPLOYED_PENDING_EXTERNAL_KEY
HARDENED_VALIDATOR_SHA256: 0ff65ddb2d5e01bc04f4857dde46d321c0610826e108fdc3583100a8b2c3b0b9
AUTHENTICITY_MODULE_SHA256: f89d9688ca39795a0c4fcf9b5a33b9c257f2d9dee8e17cfeb24b6df7de56cbcc
PENDING_TRUST_CONFIG_SHA256: d59292473a58dd87bb9172ed6c8daedbfa6bdf8c4f5edb13ce6d567a904e22cb
TOOLING_MANIFEST_SHA256: ce816d32a234a5d1c25e3cc5cfc393b609f41094d410d1402a8306cd8cb65805
TOOLING_MANIFEST_TEST_SHA256: e583402ce20c0724db20358ef119a7b0564a25169d52c0ea1a237341d283d889
HARDENED_WATCHER_SHA256: 2a25159b429e632926f9f40e76190a1e70b25ee5dd16e99b5ce977da736e8490
WATCHER_FAILCLOSED_TEST_SHA256: f2e94bb8f1094c1f0d806cd6f0e1d210c22c6fbefe0a21e3e2606321c16bb502
LOCAL_IDENTITY_LOADER_SHA256: d1405c2787d22a382408f5401fd6e3a9c0747a1356c1c3436014c704f3f991bc
LOCAL_IDENTITY_CONTEXT_EXPECTED_SHA256: c56a13e65ac76f6fe59245a5706ec6270c3c85fd69c81aa50fa2e3ce7165acbc
```

## Protected inbox

The Windows-side authority-approved inbox is ACL-protected with inheritance disabled and exactly two access identities: the current Windows operator and SYSTEM. Runtime ACL inspection confirms both identities have `FullControl`. It currently contains only the non-consumable envelope template, README, and `NO_APPROVAL_PRESENT` marker; `objects/` is empty and `approval-envelope.json` does not exist.

This ACL protects against inherited/ambient writers but **does not establish external authority against the current operator**. Hash-addressed objects prove integrity, not authorship. Finding `V02-AUTHENTICITY-001` therefore blocks future APPROVE consumption until the reviewed signature/trust-anchor hardening is deployed.

The template is intentionally `decision=PENDING` and `approved_by_external_authority=false`. Creating the inbox does not grant authority.

## Validator boundary

`v02-authority-intake.py` imports the exact dev21 pure authority and harness definitions. Before it can emit `READY_TO_ADVANCE`, it requires exact candidate/content bindings, protected LAB registration/attestations/recovery, approved LAB plan, <=24h suite coverage for all 86 procedures, all 85 native fixture specs, hash-addressed objects and role pins, single-pin `registration/design/code`, actual pin membership for every execution plan/fixture spec, and pure `authority.authorize()` success for every approved plan.

It never starts WSL LAB, writes HKLM, performs a native request, or converts `NOT_RUN` to PASS.

## Adversarial fail-closed checks

- renaming the `PENDING` template to `approval-envelope.json` is rejected with `EXTERNAL_DECISION_NOT_APPROVE`, exit 12;
- changing only the envelope flags to `APPROVE/true` while leaving immutable refs absent is rejected with `ENVELOPE_REF_MISSING`, exit 12;
- a deliberately planted stale `READY_TO_ADVANCE.flag` was removed by the watcher when current validation remained BLOCKED.

No synthetic package was permitted to produce a surviving `READY_TO_ADVANCE` signal.

The hardening candidate adds six persistent signature-layer cases plus full-validator checks showing that operator-authored `APPROVE=true` envelopes stop at `EXTERNAL_AUTHENTICITY_ANCHOR_PENDING` before object consumption. Synthetic test keys are isolated and explicitly non-authoritative.

## Watcher

`aifilm-p00-v02-authority-watch.timer` is enabled and active every 5 minutes. Its oneshot service has no Internet socket families or capabilities and an observed `systemd-analyze security` exposure score of `4.9 OK`. It only refreshes mode-600 local status evidence. The hardened watcher SHA `2a25159b...` is now deployed. It deletes READY before every evaluation and recreates it only from current successful READY evidence; three persistent adversarial cases cover malformed output, BLOCKED and READY. Post-deployment real-inbox execution remained BLOCKED with READY absent. It still does not start LAB or advance the canonical run automatically.

Current validator result is fail-closed: `APPROVAL_ENVELOPE_MISSING`, exit 12, `ready_to_advance=false`.
