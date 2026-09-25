from __future__ import annotations

from typing import Any

from .script_engine import validate_screenplay_against_shots


class StoryCoverageError(ValueError):
    pass


def compile_story_shot_coverage(
    screenplay: dict[str, Any],
    timing: dict[str, Any],
    shots: list[dict[str, Any]],
) -> dict[str, Any]:
    script = validate_screenplay_against_shots(screenplay, shots)
    shot_by_id = {shot["shot_id"]: shot for shot in shots}
    timing_rows = timing.get("shots", [])
    if {row.get("shot_id") for row in timing_rows} != set(shot_by_id):
        raise StoryCoverageError("timing/shot population mismatch")

    # Flatten scene-relative beat ranges into project-global ranges.
    beats = []
    scene_offset = 0.0
    for scene in script["scenes"]:
        for beat in scene["beats"]:
            beats.append({
                "scene_id": scene["scene_id"],
                "beat_id": beat["beat_id"],
                "story_intent": beat["action"],
                "start_sec": scene_offset + float(beat["start_sec"]),
                "end_sec": scene_offset + float(beat["end_sec"]),
            })
        scene_offset += float(scene["estimated_duration_sec"])

    cursor = 0.0
    shot_rows = []
    blockers: list[str] = []
    beat_to_shots = {beat["beat_id"]: [] for beat in beats}
    for timing_row in timing_rows:
        shot_id = timing_row["shot_id"]
        duration = float(timing_row["duration_sec"])
        start = cursor
        end = start + duration
        containing = [
            beat for beat in beats
            if start >= beat["start_sec"] - 1e-9 and end <= beat["end_sec"] + 1e-9
        ]
        if len(containing) != 1:
            blockers.append(f"shot-not-contained-by-one-beat:{shot_id}")
            beat_id = None
            story_intent = None
            scene_id = None
        else:
            beat = containing[0]
            beat_id = beat["beat_id"]
            story_intent = beat["story_intent"]
            scene_id = beat["scene_id"]
            beat_to_shots[beat_id].append(shot_id)
        shot = shot_by_id[shot_id]
        shot_rows.append({
            "shot_id": shot_id,
            "scene_id": scene_id,
            "beat_id": beat_id,
            "story_intent": story_intent,
            "start_sec": round(start, 6),
            "end_sec": round(end, 6),
            "duration_sec": duration,
            "dialogue_id": shot.get("dialogue_id"),
        })
        cursor = end

    for beat in beats:
        if not beat_to_shots[beat["beat_id"]]:
            blockers.append(f"beat-without-shot:{beat['beat_id']}")

    if abs(cursor - float(script["target_duration_sec"])) > 1e-9:
        blockers.append(
            f"runtime-mismatch:shots={cursor}:screenplay={script['target_duration_sec']}"
        )

    covered_shots = {row["shot_id"] for row in shot_rows if row["beat_id"]}
    orphan_shots = sorted(set(shot_by_id) - covered_shots)
    for shot_id in orphan_shots:
        blockers.append(f"orphan-shot:{shot_id}")

    coverage_rows = [
        {
            **beat,
            "shot_ids": list(beat_to_shots[beat["beat_id"]]),
            "covered": bool(beat_to_shots[beat["beat_id"]]),
        }
        for beat in beats
    ]
    return {
        "schema_version": 1,
        "project_id": script["project_id"],
        "status": "COMPLETE" if not blockers else "BLOCKED_COVERAGE",
        "duration_sec": round(cursor, 6),
        "beat_coverage": coverage_rows,
        "shots": shot_rows,
        "blockers": sorted(set(blockers)),
    }
