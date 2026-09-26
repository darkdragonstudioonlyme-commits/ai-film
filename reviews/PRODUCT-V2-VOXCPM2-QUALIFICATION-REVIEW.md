# PRODUCT V2 — VoxCPM2 A40 qualification + blind materialization review

VERDICT: PASS FOR EVIDENCE MERGE

Blind image materialization:
- 8/8 neutral blind-ID PNG copies exist on Pod under /workspace/artifacts/blind-comparison;
- every neutral copy matched canonical byte count and asset SHA-256;
- Pod-local neutral manifest SHA-256 is 2dbc18d0f9ebc56024980b864a7fc27d6633a18ed9741049f851404512fe2728;
- public packet contains no model/job/revision identity; scores remain blank and no winner is authorized.

VoxCPM2 qualification:
- exact model: openbmb/VoxCPM2 @ 32279effe8c19989596f05d353d1447f51d9e915;
- package: voxcpm==2.0.3;
- model snapshot: 7 required files / 4.620033 GiB;
- request: voxreq_7f50b3325b6132e8, EN, seed 41001, Voice Design only;
- reference_audio=null and voice cloning disabled;
- PASS_RUNTIME on RunPod A40;
- peak VRAM 5,827 MiB;
- inference 3.452767s; runner elapsed 31.527109s;
- output 3.04s / 48 kHz, fitting the 3.5s cue;
- WAV SHA-256 f562abbb391460d4cda9f75c0930bfe8ccb603257fd971b6a8a19a33544d3940;
- measured compute cost USD 0.004291;
- raw evidence SHA-256 1fcda9770d3a4c9ef30a5362302cd32608f36462ad2bf166f50c8b7264aa69de.

Boundary:
- resource admission is ready at required 6 GiB + 4 GiB reserve;
- quality/cross-language identity are NOT_EVALUATED;
- formal fixed packet has 11 requests remaining;
- smoke images and qualification WAV are not production-accepted;
- no binary media is committed.
