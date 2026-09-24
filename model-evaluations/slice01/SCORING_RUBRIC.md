# Slice01 Blind Model-Eval Scoring Rubric

Reviewers score only opaque blind_id samples. Do not inspect blind_map_private.json until all scores are locked.

Scale:
- 1 — unusable / severe defect
- 2 — major defect, unlikely to survive edit
- 3 — usable with visible compromise
- 4 — strong production candidate
- 5 — excellent for the target style
- blank — not applicable to this stage

Criteria:
1. identity_consistency — face/body/age/hair/character separation match casting and continuity.
2. style_quality — target photoreal or stylized-3D look is coherent and artifact-light.
3. prompt_adherence — action, location, costume/injury/prop and camera intent are represented.
4. motion_quality — video only: natural motion, anatomy and camera movement.
5. temporal_stability — video only: low flicker/drift across the clip.
6. framing — target aspect, safe composition and readable action.
7. overall — holistic production usefulness, not an arithmetic average.
8. usable — YES only if the take could enter an edit without regeneration.

Failure tags:
FACE_DRIFT, BODY_DRIFT, HAIR_DRIFT, AGE_DRIFT, COSTUME_DRIFT, LOCATION_DRIFT, BAD_HAND, BAD_MOTION, CAMERA_ERROR, LIP_SYNC_ERROR, VOICE_EMOTION_ERROR, TEMPORAL_FLICKER, LOW_REALISM, BAD_EDIT.

Selection discipline:
- License gate must pass before production selection.
- Compare quality on the same shot/style population, then elapsed time, peak VRAM, failure/OOM rate and rental cost.
- Do not choose from one hero sample. Use the fixed core population and stability profile for finalists.
- Record ties and uncertainty; do not manufacture a winner.
