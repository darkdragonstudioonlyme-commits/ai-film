# PRODUCT V2 — Z-Image live qualification runner review

VERDICT: READY FOR PLAN-ONLY MERGE CANDIDATE

Scope:
- exact pinned Tongyi-MAI/Z-Image revision 04cc4abb7c5069926f75c9bfde9ef43d49423021
- RunPod A40 host-bound runtime, Torch 2.8.0+cu128, diffusers 0.40.0
- 512×512 qualification using upstream inference settings: BF16, low_cpu_mem_usage=false, 50 steps, guidance 4, cfg_normalization=false
- native negative_prompt from canonical casting job
- canonical job: castjob_8e02916e0db64eb6 / An photoreal face_front

Safety:
- plan-only is the CI/default path and grants no execution authority
- active A40 USD 60 receipt/budget/runtime/model revision are checked before execution
- model production_gate remains PENDING_DEPENDENCY_DATASET_AND_PUBLICATION_REVIEW
- model_matrix execution_ready remains false
- qualification cannot select a winner, accept production assets, publish, or create another resource
- actual model inference is deferred until this runner is merged and the exact model directory validates

Next after merge:
1. download the exact 18-file diffusers snapshot (~19.1 GiB) to /workspace/models/z-image
2. run one 512 qualification job
3. record VRAM/time/cost/hash evidence
4. only if PASS, add/run the fixed four-job 1024 comparison smoke
