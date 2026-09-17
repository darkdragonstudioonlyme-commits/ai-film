# HEALTH_REVIEW-WF-P00-V02-AUTHENTICITY-003

```yaml
HEALTH_REVIEW_ID: HEALTH-WF-P00-V02-AUTHENTICITY-003
RUN_ID: RUN-P00-VALIDATION-001
STEP_ID: V02_LAB_EXECUTION_AUTHORITY
TRIGGER: POST_PROMOTION_V02_FORENSIC_AUTHORITY_AUDIT
STATUS: BLOCKER_CONFIRMED_HARDENING_CANDIDATE
FINDING_ID: V02-AUTHENTICITY-001
SECONDARY_FINDING_ID: V02-WATCHER-FAILCLOSED-002
SEVERITY: CRITICAL_GATE_INTEGRITY
PRODUCT_SOURCE_CHANGED: false
NATIVE_EXECUTION_ADVANCED: false
LAB_STATE: STOPPED
TRUST_ANCHOR_INSTALLED: false
```

## Finding

The existing V02 validator strongly validates content integrity, exact candidate identity, hash-addressed objects, role pins, containment fields, <=24h suite validity and pure `authorize()` admission. It does **not** authenticate who authored the approved package.

Runtime ACL inspection on 2026-09-18 showed both `authority-pending/dev21` and `authority-approved/dev21` have inheritance disabled but grant the current Windows operator account and `NT AUTHORITY\SYSTEM` `FullControl`. The effective ACL identity was confirmed to match the current operator account. Therefore the approved inbox is locally protected from inheritance/other users, but it is not an external-authority boundary against the operator who is being constrained by V02.

The existing validator SHA-256 `05143de5f2ba7b6e58c3e9256cfc0c724f7f38aea3d945368506e3cf1180bc89` validates object bytes and assertions but has no external signature/trust-anchor check. Because the operator has the reviewed procedures and can derive the required local candidate facts, hash addressing alone proves integrity, not external provenance. No forged approval package was created during this audit.

## Fail-closed correction candidate

The candidate adds Ed25519 authentication of the **exact raw bytes** of `approval-envelope.json` before any approval object is consumed. The signature is accepted only under a source-controlled trust-anchor config whose exact SHA-256 is pinned in the verifier. The committed trust anchor is intentionally `PENDING_EXTERNAL_KEY`; it cannot authorize any envelope.

```yaml
HARDENED_VALIDATOR_SHA256: 0ff65ddb2d5e01bc04f4857dde46d321c0610826e108fdc3583100a8b2c3b0b9
AUTHENTICITY_MODULE_SHA256: f89d9688ca39795a0c4fcf9b5a33b9c257f2d9dee8e17cfeb24b6df7de56cbcc
PENDING_TRUST_CONFIG_SHA256: d59292473a58dd87bb9172ed6c8daedbfa6bdf8c4f5edb13ce6d567a904e22cb
TOOLING_MANIFEST_SHA256: ce816d32a234a5d1c25e3cc5cfc393b609f41094d410d1402a8306cd8cb65805
TOOLING_MANIFEST_TEST_SHA256: e583402ce20c0724db20358ef119a7b0564a25169d52c0ea1a237341d283d889
PREFLIGHT_SHA256: 6518908e72f39fd6ba1200b0066220e94140d88cc927c2d2180c0f8e17408785
MATERIALIZER_SHA256: cd71be5a65dfc90fa6fdf76f2e865a4651fd717c03fbb6b05cc1dad147020b0e
PRE_V03_GATE_SHA256: cbf4e25d7d6a544ca5709f7661f56b927ac766cdbc5bb5292c4475bc410a407a
WATCHER_SHA256: 2a25159b429e632926f9f40e76190a1e70b25ee5dd16e99b5ce977da736e8490
AUTHENTICITY_TEST_SHA256: 61bdf99aa38bc51e58baad54bcae21deee5009ea8fdd3e7affb7043a59566d10
HARDENED_VALIDATOR_TEST_SHA256: 70348264e24e24086d60ed68b6bd519cf5dffbddd62d3dc9c244378e9229fdf9
WATCHER_FAILCLOSED_TEST_SHA256: f2e94bb8f1094c1f0d806cd6f0e1d210c22c6fbefe0a21e3e2606321c16bb502
LOCAL_IDENTITY_LOADER_SHA256: d1405c2787d22a382408f5401fd6e3a9c0747a1356c1c3436014c704f3f991bc
LOCAL_IDENTITY_CONTEXT_EXPECTED_SHA256: c56a13e65ac76f6fe59245a5706ec6270c3c85fd69c81aa50fa2e3ce7165acbc
```

## Negative evidence

Persistent synthetic tests use a generated **test-only** Ed25519 key that is explicitly not authority. Six signature-layer cases pass: pending anchor rejection, valid synthetic signature verification, payload-digest tamper rejection, key-id mismatch rejection, trust-config drift rejection and invalid-signature rejection.

Full hardened-validator staging tests add six cases: existing `MISSING`, existing PENDING decision rejection, operator-authored `APPROVE=true` with absent refs, operator-authored syntactically valid fake refs, a fake operator signature under the still-pending anchor, and local identity-context drift. The three operator-authored APPROVE variants stop at `EXTERNAL_AUTHENTICITY_ANCHOR_PENDING` before object consumption; identity drift fails separately. Staging remains unchanged.


## Secondary watcher finding

Independent review found a separate fail-closed gap in the deployed watcher SHA `acb117e22af0a574a0912c3545b75d6d1d3ff6bbf6223408b693f48a863c05e1`. It moved validator output into `latest.json` and then parsed `status` under `set -e`; malformed/non-JSON validator output could terminate the script before the error branch removed an old READY flag. No stale READY flag existed during this audit.

The candidate watcher deletes `READY_TO_ADVANCE.flag` **before every evaluation** and recreates it only after current `READY_TO_ADVANCE:0`. Parse failure is normalized to `UNREADABLE` and exits nonzero with READY absent. Three adversarial watcher cases prove crash/non-JSON cleanup, BLOCKED cleanup and evidence-bound READY recreation.

## Activation boundary

This health record does not activate a public key, approve LAB execution or advance V02. External owner/controller must independently establish an Ed25519 public-key identity and provenance. Activating that key requires a separate reviewed trust-anchor update that changes both the trust config and its pinned hash. Only then may the external authority sign the exact approval envelope. V03 remains forbidden until signed intake, native-policy staging and trust-anchor installation all pass.
