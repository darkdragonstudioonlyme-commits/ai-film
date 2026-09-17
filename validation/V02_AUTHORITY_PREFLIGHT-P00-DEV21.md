# Phase00 dev21 — V02 external-authority staging preflight

```yaml
PREFLIGHT_RECORD_ID: V02-AUTHORITY-PREFLIGHT-P00-DEV21-001
STATUS: PASS
SCRIPT: /home/dragon/ai-film-dev/validation-ops/v02-authority-preflight.py
SCRIPT_SHA256: 6518908e72f39fd6ba1200b0066220e94140d88cc927c2d2180c0f8e17408785
VALIDATOR: /home/dragon/ai-film-dev/validation-ops/v02-authority-intake.py
USES_EXACT_V02_VALIDATOR_SEMANTICS: true
WRITES_READY_FLAG: false
WRITES_HKLM: false
STARTS_LAB: false
STARTS_NATIVE_EXECUTION: false
MUTATES_STAGING: false
CURRENT_INBOX_TEST: MISSING_APPROVAL_ENVELOPE
MALFORMED_STAGING_TEST: INVALID_ENVELOPE_SCHEMA
READY_FLAG_AFTER_TESTS: absent
```

The preflight is a wrapper around the existing V02 authority validator rather than an alternate implementation. It runs the exact validator with `--inbox <staging>`, snapshots the staging directory metadata before and after execution, and refuses the result if the staging tree changes while the validator runs.

It deliberately exposes only normalized classification and non-sensitive summary fields. It does not dump protected object bodies, raw operator identity material, credentials or authority contents.

Return semantics:

- `0`: `READY_FOR_INTAKE` — the exact validator reports READY for that staging package. This still does not create the authoritative watcher READY flag or advance the run.
- `10`: `MISSING` — approval envelope absent.
- `11`: `INVALID` — validator rejected package; `reason` is the exact validator failure class such as schema/ref/coverage/time/pin mismatch.
- `3`: preflight detected staging mutation during validation and fails closed.
- `4`: validator output could not be normalized.

Observed tests:

1. The current authoritative inbox returned `MISSING / APPROVAL_ENVELOPE_MISSING`, with `staging_unchanged=true`.
2. A disposable staging directory containing an empty `approval-envelope.json` returned `INVALID / ENVELOPE_SCHEMA`, with identical before/after staging metadata and no READY flag.

This tool is intended for external-owner packaging QA before a package is moved into the protected authoritative inbox. It cannot create independent authority, approve a package, install trust, or satisfy V02 by itself.

## Deployed external-authenticity hardening

Finding `V02-AUTHENTICITY-001` shows that the operator-writable approved inbox is not by itself proof of external provenance. The independently reviewed/audited hardening in `validation/V02_EXTERNAL_AUTHENTICITY_HARDENING-P00-DEV21.md` is deployed. The Ed25519 trust config intentionally remains `PENDING_EXTERNAL_KEY`; therefore this step remains BLOCKED until external key provenance is established and separately activated, and no readiness/preflight result may be interpreted as authority.
