# NEXT WORK ITEM — complete the multi-model automatic evaluation gate

STATUS: READY
MILESTONE: M2 + M3 + M4

HUMAN REVIEW POLICY:
- no owner scoring for current short voice/image/motion takes;
- human review begins at LONGFORM_ROUGH_CUT and FINAL_CUT;
- later owner 0–8 scores are calibration labels for evaluator weights, not prerequisites for short-take iteration.

COMPLETED AUTO_EVAL:
- voice evaluator v1 false negatives from clock notation and Traditional/Simplified variants are preserved as audit history; v2 normalization corrected them without inference;
- 10 voice AUTO_SHORTLIST samples are locked in model-evaluations/auto-eval/voice_shortlist_20260926.json;
- unattended 2-job VoxCPM2 retry batch is dry-run validated and waits only for the same authorized A40;
- longform rough-cut/final-cut owner review contract is ready; labels feed calibration only after at least 3 reviewed cuts and never mutate weights automatically.
- Whisper turbo exact-checksum CPU runtime: qualified;
- canonical Whisper v2 re-score: 12/12 voice takes => 10 AUTO_SHORTLIST, 2 AUTO_RETRY, 0 reject;
- Qwen3-VL-2B CPU runtime: qualified and evaluated 4/4 current video takes;
- PaddleOCR CPU runtime: qualified and evaluated 4/4 current video takes;
- Z-Image-reference motion is AUTO_REJECT_HARD_FAIL from UNMOTIVATED_READABLE_TEXT before weighted score;
- DOVER remains disabled because its current upstream license is non-commercial.

REQUIRED VIDEO ENSEMBLE:
- VBench: subject/background consistency, motion smoothness, dynamic degree, aesthetic and imaging quality;
- Qwen3-VL-2B: semantic adherence, character consistency, continuity, world/period consistency;
- PaddleOCR: generated text/logo artifact detection.

FAIL-CLOSED RULES:
- missing required evaluator => BLOCKED;
- severe objective failure => AUTO_REJECT_HARD_FAIL before score;
- high weighted score => AUTO_SHORTLIST only;
- automatic evaluation never grants production acceptance or publish authority.

CURRENT BLOCKER:
- VBench is the only missing required evaluator;
- VBench requires isolated CUDA <=12.1 runtime on the existing authorized A40;
- Pod 0h1twwxqw6yx0k is EXITED; restart attempt failed because its retained host has no free A40;
- do not create a new Pod/resource.

NEXT:
1. retry start on the same authorized A40 only;
2. create/pin isolated VBench cu121 runtime and exact repo revision;
3. run VBench only on the 3 eligible video takes; the Z-Image-reference clip is already terminal AUTO_REJECT_HARD_FAIL;
4. aggregate 3-model video receipts and rank takes;
5. promote only AUTO_SHORTLIST media into the first multi-shot M3/M4 benchmark;
6. execute the 2-request zh-CN cue-overflow retry plan when the same A40 is available; do not ask the owner to score short takes.

PAID RESOURCE:
- existing RunPod A40 only, USD 0.49/h, hard cap USD 60;
- provider lifetime bill snapshot USD 10.607923;
- Pod is EXITED, so only retained disk is currently billable.
