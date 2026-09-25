# NEXT WORK ITEM — T-019 Z-Image formal casting smoke

STATUS: READY
MILESTONE: M2
TASK: run the fixed four-job 1024×1024 Z-Image casting smoke on the authorized RunPod A40, then ingest measured evidence before blind scoring.

COMPLETED Z-IMAGE QUALIFICATION:
- exact revision 04cc4abb7c5069926f75c9bfde9ef43d49423021
- canonical job castjob_8e02916e0db64eb6 / seed 2382532974
- 512×512, 50 steps, guidance 4, cfg_normalization=false, BF16 FULL_GPU
- native canonical negative_prompt applied
- status: PASS
- load CPU: 7.743865s; transfer to CUDA: 4.718485s
- inference: 21.623722s; total elapsed: 34.140679s
- nvidia-smi after load: 20,263 MiB; measured peak: 21,913 MiB
- artifact SHA-256: 682f2ae66cf262004e5487d809e7c840c8a4fc2e86ba8529f98a446294a2f567
- raw evidence SHA-256: db0dec072f4c77aff01e5cf97d5145ec376b97e32c0d22086d4c8f2659465af4
- estimated compute cost: USD 0.004647
- canonical cost ledger after qualification: USD 0.118397
- profile remains admission_ready=false because the 1024 four-job comparison profile is still unmeasured

RUNNER_READY:
- model-evaluations/slice01/z_image_casting_profile.json
- film/z_image_casting.py
- tools/run_z_image_casting_batch.py
- fixed population: An/Linh × photoreal/stylized_3d × face_front
- profile itself remains non-authorizing; execution context validates active A40 receipt/budget and the prior 512 gate

NEXT:
1. Execute the fixed four-job Z-Image population at 1024×1024, 50 steps, guidance 4, cfg_normalization=false.
2. Capture per-job elapsed/peak VRAM/output hashes and batch estimated cost.
3. Only after 4/4 PASS, derive required_vram_gb + reserve and mark Z-Image resource admission ready.
4. Then prepare blind comparison scoring; do not select a winner before complete blind scores.

DO NOT:
- promote Z-Image admission from the 512-only result
- treat smoke assets as production references
- create another Pod/resource
- exceed the USD 60 project cap
- publish content
