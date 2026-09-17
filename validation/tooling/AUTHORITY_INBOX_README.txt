AI-FILM Phase00 V02 external authority intake

This inbox is NOT authority by itself.
Do not rename approval-envelope.template.json to approval-envelope.json unless an external authority has actually approved candidate 336b12af-cada-4968-8083-8a5b41e479a2.

A valid intake requires immutable hash-addressed JSON objects in objects/<sha256>.json plus approval-envelope.json binding the exact dev21 build/test/contract and pending bundle identities.

The validator checks registration containment, external attestations, recovery refs, fixture coverage, all 86 suite procedure digests, <=24h suite validity, execution-plan objects, and pure authorize() admission for every approved plan.

No passwords, raw MachineGuid, signing secrets, or unrelated credentials belong here.

Hardened V02 also requires a separately reviewed ACTIVE Ed25519 trust anchor and approval-envelope.sig.json authenticating the exact raw approval-envelope.json bytes.
The committed runtime trust anchor starts PENDING_EXTERNAL_KEY. Do not generate a local key to satisfy this requirement; external key identity/provenance must be established out-of-band and independently reviewed.
