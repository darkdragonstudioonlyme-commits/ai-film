from __future__ import annotations
from typing import Any

from .auto_eval import AutoEvalError

DIMENSIONS = (
    "subject_consistency",
    "background_consistency",
    "motion_smoothness",
    "dynamic_degree",
    "aesthetic_quality",
    "imaging_quality",
)

def parse_vbench_results(value: dict[str, Any]) -> dict[str, float]:
    if not isinstance(value, dict):
        raise AutoEvalError("VBench results must be object")
    out = {}
    for dim in DIMENSIONS:
        if dim not in value:
            raise AutoEvalError(f"VBench missing dimension: {dim}")
        raw = value[dim]
        score = raw[0] if isinstance(raw, (list, tuple)) and raw else raw
        if isinstance(score, bool):
            raise AutoEvalError(f"VBench invalid dimension score: {dim}")
        try:
            score = float(score)
        except (TypeError, ValueError) as exc:
            raise AutoEvalError(f"VBench invalid dimension score: {dim}") from exc
        if not 0 <= score <= 1.0:
            raise AutoEvalError(f"VBench dimension out of 0-1 range: {dim}")
        out[dim] = round(score * 100.0, 6)
    return out

def build_receipt(*, asset_id: str, results: dict[str, Any], code_revision: str) -> dict[str, Any]:
    metrics = parse_vbench_results(results)
    return {
        "schema_version": 1,
        "evaluator_id": "vbench-video-v0.1.5",
        "asset_id": asset_id,
        "status": "PASS_MODEL_EVAL",
        "metrics": metrics,
        "hard_fail_tags": [],
        "evidence": {
            "code_repo": "Vchitect/VBench",
            "code_revision": code_revision,
            "raw_dimensions": list(DIMENSIONS),
        },
        "production_acceptance": False,
    }
