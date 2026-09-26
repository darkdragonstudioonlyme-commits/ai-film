from __future__ import annotations

from typing import Any


class ScoredMediaPromotionError(ValueError):
    pass


def _require_owner_summary(summary: dict[str, Any]) -> None:
    if not isinstance(summary, dict) or summary.get("schema_version") != 1:
        raise ScoredMediaPromotionError("unsupported owner summary schema")
    if summary.get("score_set_complete") is not True:
        raise ScoredMediaPromotionError("owner score set is incomplete")
    if summary.get("quality_status") != "OWNER_SCORED_NOT_PRODUCTION_ACCEPTED":
        raise ScoredMediaPromotionError("owner summary quality status is not promotable")
    if summary.get("production_acceptance") is not False:
        raise ScoredMediaPromotionError("owner summary must not grant production acceptance")
    scale = summary.get("scale")
    if scale != {"min": 0, "max": 8}:
        raise ScoredMediaPromotionError("owner summary scale must be 0-8")


def _motion_decision(summary: dict[str, Any]) -> dict[str, Any]:
    motion = summary.get("motion")
    if not isinstance(motion, dict) or motion.get("sample_count") != 2:
        raise ScoredMediaPromotionError("owner motion summary must contain exactly two samples")
    rows = motion.get("rows")
    if not isinstance(rows, list) or len(rows) != 2:
        raise ScoredMediaPromotionError("owner motion rows missing")
    normalized = []
    seen = set()
    for row in rows:
        item_id = row.get("id")
        source = row.get("reference_model_id")
        score = row.get("score")
        if not isinstance(item_id, str) or not item_id or item_id in seen:
            raise ScoredMediaPromotionError("invalid/duplicate motion id")
        seen.add(item_id)
        if not isinstance(source, str) or not source.strip():
            raise ScoredMediaPromotionError("motion reference model missing")
        if isinstance(score, bool) or not isinstance(score, int) or not 0 <= score <= 8:
            raise ScoredMediaPromotionError("motion score out of range")
        normalized.append({
            "id": item_id,
            "reference_model_id": source.strip(),
            "score": score,
            "notes": str(row.get("notes") or "").strip(),
        })
    normalized.sort(key=lambda r: (-r["score"], r["id"]))
    top = normalized[0]
    second = normalized[1]
    if top["score"] == second["score"]:
        return {
            "status": "BLOCKED_MOTION_SCORE_TIE",
            "selected_reference_model_id": None,
            "selected_motion_id": None,
            "rows": normalized,
            "selection_authorized": False,
        }
    return {
        "status": "READY_UNIQUE_OWNER_TOP_SCORE",
        "selected_reference_model_id": top["reference_model_id"],
        "selected_motion_id": top["id"],
        "selected_score": top["score"],
        "runner_up_score": second["score"],
        "rows": normalized,
        "selection_authorized": True,
    }


def build_scored_benchmark_plan(
    summary: dict[str, Any],
    *,
    benchmark_shot_ids: list[str],
) -> dict[str, Any]:
    _require_owner_summary(summary)
    if (
        not isinstance(benchmark_shot_ids, list)
        or not benchmark_shot_ids
        or any(not isinstance(x, str) or not x.strip() for x in benchmark_shot_ids)
        or len(benchmark_shot_ids) != len(set(benchmark_shot_ids))
    ):
        raise ScoredMediaPromotionError("benchmark_shot_ids must be unique non-empty strings")

    voice = summary.get("voice")
    if not isinstance(voice, dict) or voice.get("sample_count") != 12:
        raise ScoredMediaPromotionError("owner voice summary must contain 12 samples")
    overall_mean = voice.get("overall_mean")
    if not isinstance(overall_mean, (int, float)) or not 0 <= float(overall_mean) <= 8:
        raise ScoredMediaPromotionError("invalid voice overall mean")
    for group_name in ("by_character", "by_language"):
        groups = voice.get(group_name)
        if not isinstance(groups, dict) or not groups:
            raise ScoredMediaPromotionError(f"voice {group_name} summary missing")

    motion = _motion_decision(summary)
    blocked = motion["status"] != "READY_UNIQUE_OWNER_TOP_SCORE"
    return {
        "schema_version": 1,
        "status": "BLOCKED_OWNER_MOTION_TIE" if blocked else "READY_FOR_MULTI_SHOT_BENCHMARK_CONFIGURATION",
        "owner_review_id": summary.get("review_id"),
        "owner_score_scale": {"min": 0, "max": 8},
        "benchmark_shot_ids": list(benchmark_shot_ids),
        "voice": {
            "status": "OWNER_SCORED_NO_AUTOMATIC_ACCEPTANCE",
            "sample_count": 12,
            "overall_mean": round(float(overall_mean), 6),
            "by_character": voice["by_character"],
            "by_language": voice["by_language"],
            "production_acceptance": False,
        },
        "motion": motion,
        "quality_selection_basis": "owner 0-8 scores only; unique top motion score required",
        "selection_authorized": not blocked,
        "production_acceptance": False,
        "publish_authority": False,
        "new_resource_creation_authorized": False,
    }