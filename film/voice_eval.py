from __future__ import annotations

import hashlib
import json
from typing import Any

from .blind_scoring import BlindScoreError, ScoreSchema, validate_complete_scores, unblind_and_rank


class VoiceEvalError(ValueError):
    pass


def canonical_digest(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def compile_voxcpm2_requests(
    config: dict[str, Any],
    packet: dict[str, Any],
) -> list[dict[str, Any]]:
    if config.get("mode") != "voice_design":
        raise VoiceEvalError("only voice_design mode is allowed")
    if config.get("reference_audio_allowed") or config.get("voice_cloning_allowed"):
        raise VoiceEvalError("reference audio / cloning must remain disabled")
    model = config["model"]
    if model["model_id"] != "voxcpm2":
        raise VoiceEvalError("unexpected model id")

    rows: list[dict[str, Any]] = []
    for sample in packet.get("samples", []):
        if sample.get("reference_audio") is not None:
            raise VoiceEvalError("sample contains reference audio")
        if sample.get("mode") != "voice_design":
            raise VoiceEvalError("sample mode is not voice_design")
        source = {
            "schema_version": 1,
            "evaluation_id": config["evaluation_id"],
            "blind_id": sample["blind_id"],
            "voice_group": sample["voice_group"],
            "model": {
                "model_id": model["model_id"],
                "repo": model["repo"],
                "revision": model["revision"],
                "package": model["package"],
                "sample_rate_hz": model["sample_rate_hz"],
            },
            "mode": "voice_design",
            "language": sample["language"],
            "dialogue_id": sample["dialogue_id"],
            "target_text": sample["target_text"],
            "voice_design_description": sample["voice_design_description"],
            "model_input_text": sample["model_input_text"],
            "seed": int(sample["seed"]),
            "cfg_value": float(sample["cfg_value"]),
            "inference_timesteps": int(sample["inference_timesteps"]),
            "reference_audio": None,
            "cue_budget_sec": float(sample["cue_budget_sec"]),
            "execution_permitted": False,
        }
        request_digest = canonical_digest(source)
        rows.append(
            {
                **source,
                "request_id": "voxreq_" + request_digest[:16],
                "request_digest": request_digest,
            }
        )
    if len(rows) != 12:
        raise VoiceEvalError(f"expected 12 requests, got {len(rows)}")
    if len({row["blind_id"] for row in rows}) != len(rows):
        raise VoiceEvalError("duplicate blind id")
    return rows


def validate_voice_output_manifest(
    request: dict[str, Any],
    manifest: dict[str, Any],
) -> dict[str, Any]:
    required = {
        "request_digest",
        "blind_id",
        "audio_sha256",
        "sample_rate_hz",
        "duration_sec",
        "bytes",
    }
    missing = required - set(manifest)
    if missing:
        raise VoiceEvalError(f"voice output manifest missing fields: {sorted(missing)}")
    if manifest["request_digest"] != request["request_digest"]:
        raise VoiceEvalError("request digest mismatch")
    if manifest["blind_id"] != request["blind_id"]:
        raise VoiceEvalError("blind id mismatch")
    if not isinstance(manifest["audio_sha256"], str) or len(manifest["audio_sha256"]) != 64:
        raise VoiceEvalError("invalid audio sha256")
    if int(manifest["sample_rate_hz"]) != int(request["model"]["sample_rate_hz"]):
        raise VoiceEvalError("sample rate mismatch")
    duration = float(manifest["duration_sec"])
    if duration <= 0:
        raise VoiceEvalError("invalid audio duration")
    if int(manifest["bytes"]) <= 0:
        raise VoiceEvalError("invalid audio bytes")
    return {
        **manifest,
        "cue_fit": duration <= float(request["cue_budget_sec"]),
    }


VOICE_SCORE_SCHEMA = ScoreSchema(
    criteria=(
        "intelligibility",
        "character_match",
        "cross_language_identity",
        "between_character_separation",
        "prosody",
        "artifact_free",
        "overall",
    )
)


def rank_voice_scores(
    public_items: list[dict[str, Any]],
    score_rows: list[dict[str, str]],
    private_mapping: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    validated = validate_complete_scores(public_items, score_rows, VOICE_SCORE_SCHEMA)
    return unblind_and_rank(
        validated,
        private_mapping,
        group_fields=("voice_group", "character_id"),
    )
