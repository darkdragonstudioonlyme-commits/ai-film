# PRODUCT V2 — Z-Image 512 A40 qualification review

VERDICT: PASS FOR FORMAL 1024 SMOKE; NOT ADMISSION-READY

Observed on the owner-authorized RunPod A40:
- exact revision 04cc4abb7c5069926f75c9bfde9ef43d49423021
- canonical job castjob_8e02916e0db64eb6 / seed 2382532974
- 512×512, 50 steps, guidance 4, cfg_normalization=false, BF16, FULL_GPU
- canonical negative prompt applied natively through ZImagePipeline
- runtime: Torch 2.8.0+cu128 / CUDA 12.8 / diffusers 0.40.0
- load CPU 7.743865s; transfer to CUDA 4.718485s
- inference 21.623722s; total 34.140679s
- nvidia-smi after load 20,263 MiB; measured peak 21,913 MiB
- output PNG 330,159 bytes, SHA-256 682f2ae66cf262004e5487d809e7c840c8a4fc2e86ba8529f98a446294a2f567
- raw Pod evidence 7,174 bytes, SHA-256 db0dec072f4c77aff01e5cf97d5145ec376b97e32c0d22086d4c8f2659465af4
- estimated compute cost USD 0.004647

Boundary:
- this 512 result is real runtime/VRAM evidence but is not enough to derive the 1024 production comparison requirement;
- required_vram_gb and vram_reserve_gb remain null; admission_ready remains false;
- model_matrix execution_ready remains false;
- artifact is smoke evidence only; production_acceptance/selection/publish authority remain false;
- next valid gate is the fixed four-job 1024×1024 face_front comparison smoke matching the FLUX2 population.
