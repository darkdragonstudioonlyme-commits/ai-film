from __future__ import annotations

from copy import deepcopy
from typing import Any


class QCError(ValueError):
    pass


FAILURE_TAGS = {
    "FACE_DRIFT",
    "BODY_DRIFT",
    "HAIR_DRIFT",
    "AGE_DRIFT",
    "COSTUME_DRIFT",
    "LOCATION_DRIFT",
    "BAD_HAND",
    "BAD_MOTION",
    "CAMERA_ERROR",
    "LIP_SYNC_ERROR",
    "VOICE_EMOTION_ERROR",
    "TEMPORAL_FLICKER",
    "LOW_REALISM",
    "BAD_EDIT",
}

SEVERE_TAGS = {
    "FACE_DRIFT",
    "BODY_DRIFT",
    "COSTUME_DRIFT",
    "BAD_MOTION",
    "LIP_SYNC_ERROR",
    "TEMPORAL_FLICKER",
    "BAD_EDIT",
}

DEFAULT_CRITERIA = (
    "story_comprehension",
    "visual_quality",
    "character_consistency",
    "motion_quality",
    "voice_quality",
    "lip_sync",
    "edit_quality",
    "continuity",
)


def _score(value: Any, name: str) -> float:
    try:
        score = float(value)
    except (TypeError, ValueError) as exc:
        raise QCError(f"invalid score: {name}") from exc
    if not 1.0 <= score <= 5.0:
        raise QCError(f"score out of range: {name}")
    return score


def validate_qc_record(record: dict[str, Any]) -> dict[str, Any]:
    for key in ("qc_id", "asset_id", "manifest_sha256", "scope", "scores", "failure_tags"):
        if key not in record:
            raise QCError(f"missing QC field: {key}")
    if not isinstance(record["qc_id"], str) or not record["qc_id"]:
        raise QCError("invalid qc_id")
    if not isinstance(record["asset_id"], str) or not record["asset_id"]:
        raise QCError("invalid asset_id")
    manifest = record["manifest_sha256"]
    if not isinstance(manifest, str) or len(manifest) != 64:
        raise QCError("invalid manifest_sha256")
    scores = record["scores"]
    if not isinstance(scores, dict) or not scores:
        raise QCError("scores must be a non-empty mapping")
    normalized_scores = {name: _score(value, name) for name, value in scores.items()}
    tags = record["failure_tags"]
    if not isinstance(tags, list):
        raise QCError("failure_tags must be a list")
    unknown = sorted(set(tags) - FAILURE_TAGS)
    if unknown:
        raise QCError(f"unknown failure tags: {unknown}")
    out = deepcopy(record)
    out["scores"] = normalized_scores
    out["failure_tags"] = sorted(set(tags))
    out.setdefault("reviewer", "UNSPECIFIED")
    out.setdefault("population_id", None)
    return out


def acceptance_decision(
    record: dict[str, Any],
    *,
    required_scores: dict[str, float],
    severe_tags: set[str] | None = None,
) -> dict[str, Any]:
    normalized = validate_qc_record(record)
    severe = severe_tags or SEVERE_TAGS
    blockers: list[str] = []
    for criterion, threshold in required_scores.items():
        actual = normalized["scores"].get(criterion)
        if actual is None:
            blockers.append(f"missing-score:{criterion}")
        elif actual < float(threshold):
            blockers.append(f"below-threshold:{criterion}:{actual}<{threshold}")
    for tag in normalized["failure_tags"]:
        if tag in severe:
            blockers.append(f"severe-failure:{tag}")
    return {
        "schema_version": 1,
        "qc_id": normalized["qc_id"],
        "asset_id": normalized["asset_id"],
        "manifest_sha256": normalized["manifest_sha256"],
        "accepted": not blockers,
        "blockers": blockers,
        "selection_authorized": False,
    }


def validate_experiment(experiment: dict[str, Any]) -> dict[str, Any]:
    required = {
        "experiment_id",
        "hypothesis",
        "changed_variable",
        "eval_population_id",
        "sample_count",
        "baseline_metrics",
        "candidate_metrics",
        "regressions",
    }
    missing = sorted(required - set(experiment))
    if missing:
        raise QCError(f"experiment missing fields: {missing}")
    if int(experiment["sample_count"]) <= 0:
        raise QCError("sample_count must be positive")
    if not str(experiment["hypothesis"]).strip():
        raise QCError("hypothesis required")
    if not str(experiment["changed_variable"]).strip():
        raise QCError("changed_variable required")
    if not isinstance(experiment["baseline_metrics"], dict) or not isinstance(experiment["candidate_metrics"], dict):
        raise QCError("metrics must be mappings")
    if set(experiment["baseline_metrics"]) != set(experiment["candidate_metrics"]):
        raise QCError("baseline/candidate metric sets differ")
    if not isinstance(experiment["regressions"], list):
        raise QCError("regressions must be a list")
    out = deepcopy(experiment)
    out.setdefault("decision", "PENDING")
    if out["decision"] not in {"PENDING", "KEEP", "REVERT"}:
        raise QCError("invalid experiment decision")
    return out


def experiment_delta(experiment: dict[str, Any]) -> dict[str, Any]:
    normalized = validate_experiment(experiment)
    deltas = {
        name: float(normalized["candidate_metrics"][name]) - float(normalized["baseline_metrics"][name])
        for name in sorted(normalized["baseline_metrics"])
    }
    return {
        "schema_version": 1,
        "experiment_id": normalized["experiment_id"],
        "sample_count": normalized["sample_count"],
        "deltas": deltas,
        "regressions": list(normalized["regressions"]),
        "promotion_authorized": normalized["decision"] == "KEEP" and not normalized["regressions"],
    }
