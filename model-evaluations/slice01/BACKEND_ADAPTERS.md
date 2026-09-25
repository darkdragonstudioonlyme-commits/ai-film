# Backend adapter contracts

Scope: deterministic translation only. No adapter in this batch executes inference.

Implemented evaluation backends:
- z-image -> diffusers ZImagePipeline
- flux2-klein-4b -> diffusers Flux2KleinPipeline
- wan22-ti2v-5b -> Wan 2.2 TI2V-5B
- wan22-i2v-14b -> Wan 2.2 I2V-A14B
- ltx-2.5 -> LTX-2.5

The adapter binds exact model source repo/revision from model_matrix.json, job/job_digest, compiled prompt SHA-256, shot identity, style/aspect/resolution, seed and resolved references. Missing required references, disabled models, unknown models and prompt hash drift fail closed. execution_permitted mirrors model execution_ready and therefore remains false until the later runtime/paid-resource gates are satisfied.

Qwen-Image-2.1 is intentionally rejected because it is disabled by the current commercial gate. Downstream Wan-Animate-2, lip-sync, voice and music adapters are added only when their stages become active.
