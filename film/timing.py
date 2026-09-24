from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

LANGUAGES = ("en", "zh-CN", "vi")


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _shot_index(shots: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for shot in shots:
        shot_id = shot.get("shot_id")
        if not isinstance(shot_id, str) or not shot_id:
            raise ValueError("shot missing shot_id")
        if shot_id in result:
            raise ValueError(f"duplicate shot_id: {shot_id}")
        result[shot_id] = shot
    return result


def validate_timing(
    timing: dict[str, Any],
    shots: list[dict[str, Any]],
    *,
    min_total_sec: float = 60.0,
    max_total_sec: float = 90.0,
) -> dict[str, Any]:
    shot_by_id = _shot_index(shots)
    rows = timing.get("shots")
    cues = timing.get("dialogue_cues")
    if not isinstance(rows, list) or not rows:
        raise ValueError("timing.shots must be non-empty list")
    if not isinstance(cues, list):
        raise ValueError("timing.dialogue_cues must be list")

    seen: set[str] = set()
    timeline = []
    cursor = 0.0
    duration_by_shot: dict[str, float] = {}
    for row in rows:
        shot_id = row.get("shot_id")
        if shot_id not in shot_by_id:
            raise ValueError(f"unknown timing shot: {shot_id}")
        if shot_id in seen:
            raise ValueError(f"duplicate timing shot: {shot_id}")
        seen.add(shot_id)
        duration = float(row.get("duration_sec", 0))
        if duration <= 0:
            raise ValueError(f"non-positive duration: {shot_id}")
        start = cursor
        end = start + duration
        timeline.append(
            {
                "shot_id": shot_id,
                "start_sec": round(start, 6),
                "end_sec": round(end, 6),
                "duration_sec": duration,
            }
        )
        duration_by_shot[shot_id] = duration
        cursor = end

    if seen != set(shot_by_id):
        missing = sorted(set(shot_by_id) - seen)
        extra = sorted(seen - set(shot_by_id))
        raise ValueError(f"timing population mismatch missing={missing} extra={extra}")
    if not (min_total_sec <= cursor <= max_total_sec):
        raise ValueError(f"total duration {cursor} outside [{min_total_sec}, {max_total_sec}]")

    cue_by_dialogue: dict[str, dict[str, Any]] = {}
    for cue in cues:
        dialogue_id = cue.get("dialogue_id")
        shot_id = cue.get("shot_id")
        if not isinstance(dialogue_id, str) or not dialogue_id:
            raise ValueError("cue missing dialogue_id")
        if dialogue_id in cue_by_dialogue:
            raise ValueError(f"duplicate dialogue cue: {dialogue_id}")
        if shot_id not in duration_by_shot:
            raise ValueError(f"cue references unknown shot: {shot_id}")
        shot = shot_by_id[shot_id]
        if shot.get("dialogue_id") != dialogue_id:
            raise ValueError(f"cue dialogue mismatch: {dialogue_id}")
        dialogue = shot.get("dialogue")
        if not isinstance(dialogue, dict) or set(dialogue) != set(LANGUAGES):
            raise ValueError(f"dialogue language contract: {dialogue_id}")
        start = float(cue.get("start_offset_sec", -1))
        end = float(cue.get("end_offset_sec", -1))
        if start < 0 or end <= start or end > duration_by_shot[shot_id]:
            raise ValueError(f"cue outside shot: {dialogue_id}")
        cue_by_dialogue[dialogue_id] = deepcopy(cue)

    expected_dialogue = {
        shot["dialogue_id"]
        for shot in shots
        if shot.get("dialogue_id")
    }
    if set(cue_by_dialogue) != expected_dialogue:
        raise ValueError(
            f"dialogue cue population mismatch expected={sorted(expected_dialogue)} actual={sorted(cue_by_dialogue)}"
        )

    start_by_shot = {row["shot_id"]: row["start_sec"] for row in timeline}
    global_cues = []
    for dialogue_id in sorted(cue_by_dialogue):
        cue = cue_by_dialogue[dialogue_id]
        base = start_by_shot[cue["shot_id"]]
        global_cues.append(
            {
                **cue,
                "start_sec": round(base + float(cue["start_offset_sec"]), 6),
                "end_sec": round(base + float(cue["end_offset_sec"]), 6),
            }
        )
    global_cues.sort(key=lambda row: row["start_sec"])
    return {
        "schema_version": 1,
        "fps": int(timing.get("fps", 24)),
        "total_duration_sec": round(cursor, 6),
        "timeline": timeline,
        "dialogue_cues": global_cues,
        "timing_digest": sha256_json(timing),
    }


def srt_timestamp(seconds: float) -> str:
    if seconds < 0:
        raise ValueError("negative timestamp")
    millis = int(round(seconds * 1000))
    hours, millis = divmod(millis, 3_600_000)
    minutes, millis = divmod(millis, 60_000)
    secs, millis = divmod(millis, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def build_srt(
    timing: dict[str, Any],
    shots: list[dict[str, Any]],
    language: str,
) -> str:
    if language not in LANGUAGES:
        raise ValueError(f"unsupported language: {language}")
    validated = validate_timing(timing, shots)
    shot_by_id = _shot_index(shots)
    blocks = []
    for idx, cue in enumerate(validated["dialogue_cues"], 1):
        shot = shot_by_id[cue["shot_id"]]
        text = shot["dialogue"][language].strip()
        blocks.append(
            "\n".join(
                [
                    str(idx),
                    f"{srt_timestamp(cue['start_sec'])} --> {srt_timestamp(cue['end_sec'])}",
                    text,
                ]
            )
        )
    return "\n\n".join(blocks) + ("\n" if blocks else "")
