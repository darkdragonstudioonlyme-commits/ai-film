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

RUNNER PREPARED:
- exact pinned Z-Image revision: 04cc4abb7c5069926f75c9bfde9ef43d49423021
- diffusers 0.40.0 ZImagePipeline import verified on A40 runtime
- upstream pinned settings: BF16, low_cpu_mem_usage=false, 50 steps, guidance 4, cfg_normalization=false
- qualification runner is plan-first and uses native canonical negative_prompt

NEXT:
1. Merge the plan-only Z-Image qualification runner.
2. Download the exact 18-file diffusers snapshot into /workspace/models/z-image.
3. Run a single low-resolution qualification before the four-job 1024 comparison smoke.
4. Ingest Z-Image measurement/cost evidence before any blind scoring.
5. Preserve/sync all FLUX2/Z-Image smoke assets before Pod termination.

DO NOT:
- select FLUX2 as winner before blind scores
- treat smoke assets as production references
- create another Pod/resource
- exceed the USD 60 project cap
