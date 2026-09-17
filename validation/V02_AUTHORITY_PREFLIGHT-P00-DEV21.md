# Phase00 dev21 — V02 external-authority staging preflight

```yaml
PREFLIGHT_RECORD_ID: V02-AUTHORITY-PREFLIGHT-P00-DEV21-001
STATUS: PASS
SCRIPT: /home/dragon/ai-film-dev/validation-ops/v02-authority-preflight.py
SCRIPT_SHA256: f756eda462ce4555622dae36164f00872664747a0c87c5578521f7e0c66d5236
VALIDATOR: /home/dragon/ai-film-dev/validation-ops/v02-authority-intake.py
USES_EXACT_V02_VALIDATOR_SEMANTICS: true
WRITES_READY_FLAG: false
WRITES_HKLM: false
STARTS_LAB: false
STARTS_NATIVE_EXECUTION: false
MUTATES_STAGING: false
BYTE_INTEGRITY_SNAPSHOT: true
SYMLINK_TARGET_SNAPSHOT: true
CURRENT_INBOX_TEST: MISSING_APPROVAL_ENVELOPE
MALFORMED_STAGING_TEST: INVALID_ENVELOPE_SCHEMA
READY_FLAG_AFTER_TESTS: absent
```

The preflight is a wrapper around the existing V02 authority validator rather than an alternate implementation. It runs the exact validator with `--inbox <staging>`, snapshots the staging tree before and after execution, and refuses the result if that tree changes while the validator runs.

The snapshot is content-aware: regular files bind type/mode/size/mtime plus streaming SHA-256 bytes; symlinks bind their link target without following them; directories bind type/mode/mtime. A same-size content rewrite with restored mtime therefore still fails closed as `PREFLIGHT_MUTATED_STAGING`.

It deliberately exposes only normalized classification and non-sensitive summary fields. It does not dump protected object bodies, raw operator identity material, credentials or authority contents.

Return semantics:

- `0`: `READY_FOR_INTAKE` — the exact validator reports READY for that staging package. This still does not create the authoritative watcher READY flag or advance the run.
- `10`: `MISSING` — approval envelope absent.
- `11`: `INVALID` — validator rejected package; `reason` is the exact validator failure class such as schema/ref/coverage/time/pin mismatch.
- `3`: preflight detected staging mutation during validation and fails closed.
- `4`: validator output could not be normalized.

Observed tests include the current missing-envelope and malformed-envelope cases plus a persistent regression where a synthetic validator rewrites a file to different bytes of the same size and restores its mtime; the byte-aware snapshot rejects that mutation.

This tool is intended for external-owner packaging QA before a package is moved into the protected authoritative inbox. It cannot create independent authority, approve a package, install trust, or satisfy V02 by itself.

## External-authenticity boundary

Finding `V02-AUTHENTICITY-001` remains authoritative: an operator-writable approved inbox is not by itself proof of external provenance. The independently reviewed/audited Ed25519 hardening remains deployed and the trust config remains `PENDING_EXTERNAL_KEY`; therefore V02 stays BLOCKED until external key provenance is established and separately activated. No readiness/preflight result may be interpreted as authority.
