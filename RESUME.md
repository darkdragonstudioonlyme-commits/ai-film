# AI-FILM — Resume v2

GOAL: ship a measurable 60–90 second vertical slice before adding more infrastructure.
MILESTONE: M2 voice approval + M4 owner motion scoring remain open; historical-China/European image→video technical capability is proven.
LIVE_GPU: RunPod Pod 0h1twwxqw6yx0k, NVIDIA A40, 46068 MiB, USD 0.49/h.
AUTHORITY: maximum USD 60; existing A40 Pod only; no new resource or publication authority.
OWNER_ACTION: open http://localhost:8765/, score all 12 VoxCPM2 samples + blind motion_A/motion_B on the 0–8 scale, then click Submit & Save; server validation writes owner_review_scores_20260926.json.
PAID_RESOURCE: source=projects/slice01/runtime/gpu_session.json | state=RUNNING idle at owner-review gate | provider_billed=USD 9.971950/USD 60 | GPU util 0%; stop recommended if review will pause.
MEDIA_SYNC: slice01 tracked media 25/25 synced; world-capability generated outputs 5/5 synced/hash-verified; unsynced=0.
WORLD_CAPABILITY: PASS technical proof — Tang Chang'an and Belle Époque Paris each generated a photoreal keyframe plus Wan2.2 motion smoke. Paris v1 was retained as rejected-cost evidence for pseudo-text; v2 removed text-bearing foreground props. No production acceptance.
WAN22_BALANCED_MOTION: 2/2 runtime PASS at 25f/8-step, 704x1280@24fps; peak 31249 MiB; owner quality scoring pending.
WAN22_TI2V_ADMISSION: PASS 17f/5-step A40 smoke; peak 31883 MiB; 32 GiB + 4 GiB reserve admission profile.
IMAGE_MODEL_COMPARISON: owner scores complete; FLUX2 and Z-Image tie at 8/32 each; photoreal preferred over stylized in this round; no winner selected.
VOXCPM2_FORMAL_BATCH: 12/12 PASS_RUNTIME; 10/12 cue-fit; quality/identity awaits owner scoring; no reference audio/no cloning.
COST_LEDGER: measured execution total USD 0.455474 including rejected Paris v1; provider lifetime bill USD 9.971950 including GPU + disk. Budget guard follows provider spend.
NEXT: ingest the server-saved complete owner review JSON, unblind motion only after all 14 scores exist, then use the fail-closed scored-media promotion gate; a motion-score tie blocks rather than guesses.
STORAGE_NOTE: current generated media is synced off the root-only Pod; no separate network volume exists.
SAFETY: no quality/production promotion before owner scoring, no publish, no extra resource creation, hard cap USD 60.