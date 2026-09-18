# Phase00 V02 validation tooling source — dev22 local authority

This directory preserves exact source for dev22 host-side V02 tooling. Runtime copies live under `/home/dragon/ai-film-dev/validation-ops/` only after independent review/audit and byte-for-byte deployment verification.

The owner selected Choice B: same-WSL local operator authority. The tooling therefore never claims independent/external provenance. `local-operator-trust-anchor.json` starts `PENDING_LOCAL_KEY`; the private Ed25519 key may be generated locally only after the tooling/trust schema is independently audited. Private key bytes never enter Git or the approval inbox.

`dev22-candidate-binding.json` immutably binds candidate ID, exact source/package/build/test/contract and authority model. The intake rejects old external envelope schema, requires `controller_external=false` in registration/fixtures, verifies exact local signature bytes and preserves content-addressed role pins, <=24h suite validity, current-evaluation invalidation, preflight byte-integrity and pre-V03 fail-closed behavior.

Tests use only synthetic keys/staging directories. They grant no LAB authority or native PASS.

Deployment of an ACTIVE local key must also pass `verify_local_authority_key_parity.py` against the owner-only private/public files and metadata. File mode alone is not key identity evidence. A trust anchor whose corresponding private identity is unavailable is superseded, never regenerated under the old identity.
