# PRODUCT V2 — Wan2.2 balanced motion batch review

Reviewer: ChatGPT
Scope: wan22-sc01-sh04-balanced-motion-20260926
Tests executed: 273/273 tests PASS; PRODUCT_V2_CHECK_PASS; git diff --check PASS

## Findings
- Both balanced branches used the same Wan2.2 TI2V-5B revision, 25 frames, 8 sampling steps, base seed 52004, and 704×1280 output at 24 fps.
- FLUX2-reference branch: 276.602905s, peak 31,249 MiB, SHA-256 683bc5bdadf896fe23795839872c55b5c129c5c77cad3c12ff69d82525e59a09.
- Z-Image-reference branch: 259.576828s, peak 31,249 MiB, SHA-256 618995be4b8f74384608a0631e5cb73d878201499651b9e4866ec12f86bae2a2.
- First/middle/last sampled frames preserve gross identity in both branches with no obvious catastrophic deformation.
- Both branches retain pseudo-text on the silver name badge. This is a production-quality defect, not a runtime failure. The visual prompt compiler now makes badge/sign/label surfaces blank and defers readable typography to post-production.
- This batch does not select an image model and does not grant production acceptance.

Verdict: PASS_RUNTIME / AWAIT_OWNER_SCORING

Remaining blockers: owner motion-quality score; owner VoxCPM2 voice score; no full multi-shot video benchmark promotion until scored.
