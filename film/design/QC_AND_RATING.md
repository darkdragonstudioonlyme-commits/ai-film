# QC and Rating

Automatic checks begin with schema completeness, manifest integrity, fixed seed identity and expected continuity state.
Rendered-media checks will add identity similarity, costume/injury agreement, temporal flicker and lip-sync when GPU outputs exist.
Human review uses 1–5 scores for story comprehension, visual quality, character consistency, motion, voice and lip-sync.
Failure tags reuse the project taxonomy: FACE_DRIFT, COSTUME_DRIFT, BAD_HAND, BAD_MOTION, LIP_SYNC_ERROR, TEMPORAL_FLICKER and related tags.
Acceptance decisions bind the exact asset manifest; a high-scoring isolated frame cannot approve a broken sequence.
