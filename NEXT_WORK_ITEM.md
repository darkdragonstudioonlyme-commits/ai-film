# NEXT WORK ITEM — T-019 Z-Image qualification on A40

STATUS: READY
MILESTONE: M2
TASK: qualify the exact pinned Z-Image runtime and run the same four face_front comparison jobs after FLUX.2 formal smoke passed.

FLUX2 FORMAL SMOKE COMPLETE:
- four fixed face_front jobs, characters An/Linh × photoreal/stylized_3d
- 1024×1024, 4 steps, guidance 1.0, BF16 FULL_GPU
- 4/4 PASS
- total elapsed: 15.430117s
- mean job elapsed: 2.366221s; median: 2.239497s
- max torch reserved: 20,080 MiB; max nvidia-smi: 20,415 MiB
- estimated batch compute cost: USD 0.0021
- cost ledger total: USD 0.11375
- FLUX2 profile required_vram_gb=20.0 + reserve=4.0, admission_ready=true
- outputs remain smoke evidence only; no winner/production acceptance/publication

NEXT:
1. Inspect exact Z-Image model repository/revision and dependency/runtime requirements.
2. Download only required inference components into /workspace/models.
3. Run a single low-resolution qualification before the four-job 1024 comparison smoke.
4. Ingest Z-Image measurement/cost evidence before any blind scoring.
5. Preserve/sync all FLUX2/Z-Image smoke assets before Pod termination.

DO NOT:
- select FLUX2 as winner before blind scores
- treat smoke assets as production references
- create another Pod/resource
- exceed the USD 60 project cap
