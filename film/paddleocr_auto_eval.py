from __future__ import annotations
import re
from typing import Any

from .auto_eval import AutoEvalError

def evaluate_ocr_payloads(
    payloads: list[dict[str, Any]],
    *,
    allowed_text_regex: list[str] | None = None,
    confidence_threshold: float = 0.75,
) -> dict[str, Any]:
    if not isinstance(payloads, list) or not payloads:
        raise AutoEvalError("OCR frame payloads required")
    patterns = [re.compile(x, re.I) for x in (allowed_text_regex or [])]
    detections = []
    for frame_index, payload in enumerate(payloads):
        res = payload.get("res", payload)
        texts = res.get("rec_texts", [])
        scores = res.get("rec_scores", [])
        if not isinstance(texts, list) or not isinstance(scores, list) or len(texts) != len(scores):
            raise AutoEvalError("OCR payload text/score mismatch")
        for text, score in zip(texts, scores):
            if not isinstance(text, str):
                continue
            try:
                conf = float(score)
            except (TypeError, ValueError):
                continue
            clean = text.strip()
            if not clean or conf < confidence_threshold:
                continue
            allowed = any(p.search(clean) for p in patterns)
            detections.append({
                "frame_index": frame_index,
                "text": clean,
                "confidence": round(conf, 6),
                "allowed": allowed,
            })
    unexpected = [d for d in detections if not d["allowed"] and len(d["text"]) >= 2]
    penalty = min(100.0, 25.0 * len(unexpected))
    score = round(100.0 - penalty, 6)
    tags = ["UNMOTIVATED_READABLE_TEXT"] if unexpected else []
    return {
        "text_artifact_free": score,
        "hard_fail_tags": tags,
        "detections": detections,
        "unexpected": unexpected,
    }

def build_receipt(
    *,
    asset_id: str,
    payloads: list[dict[str, Any]],
    allowed_text_regex: list[str] | None = None,
) -> dict[str, Any]:
    result = evaluate_ocr_payloads(payloads, allowed_text_regex=allowed_text_regex)
    return {
        "schema_version": 1,
        "evaluator_id": "paddleocr-text-artifact",
        "asset_id": asset_id,
        "status": "PASS_MODEL_EVAL",
        "metrics": {"text_artifact_free": result["text_artifact_free"]},
        "hard_fail_tags": result["hard_fail_tags"],
        "evidence": {"detections": result["detections"], "unexpected": result["unexpected"]},
        "production_acceptance": False,
    }
