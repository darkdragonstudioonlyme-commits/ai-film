# NEXT WORK ITEM — T-019 paid GPU production boundary

STATUS: BLOCKED
MILESTONE: M2
TASK: T-019 — launch the bounded rental-GPU benchmark / first real generation stage.

BLOCKER: EXPLICIT_PAID_GPU_APPROVAL_REQUIRED

READINESS_DAG:
- source_ingestion: COMPLETE
- screenplay_localization: COMPLETE
- continuity_shot_spec: COMPLETE
- casting_reference_generation: BLOCKED only by paid_gpu_authorized
- voice_eval: BLOCKED only by paid_gpu_authorized
- all downstream visual/video/audio/lipsync/edit/delivery stages remain blocked by those generated-media dependencies
- ready_stages: none

PREPARED:
- exact model/runtime/license pins and worker admission
- bounded queue/cost/budget controls
- 32 casting generation jobs + blind scoring
- multilingual voice evaluation requests
- paid launch authorization/rate gate
- asset graph, continuity, QC, rights/publication, edit/render/delivery contracts
- portable spec transport and schema compatibility checks

TO UNBLOCK:
The project owner must explicitly approve a bounded paid GPU amount. Launch time must recheck provider/GPU/rate and bind that snapshot into the authorization receipt.

DO NOT:
- create more preparatory backlog solely to avoid this boundary
- launch/rent GPU without explicit bounded approval
- spend above the approved receipt
- publish content
