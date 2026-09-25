# Batch 014 — screenplay, localization and aspect planning

T-044 screenplay:
- slice01 now has machine-readable screenplay JSON with one 75s scene, six contiguous beats and four stable dialogue IDs;
- the source is bound to project.json by SHA-256 and to source-original in the rights register;
- original/adaptation rights status is validated; shot dialogue IDs/speakers must match screenplay.

T-045 localization:
- one bundle covers EN master plus ZH/VI using stable dialogue IDs;
- EN/VI timing measurements are bound to PREVIS_AUDIO evidence hash and explicitly marked PREVIS_MEASURED;
- ZH timing stays NOT_MEASURED until approved synthesis/model-eval exists;
- missing translation, missing evidence and over-budget speech are blockers rather than silently accepted.

T-046 reframe:
- every shot has explicit 9:16→16:9 strategy, horizontal intent and protected subjects;
- wide/two-shot compositions rerender from structured shot spec;
- selected medium/close shots may outpaint only when an exact 9:16 master asset exists, otherwise deterministically fall back to rerender;
- crop-only widening is rejected and no render authority is granted.
