# NEXT WORK ITEM — T-019 FLUX.2 formal casting smoke

STATUS: READY
MILESTONE: M2
TASK: run the fixed four-job 1024×1024 FLUX.2 klein casting smoke on the authorized RunPod A40, then ingest measured evidence before broader casting.

COMPLETED QUALIFICATION:
- one canonical FLUX.2 klein job at 512×512 / 4 steps / guidance 1.0 / BF16 / FULL_GPU
- status: PASS
- total elapsed: 10.139162s
- inference: 1.285966s
- peak GPU memory: 16,577 MiB
- artifact SHA-256: f1af28a78a13be0bc8f3cb82f591f6c2bfa7046658b51b142c67532dc2871bf9
- raw evidence SHA-256: 494b833da19cc03b9dc4146f0c74eeab0ed0d2adb1fe7f07c9247348c1bbf7df
- estimated compute cost: USD 0.00138
- profile remains admission_ready=false because 1024 production smoke has not been measured

NEXT:
1. Run tools/run_flux2_casting_batch.py on the fixed four face_front jobs at 1024×1024.
2. Capture per-job elapsed/peak VRAM, output hashes and batch estimated cost.
3. If all four jobs pass and budget remains healthy, ingest evidence and set a measured 1024 requirement/reserve before admission_ready.
4. Preserve/sync Pod-local PNGs before Pod termination.
5. Then qualify Z-Image on the same fixed population; do not choose a winner before blind scores.

DO NOT:
- create another Pod/resource
- mark FLUX2 admission-ready from the 512-only measurement
- publish or production-accept generated smoke assets
- exceed the USD 60 project cap
