# Milestones v2

- [x] M0 — practical host ready, workflow v2 active
- [x] M1 — original 60–90s screenplay + shot list + executable film schemas
- [ ] M2 — casting/look/voice references approved
  - [x] image comparison scored by owner
  - [x] 12/12 voice packet generated + AUTO_EVAL qualified/scored
  - [ ] An/Linh appearance + voice approved
- [ ] M3 — benchmark keyframes meet identity/style threshold
- [ ] M4 — motion clips produced and scored
  - [x] staged video runtime smoke admitted by measured VRAM/runtime evidence
  - [ ] benchmark motion clips generated + multi-model AUTO_EVAL scored
- [ ] M5 — EN/ZH/VI voice + selected lip-sync
- [ ] M6 — first edited 9:16 film exported; 16:9 path verified
- [ ] M7 — measured quality experiment improves a film KPI

Current M4 admission evidence: Wan2.2 TI2V-5B technical smoke PASS on A40 (17 frames / 5 steps), peak 31,883 MiB, 266.384s, 24 fps output. Balanced quality-motion probe: 2/2 runtime PASS at 25 frames / 8 steps, 704×1280 @24fps, peak 31,249 MiB; owner quality scoring pending.
Platform capability evidence: Tang Chang'an and Belle Époque Paris world profiles each completed generated photoreal image → Wan2.2 motion technical proof; this proves pipeline coverage, not production quality or historical-accuracy approval.

Current M2 evidence: FLUX2 and Z-Image passed fixed 4-job 1024 A40 smoke; owner scored all 8 comparison images on a 0–8 scale and the models tied, with photoreal preferred over stylized in this round. VoxCPM2 generated 12/12 fixed EN/ZH/VI samples with 10/12 cue-fit; voice quality scoring/approval remains open.
Progress is checklist-based. Infrastructure work counts only when it removes a blocker for a milestone.
North-star metrics: seconds of finished film/week, usable-take ratio, human quality score, cost/finished-second, time-to-first-clip.

Owner review policy: short-take quality gates use multi-model automatic evaluation; owner 0–8 review begins at longform rough cut/final cut and is later used to calibrate evaluator weights.

Current AUTO_EVAL evidence: Whisper v2 12/12 voice complete (10 shortlist / 2 retry / 0 reject); v1 false negatives are retained for audit. Qwen3-VL + PaddleOCR video 4/4 complete; VBench pending due existing A40 host capacity. Short-take owner review is not required.
