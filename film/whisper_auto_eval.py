from __future__ import annotations
import re
import unicodedata
from typing import Any

from .auto_eval import AutoEvalError

LANG_MAP = {"en": "en", "vi": "vi", "zh-CN": "zh", "zh": "zh"}

def _norm(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).casefold()
    text = re.sub(r"[^\w\s\u3400-\u9fff]", " ", text, flags=re.UNICODE)
    return " ".join(text.split())

def _lev(a: list[str], b: list[str]) -> int:
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i]
        for j, y in enumerate(b, 1):
            cur.append(min(cur[-1] + 1, prev[j] + 1, prev[j - 1] + (x != y)))
        prev = cur
    return prev[-1]

def text_match_score(target: str, transcript: str, language: str) -> float:
    target_n = _norm(target)
    transcript_n = _norm(transcript)
    if not target_n:
        raise AutoEvalError("Whisper target text empty")
    if LANG_MAP.get(language, language) == "zh":
        a = [c for c in target_n if not c.isspace()]
        b = [c for c in transcript_n if not c.isspace()]
    else:
        a = target_n.split()
        b = transcript_n.split()
    dist = _lev(a, b)
    return round(max(0.0, 1.0 - dist / max(1, len(a))) * 100.0, 6)

def build_whisper_receipt(
    *,
    asset_id: str,
    target_text: str,
    expected_language: str,
    transcript: str,
    detected_language: str,
    detected_probabilities: dict[str, float],
    model_sha256: str,
) -> dict[str, Any]:
    expected = LANG_MAP.get(expected_language, expected_language)
    match = text_match_score(target_text, transcript, expected_language)
    probs = {str(k): float(v) for k, v in detected_probabilities.items()}
    expected_prob = max(0.0, min(1.0, float(probs.get(expected, 0.0))))
    language_match = round(expected_prob * 100.0, 6)
    tags = []
    if detected_language != expected and expected_prob < 0.20:
        tags.append("WRONG_LANGUAGE")
    if match < 35.0:
        tags.append("SEVERE_TEXT_MISMATCH")
    return {
        "schema_version": 1,
        "evaluator_id": "whisper-turbo-asr",
        "asset_id": asset_id,
        "status": "PASS_MODEL_EVAL",
        "metrics": {"asr_text_match": match, "language_match": language_match},
        "hard_fail_tags": tags,
        "evidence": {
            "target_text": target_text,
            "transcript": transcript,
            "expected_language": expected,
            "detected_language": detected_language,
            "detected_language_probability": round(expected_prob, 6),
            "model_name": "turbo",
            "model_sha256": model_sha256,
        },
        "production_acceptance": False,
    }
