# NEXT WORK ITEM — complete owner media review, then promote scored benchmark inputs

STATUS: READY
MILESTONE: M2 + M4

COMPLETED:
- image owner score set complete 8/8 on the owner-defined 0–8 scale; FLUX2 and Z-Image tie;
- VoxCPM2 fixed packet generated 12/12, 10/12 cue-fit, all WAVs synced/hash-verified;
- Wan2.2 TI2V-5B admitted on A40 and balanced motion probes generated 2/2;
- Tang Chang'an and Belle Époque Paris world profiles proven through generated image → Wan motion technical media;
- all current generated binaries are synced off the root-only Pod.

OWNER REVIEW:
- local review page: http://localhost:8765/
- required score set: 12 voice samples + blind motion_A/motion_B;
- scale: integer 0–8;
- click Submit & Save after all 14 scores; server writes /home/dragon/ai-film-dev/media/slice01/owner-review-20260926/owner_review_scores_20260926.json;
- motion mapping stays sealed until the complete score set is ingested.

NEXT AFTER COMPLETE SCORES:
1. ingest the server-saved owner review JSON with tools/ingest_owner_review_scores.py;
2. unblind motion only after all 14 scores validate;
3. build the fail-closed scored-media promotion plan with tools/build_scored_benchmark_plan.py; unique motion top score may configure the benchmark, while a tie blocks;
4. promote only scored media/reference choices into the first multi-shot M3/M4 quality benchmark;
5. keep 14B/LTX gated until measured admission/runtime evidence exists.

PAID RESOURCE:
- existing RunPod A40 only, USD 0.49/h, hard cap USD 60;
- lifetime provider bill snapshot USD 9.971950;
- no useful GPU batch is queued while owner review is pending; stopping the existing Pod is recommended if review will pause.

DO NOT:
- generate more GPU benchmark media merely to keep the Pod busy;
- treat technical world probes as historical-accuracy or production-quality approval;
- promote voice or motion quality before complete owner scores;
- create another paid resource or publish content.