# Casting reference acceptance

Status: contract only; no generated reference image is approved by this file.

For each character and style, generate the four required slots: face front, face three-quarter, full-body neutral, and neutral-expression anchor.

Blind human review scores 1–5:
- identity_match: fits the intended character description without accidentally resembling the other cast member;
- within_character_consistency: face/body/age/hair stay coherent across the four slots;
- between_character_separation: An and Linh remain clearly distinguishable;
- style_quality: coherent photoreal or stylized-3D target;
- anatomy_artifact_free: hands/body/face free of obvious generation defects;
- overall: usable as a production reference set.

Provisional human gate: every identity/consistency/separation/style/overall score >=4 and zero severe failure tags. This is a human rubric, not a face-embedding threshold.

Embedding thresholds remain uncalibrated until the embedding model and first accepted casting population exist. The first metric requirement is relative: within-character median similarity must exceed the maximum cross-character similarity. Record the chosen embedding model/version before promoting an absolute threshold.
