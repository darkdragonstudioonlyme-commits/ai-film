# AI-FILM — Resume v2

GOAL: ship a measurable 60–90 second vertical slice before adding more infrastructure.
MILESTONE: short-take quality gates now use multi-model AUTO_EVAL; owner review is deferred to longform rough cut/final cut.
LIVE_GPU: existing RunPod Pod 0h1twwxqw6yx0k, NVIDIA A40, EXITED; same-host restart currently capacity-blocked.
AUTHORITY: maximum USD 60; existing A40 Pod only; no new resource or publication authority.
OWNER_ACTION: none for current short voice/motion takes. Human 0–8 scoring resumes at longform rough cut/final cut and later calibrates evaluator weights.
PAID_RESOURCE: provider_billed=USD 10.607923/USD 60 | GPU compute stopped | retained 250 GB disk still bills.
AUTO_EVAL_STACK: video=VBench + Qwen3-VL-2B + PaddleOCR; voice=Whisper turbo + deterministic cue-fit. DOVER stays disabled because the current upstream license is non-commercial.
AUTO_EVAL_VOICE: canonical v2 COMPLETE 12/12 — 10 AUTO_SHORTLIST, 2 AUTO_RETRY, 0 reject; mean 89.854707/100. V1 is retained as superseded audit evidence.
AUTO_EVAL_VIDEO: PARTIAL — Qwen3-VL 4/4 + PaddleOCR 4/4 complete; Z-Image-reference motion hard-fails UNMOTIVATED_READABLE_TEXT and is excluded from remaining GPU eval; VBench is pending for 3 eligible clips.
AUTO_EVAL_POLICY: hard fail precedes weighted score; missing required evaluator blocks; automatic outcomes never grant production acceptance or publish authority.
WORLD_CAPABILITY: Tang Chang'an and Belle Époque Paris image→motion technical proof PASS; no historical-accuracy or production-quality acceptance.
MEDIA_SYNC: all previously generated slice/world media required for current auto-eval batch is local and hash-verified.
ROUGH_CUT_AUDIO: 10 hash-verified voice candidates prepared; EN/VI have 4/4 dialogue candidates, ZH has dlg_002/dlg_003 while dlg_001 waits for retry. Candidate-only, not production-final.
COST_LEDGER: measured generation execution remains USD 0.455474; provider lifetime bill is the paid-budget truth.
NEXT: VBench still waits for the same A40. The 10 voice shortlist is locked; the 2-request zh-CN cue-overflow retry plan is wired into an unattended VoxCPM2 batch and ready when the same A40 returns; longform review contract is ready.
SAFETY: no short-take human gate, no automatic production acceptance, no publish, no new paid resource, hard cap USD 60.
