# Phase00 dev21 — V02 external authority intake

```yaml
INTAKE_ID: V02-AUTHORITY-INTAKE-P00-DEV21-001
RUN_ID: RUN-P00-VALIDATION-001
STEP_ID: V02_LAB_EXECUTION_AUTHORITY
STATUS: BLOCKED_AWAITING_EXTERNAL_APPROVAL_ENVELOPE
CANDIDATE_ID: 336b12af-cada-4968-8083-8a5b41e479a2
PENDING_BUNDLE_INDEX_SHA256: fa38540df54df9ebb87929c43e9fe8fbcd09e290e93d8c5d53d7af991df8f615
VALIDATOR_SHA256: 312a72ddc1a8551a85d93b275ea0ccfe84b87ca3ab9e575753d945c7b6f69667
WATCHER_SHA256: bc57a031a781cbe7e64036eb9c462ba2c8d63a11b1ef1e182fd7229a73548c35
ENVELOPE_TEMPLATE_SHA256: 77896f65483a1c3d367daaa9a73d6901ae15dd3c89681ba3a57007ff992015fd
INBOX_README_SHA256: 3aad89410b9382c3c85d17c7f4c5ab38bccac573f2755655bf4ec404ec0595b2
LATEST_STATUS_SHA256: 135d310986a3ebec1c90b55dab812b017374fafe1937bba7c666709d06101beb
LATEST_STATUS: BLOCKED
LATEST_REASON: APPROVAL_ENVELOPE_MISSING
READY_TO_ADVANCE: false
NATIVE_EXECUTION_STARTED: false
```

## Protected inbox

The Windows-side authority-approved inbox is ACL-protected with inheritance disabled and exactly two access identities: the current Windows operator and SYSTEM. It currently contains only the non-consumable envelope template, README, and `NO_APPROVAL_PRESENT` marker; `objects/` is empty and `approval-envelope.json` does not exist.

The template is intentionally `decision=PENDING` and `approved_by_external_authority=false`. Creating the inbox does not grant authority.

## Validator boundary

`v02-authority-intake.py` imports the exact dev21 pure authority and harness definitions. Before it can emit `READY_TO_ADVANCE`, it requires and verifies:

- exact candidate, pending-bundle, source/build/test/contract bindings;
- protected LAB registration with external-controller/disposable/no-credential/no-production-mapping assertions and operator scope;
- owner/controller attestations and restore-probed management/isolation recovery object;
- approved LAB plan and exact <=24h `lab_acceptance_suite` covering all 86 reviewed procedures;
- all 85 native fixture specs and every request route/plan reference;
- hash-addressed objects and role pins;
- pure `authority.authorize()` success for every approved execution plan.

It never starts WSL LAB, writes HKLM, performs a native request, or converts `NOT_RUN` to PASS.

## Watcher

`aifilm-p00-v02-authority-watch.timer` is enabled and active every 5 minutes. Its oneshot service has no Internet socket families or capabilities and an observed `systemd-analyze security` exposure score of `4.9 OK`. It only refreshes mode-600 local status evidence. A future valid intake creates a local `READY_TO_ADVANCE.flag` but still does not start LAB or advance the canonical run automatically.

Current validator result is fail-closed: `APPROVAL_ENVELOPE_MISSING`, exit 12, `ready_to_advance=false`.
