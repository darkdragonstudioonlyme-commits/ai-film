from __future__ import annotations

import hashlib
import json
from typing import Any


class EditPlanError(ValueError):
    pass


def canonical_digest(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def compile_edit_plan(
    timing: dict[str, Any],
    shots: list[dict[str, Any]],
    *,
    selected_takes: dict[str, dict[str, Any]],
    dialogue_tracks: dict[str, dict[str, Any]],
    subtitle_tracks: dict[str, str],
    aspect: str,
    language: str,
) -> dict[str, Any]:
    if aspect not in {"9:16", "16:9"}:
        raise EditPlanError("unsupported aspect")
    if language not in {"en", "zh-CN", "vi"}:
        raise EditPlanError("unsupported language")
    shot_by_id = {row["shot_id"]: row for row in shots}
    if len(shot_by_id) != len(shots):
        raise EditPlanError("duplicate shot id")

    timeline_rows = timing.get("shots", [])
    cursor = 0.0
    segments = []
    blockers: list[str] = []
    for row in timeline_rows:
        shot_id = row["shot_id"]
        if shot_id not in shot_by_id:
            raise EditPlanError(f"timing references unknown shot: {shot_id}")
        duration = float(row["duration_sec"])
        start = cursor
        end = start + duration
        take = selected_takes.get(shot_id)
        if take is None:
            blockers.append(f"missing-selected-take:{shot_id}")
            video = None
        else:
            required = ("selection_revision", "take_id", "asset_id", "manifest_sha256")
            missing = [key for key in required if not take.get(key)]
            if missing:
                blockers.append(f"invalid-selected-take:{shot_id}:{','.join(missing)}")
            video = {
                "take_id": take.get("take_id"),
                "asset_id": take.get("asset_id"),
                "manifest_sha256": take.get("manifest_sha256"),
                "selection_revision": take.get("selection_revision"),
            }
        segments.append({
            "shot_id": shot_id,
            "start_sec": round(start, 6),
            "end_sec": round(end, 6),
            "duration_sec": duration,
            "video": video,
        })
        cursor = end

    cue_rows = []
    for cue in timing.get("dialogue_cues", []):
        dialogue_id = cue["dialogue_id"]
        shot_id = cue["shot_id"]
        if shot_id not in {row["shot_id"] for row in segments}:
            raise EditPlanError("dialogue cue references unknown timeline shot")
        shot_start = next(row["start_sec"] for row in segments if row["shot_id"] == shot_id)
        track = dialogue_tracks.get(dialogue_id)
        if track is None:
            blockers.append(f"missing-dialogue-audio:{dialogue_id}:{language}")
            audio = None
        else:
            if track.get("language") != language:
                blockers.append(f"dialogue-language-mismatch:{dialogue_id}")
            audio = {
                "asset_id": track.get("asset_id"),
                "sha256": track.get("sha256"),
                "duration_sec": track.get("duration_sec"),
            }
            if not audio["asset_id"] or not audio["sha256"]:
                blockers.append(f"invalid-dialogue-audio:{dialogue_id}")
            if audio["duration_sec"] is not None:
                budget = float(cue["end_offset_sec"]) - float(cue["start_offset_sec"])
                if float(audio["duration_sec"]) > budget + 1e-9:
                    blockers.append(f"dialogue-over-budget:{dialogue_id}")
        cue_rows.append({
            "dialogue_id": dialogue_id,
            "shot_id": shot_id,
            "start_sec": round(shot_start + float(cue["start_offset_sec"]), 6),
            "end_sec": round(shot_start + float(cue["end_offset_sec"]), 6),
            "audio": audio,
        })

    subtitle = subtitle_tracks.get(language)
    if not subtitle:
        blockers.append(f"missing-subtitle-track:{language}")

    plan_body = {
        "schema_version": 1,
        "aspect": aspect,
        "language": language,
        "duration_sec": round(cursor, 6),
        "segments": segments,
        "dialogue": cue_rows,
        "subtitle_path": subtitle,
        "blockers": sorted(set(blockers)),
        "render_authorized": False,
    }
    plan_body["plan_digest"] = canonical_digest(plan_body)
    plan_body["status"] = "READY_TO_RENDER" if not plan_body["blockers"] else "BLOCKED_MISSING_MEDIA"
    return plan_body
