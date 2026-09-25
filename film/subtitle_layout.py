from __future__ import annotations

from typing import Any


class SubtitleLayoutError(ValueError):
    pass


LANGUAGES = {"en", "zh-CN", "vi"}
ASPECTS = {"9:16", "16:9"}


def _visible_char_count(text: str) -> int:
    return len(text.strip())


def _wrap_cjk(text: str, max_chars: int) -> list[str]:
    chars = list(text.strip())
    return ["".join(chars[i:i+max_chars]) for i in range(0, len(chars), max_chars)] or [""]


def _wrap_words(text: str, max_chars: int) -> list[str]:
    words = text.strip().split()
    if not words:
        return [""]
    lines = []
    current = words[0]
    for word in words[1:]:
        candidate = current + " " + word
        if len(candidate) <= max_chars:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def compile_subtitle_layout(
    timing: dict[str, Any],
    shots: list[dict[str, Any]],
    *,
    language: str,
    aspect: str,
    policy: dict[str, Any],
) -> dict[str, Any]:
    if language not in LANGUAGES:
        raise SubtitleLayoutError(f"unsupported language: {language}")
    if aspect not in ASPECTS:
        raise SubtitleLayoutError(f"unsupported aspect: {aspect}")
    aspect_policy = policy.get("aspects", {}).get(aspect)
    if not aspect_policy:
        raise SubtitleLayoutError(f"missing aspect policy: {aspect}")
    max_lines = int(aspect_policy["max_lines"])
    max_chars = int(aspect_policy["max_chars_per_line"][language])
    max_cps = float(policy["max_cps"][language])
    safe_box = aspect_policy["safe_box_norm"]
    for field in ("x", "y", "width", "height"):
        value = float(safe_box[field])
        if value < 0 or value > 1:
            raise SubtitleLayoutError("safe box outside normalized frame")
    if float(safe_box["x"]) + float(safe_box["width"]) > 1.0 + 1e-9:
        raise SubtitleLayoutError("safe box exceeds frame width")
    if float(safe_box["y"]) + float(safe_box["height"]) > 1.0 + 1e-9:
        raise SubtitleLayoutError("safe box exceeds frame height")

    shot_by_id = {shot["shot_id"]: shot for shot in shots}
    cursor = 0.0
    shot_starts = {}
    for row in timing.get("shots", []):
        shot_starts[row["shot_id"]] = cursor
        cursor += float(row["duration_sec"])
    if abs(cursor - 75.0) > 1e-9:
        raise SubtitleLayoutError("slice01 timeline must remain 75s")

    rows = []
    blockers: list[str] = []
    for cue in timing.get("dialogue_cues", []):
        shot = shot_by_id.get(cue["shot_id"])
        if shot is None or not shot.get("dialogue"):
            raise SubtitleLayoutError("subtitle cue missing shot dialogue")
        text = shot["dialogue"].get(language)
        if not isinstance(text, str) or not text.strip():
            blockers.append(f"missing-subtitle-text:{cue['dialogue_id']}:{language}")
            text = ""
        duration = float(cue["end_offset_sec"]) - float(cue["start_offset_sec"])
        cps = round(_visible_char_count(text) / duration, 6) if duration > 0 else float("inf")
        lines = _wrap_cjk(text, max_chars) if language == "zh-CN" else _wrap_words(text, max_chars)
        if len(lines) > max_lines:
            blockers.append(f"subtitle-too-many-lines:{cue['dialogue_id']}:{language}:{aspect}")
        if any(len(line) > max_chars for line in lines):
            blockers.append(f"subtitle-line-too-long:{cue['dialogue_id']}:{language}:{aspect}")
        if cps > max_cps + 1e-9:
            blockers.append(f"subtitle-cps-high:{cue['dialogue_id']}:{language}:{cps}>{max_cps}")
        rows.append({
            "dialogue_id": cue["dialogue_id"],
            "shot_id": cue["shot_id"],
            "start_sec": round(shot_starts[cue["shot_id"]] + float(cue["start_offset_sec"]), 6),
            "end_sec": round(shot_starts[cue["shot_id"]] + float(cue["end_offset_sec"]), 6),
            "text": text,
            "lines": lines,
            "line_count": len(lines),
            "estimated_cps": cps,
            "max_cps_heuristic": max_cps,
            "max_chars_per_line": max_chars,
        })

    return {
        "schema_version": 1,
        "project_id": policy["project_id"],
        "language": language,
        "aspect": aspect,
        "duration_sec": 75.0,
        "status": "READY_TEXT_LAYOUT" if not blockers else "BLOCKED_TEXT_LAYOUT",
        "safe_box_norm": dict(safe_box),
        "rows": rows,
        "blockers": sorted(set(blockers)),
        "visual_collision_status": "NOT_EVALUATED_REQUIRES_RENDERED_FRAME_QC",
        "render_authorized": False,
    }
