# Batch 013 — selective lip-sync and audio planning

T-041 lip-sync:
- only dialogue rows explicitly marked mouth_visible produce requests;
- slice01 currently plans dlg_001/dlg_002/dlg_003 and skips dlg_004 because profile/distance makes mouth visibility low-confidence;
- each request binds exact final video/audio identities when available;
- missing final media remains a blocker; CPU previs audio is explicitly not production lip-sync input;
- backend candidates remain LatentSync/MuseTalk evaluation candidates and execution_permitted is always false.

T-042 ambience/SFX/music cue sheet:
- all cues are bounded within the 75s timeline;
- each final-required cue needs a bound asset plus CLEARED rights and evidence reference;
- current rain/station/SFX/music cues are intentionally UNKNOWN/PENDING and therefore blocked;
- no music or SFX generation occurs.

T-043 audio mix plan:
- compiles final dialogue placements plus ambience/SFX/music cue placements;
- validates language, cue budget, exact asset/manifest SHA identities and target audio format;
- current EN/ZH/VI plans remain blocked until final assets/rights exist;
- a complete synthetic plan can become READY_TO_MIX but never grants execution authority.
