# Batch 007 contracts

T-023 image worker request:
- compiles from a casting job + exact model matrix + pinned GPU runtime;
- carries exact job/model/prompt/seed identity;
- output manifest must bind request/job/model hashes;
- provider_resource_created, paid_authority_inherited and execution_permitted remain false.

T-024 casting ingestion:
- accepts only output manifests bound to known casting jobs;
- verifies job digest, blind id, model revision, seed and SHA-256 fields;
- writes a reference index and public blind asset binding;
- never chooses a model winner or fills accepted reference slots before blind scoring/acceptance.

T-025 decision ledger:
- aggregates status, elapsed time, peak VRAM, quality, usable rate and USD cost;
- incomplete expected model/shot populations return INSUFFICIENT_EVIDENCE and an empty evidence_order;
- complete evidence may produce a deterministic evidence ordering;
- selected_winner remains null and selection_authorized remains false. Purchase/production decisions remain human-authorized.
