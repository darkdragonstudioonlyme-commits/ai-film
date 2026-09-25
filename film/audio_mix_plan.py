from __future__ import annotations

import hashlib
import json
from typing import Any

from .audio_cues import validate_cue_sheet


class AudioMixPlanError(ValueError):
    pass


LANGUAGES = {"en", "zh-CN", "vi"}


def canonical_digest(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _valid_sha(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def compile_audio_mix_plan(
    timing: dict[str, Any],
    shots: list[dict[str, Any]],
    cue_sheet: dict[str, Any],
    *,
    language: str,
    dialogue_assets: dict[str, dict[str, Any]],
    target: dict[str, Any],
) -> dict[str, Any]:
    if language not in LANGUAGES:
        raise AudioMixPlanError(f"unsupported language: {language}")
    total_duration = sum(float(row["duration_sec"]) for row in timing.get("shots", []))
    if abs(total_duration - 75.0) > 1e-9:
        raise AudioMixPlanError("slice01 timing must remain 75 seconds")
    validated_cues = validate_cue_sheet(cue_sheet, total_duration_sec=total_duration)
    shot_by_id = {row["shot_id"]: row for row in shots}

    shot_starts: dict[str, float] = {}
    cursor = 0.0
    for row in timing.get("shots", []):
        shot_starts[row["shot_id"]] = cursor
        cursor += float(row["duration_sec"])

    dialogue_rows = []
    blockers = list(validated_cues["blockers"])
    for cue in timing.get("dialogue_cues", []):
        dialogue_id = cue["dialogue_id"]
        shot_id = cue["shot_id"]
        shot = shot_by_id.get(shot_id)
        if shot is None or shot.get("dialogue_id") != dialogue_id:
            raise AudioMixPlanError(f"dialogue timing mismatch: {dialogue_id}")
        asset = dialogue_assets.get(dialogue_id)
        normalized_asset = None
        if asset is None:
            blockers.append(f"missing-final-dialogue:{dialogue_id}:{language}")
        else:
            if asset.get("language") != language:
                blockers.append(f"dialogue-language-mismatch:{dialogue_id}:{language}")
            for field in ("asset_id", "sha256", "manifest_sha256", "duration_sec"):
                if asset.get(field) in (None, ""):
                    blockers.append(f"dialogue-asset-missing-field:{dialogue_id}:{field}")
            if asset.get("sha256") and not _valid_sha(asset["sha256"]):
                blockers.append(f"dialogue-invalid-sha:{dialogue_id}")
            if asset.get("manifest_sha256") and not _valid_sha(asset["manifest_sha256"]):
                blockers.append(f"dialogue-invalid-manifest-sha:{dialogue_id}")
            budget = float(cue["end_offset_sec"]) - float(cue["start_offset_sec"])
            if asset.get("duration_sec") is not None and float(asset["duration_sec"]) > budget + 1e-9:
                blockers.append(f"dialogue-over-budget:{dialogue_id}")
            normalized_asset = {
                "asset_id": asset.get("asset_id"),
                "sha256": asset.get("sha256"),
                "manifest_sha256": asset.get("manifest_sha256"),
                "duration_sec": asset.get("duration_sec"),
            }
        dialogue_rows.append({
            "dialogue_id": dialogue_id,
            "shot_id": shot_id,
            "start_sec": round(shot_starts[shot_id] + float(cue["start_offset_sec"]), 6),
            "end_sec": round(shot_starts[shot_id] + float(cue["end_offset_sec"]), 6),
            "asset": normalized_asset,
        })

    for required in ("sample_rate_hz", "channels", "format"):
        if required not in target:
            raise AudioMixPlanError(f"mix target missing {required}")

    plan = {
        "schema_version": 1,
        "language": language,
        "duration_sec": round(total_duration, 6),
        "dialogue": dialogue_rows,
        "cues": validated_cues["cues"],
        "target": {
            "sample_rate_hz": int(target["sample_rate_hz"]),
            "channels": int(target["channels"]),
            "format": str(target["format"]),
        },
        "blockers": sorted(set(blockers)),
        "execution_permitted": False,
    }
    plan["status"] = "READY_TO_MIX" if not plan["blockers"] else "BLOCKED_MISSING_ASSETS_OR_RIGHTS"
    plan["plan_digest"] = canonical_digest(plan)
    return plan
