# PRODUCT V2 — FLUX.2 klein live runner review

STATUS: PRE-EXECUTION MERGE CANDIDATE

Purpose:
- bind a single canonical casting job to the existing RunPod A40 authorization without changing generic request execution flags;
- enforce exact model/revision/runtime/receipt/cost identity before any GPU inference;
- fixed qualification profile: 512x512, 4 steps, guidance 1.0, BF16/full-GPU;
- preserve upstream production gate in model metadata; this runner authorizes qualification only, not publication.

Safety:
- plan-only is default;
- --execute requires local model dir plus active A40 authority;
- max-runtime cost is checked against the USD 60 project cap before execution;
- no new resource creation or publish authority is accepted;
- output manifest binds request/job/model/seed/artifact hash/elapsed/peak VRAM;
- pass/fail compute cost is evidence-based from measured elapsed time and active USD 0.49/h rate.

Verification:
- 5/5 runner contract tests PASS.
- plan-only resolves canonical casting job castjob_d3ec86da4ca6b1fc.
- exact model revision e7b7dc27f91deacad38e78976d1f2b499d76a294.
- active RunPod A40 authority receipt and USD 60 project cap validated.
- max-runtime reservation for 1800s is USD 0.245; no new resource/publish authority.
- generic request execution_permitted remains false; model execution_ready remains false until measurement evidence is committed.
