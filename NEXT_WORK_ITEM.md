# NEXT WORK ITEM — complete the multi-model automatic evaluation gate

STATUS: READY
MILESTONE: M2 + M3 + M4

HUMAN REVIEW POLICY:
- no owner scoring for current short voice/image/motion takes;
- human review begins at LONGFORM_ROUGH_CUT and FINAL_CUT;
- later owner 0–8 scores are calibration labels for evaluator weights, not prerequisites for short-take iteration.

COMPLETED AUTO_EVAL:
- Whisper turbo exact-checksum CPU runtime: qualified;
- 12/12 VoxCPM2 voice takes evaluated: 9 AUTO_SHORTLIST, 1 AUTO_RETRY, 2 AUTO_REJECT_SCORE;
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
3. run VBench on the 4 current video takes;
4. aggregate 3-model video receipts and rank takes;
5. promote only AUTO_SHORTLIST media into the first multi-shot M3/M4 benchmark;
6. regenerate/retry the 1 voice AUTO_RETRY + 2 voice AUTO_REJECT_SCORE samples without asking the owner to score short takes.

PAID RESOURCE:
- existing RunPod A40 only, USD 0.49/h, hard cap USD 60;
- provider lifetime bill snapshot USD 10.607923;
- Pod is EXITED, so only retained disk is currently billable.
