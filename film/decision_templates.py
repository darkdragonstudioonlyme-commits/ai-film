from __future__ import annotations

from typing import Any


TEMPLATES = {
    "image_casting": {
        "stage": "image",
        "expected_models": ["z-image", "flux2-klein-4b"],
        "required_metrics": ["quality_overall", "usable", "elapsed_sec", "gpu_peak_memory_mb", "cost_usd"],
        "decision_scope": "casting_reference_model_evaluation",
    },
    "video_core": {
        "stage": "video",
        "expected_models": ["wan22-ti2v-5b", "wan22-i2v-14b", "ltx-2.5"],
        "required_metrics": ["quality_overall", "usable", "elapsed_sec", "gpu_peak_memory_mb", "cost_usd"],
        "decision_scope": "motion_model_evaluation",
    },
    "voice_multilingual": {
        "stage": "voice",
        "expected_models": ["voxcpm2"],
        "required_metrics": ["quality_overall", "usable", "elapsed_sec", "cost_usd"],
        "decision_scope": "multilingual_voice_evaluation",
    },
}


def get_template(name: str) -> dict[str, Any]:
    if name not in TEMPLATES:
        raise ValueError(f"unknown decision template: {name}")
    return dict(TEMPLATES[name])


def import_cost_rows(raw_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records = []
    for row in raw_rows:
        required = {"run_id","job_id","model_id","shot_id","status","elapsed_sec","cost_usd"}
        missing = sorted(required-set(row))
        if missing:
            raise ValueError(f"cost row missing fields: {missing}")
        records.append({
            "run_id": str(row["run_id"]),
            "job_id": str(row["job_id"]),
            "model_id": str(row["model_id"]),
            "shot_id": str(row["shot_id"]),
            "status": str(row["status"]),
            "elapsed_sec": float(row["elapsed_sec"]),
            "gpu_peak_memory_mb": None if row.get("gpu_peak_memory_mb") is None else float(row["gpu_peak_memory_mb"]),
            "cost_usd": float(row["cost_usd"]),
            "quality_overall": None if row.get("quality_overall") is None else float(row["quality_overall"]),
            "usable": row.get("usable"),
        })
    return records
