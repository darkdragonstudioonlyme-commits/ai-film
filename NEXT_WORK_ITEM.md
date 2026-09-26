# NEXT WORK ITEM — T-019 blind image comparison + VoxCPM2 qualification

STATUS: READY
MILESTONE: M2

IMAGE EVIDENCE COMPLETE:
- FLUX.2 klein 4B formal smoke: 4/4 PASS @ 1024×1024
- Z-Image formal smoke: 4/4 PASS @ 1024×1024
- Z-Image peak: 26,227 MiB nvidia-smi / 25,892 MiB Torch
- Z-Image mean job: 86.360403s; total 353.466833s
- Z-Image formal cost: USD 0.048111
- canonical project execution ledger: USD 0.166508 / USD 60
- both model resource profiles are admission-ready on this A40; model_matrix execution_ready remains false

BLIND COMPARISON READY:
- projects/slice01/casting/formal_comparison/blind_items.json
- projects/slice01/casting/formal_comparison/blind_map_private.json
- projects/slice01/casting/formal_comparison/scores.csv
- 8 samples = 2 models × 2 characters × 2 styles × face_front
- public packet contains no model identity
- scores are blank; selection_authorized=false

NEXT:
1. Materialize/copy the 8 Pod-local smoke PNGs into a neutral blind-ID directory without changing hashes.
2. Verify each neutral copy against canonical asset_sha256 and expose them for blind review.
3. Do not unblind/rank until all 8 score rows are complete.
4. In parallel, qualify VoxCPM2 exact pinned runtime and fixed 12-sample EN/ZH/VI Voice Design packet under the same USD 60 budget.
5. Keep voice cloning/reference_audio disabled.

DO NOT:
- rerun FLUX2 or Z-Image formal smoke without a new explicit premise
- select an image-model winner before complete blind scores
- treat smoke images as production casting references
- create another Pod/resource
- exceed USD 60
- publish content
