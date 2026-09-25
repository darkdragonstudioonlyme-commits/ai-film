# Batch 006 — casting jobs, blind score gate, VoxCPM2 adapter

T-020:
- 16 casting reference slots are crossed with the two enabled image-eval models, producing 32 deterministic jobs.
- Every job binds character/style/slot/model exact revision/prompt/seed and remains non-executing.
- Public blind items expose only blind id, style, slot and output placeholders. Character/model identity stays in the private map.

T-021:
- score population must match the public blind packet exactly;
- every criterion must be numeric 1–5 before unblinding;
- duplicate, missing, extra or out-of-range scores fail closed;
- the ingestion CLI reads the private map only after public score completeness passes;
- ranking is deterministic by mean overall score and stable group key.
This is a process seal for blind review, not cryptographic secrecy from a repository administrator.

T-022:
- 12 VoxCPM2 Voice Design requests bind exact repo revision, package, voice group, language, text, seed, cfg and timesteps.
- reference_audio is always null; execution_permitted is false.
- output manifests must bind exact request_digest/blind_id, SHA-256, 48 kHz, duration and byte size.
- scores cannot unblind until all 12 output manifests fit their cue budgets and all score fields are complete.

No model inference or paid compute is performed by this batch.
