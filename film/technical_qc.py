from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any


class TechnicalQCError(ValueError):
    pass


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_rate(value: str | None) -> float | None:
    if not value:
        return None
    if "/" in value:
        a, b = value.split("/", 1)
        denom = float(b)
        return None if denom == 0 else float(a) / denom
    return float(value)


def evaluate_ffprobe(
    probe: dict[str, Any],
    *,
    expected_duration_sec: float,
    expected_width: int,
    expected_height: int,
    expected_fps: float,
    duration_tolerance_sec: float = 0.25,
    fps_tolerance: float = 0.1,
    audio_required: bool = True,
    expected_audio_sample_rate: int = 48000,
) -> dict[str, Any]:
    blockers: list[str] = []
    streams = probe.get("streams", [])
    fmt = probe.get("format", {})
    try:
        duration = float(fmt.get("duration"))
    except (TypeError, ValueError):
        raise TechnicalQCError("ffprobe format.duration missing/invalid")
    if abs(duration - float(expected_duration_sec)) > float(duration_tolerance_sec):
        blockers.append(f"duration:{duration}")

    videos = [s for s in streams if s.get("codec_type") == "video"]
    audios = [s for s in streams if s.get("codec_type") == "audio"]
    if len(videos) != 1:
        blockers.append(f"video-stream-count:{len(videos)}")
    else:
        video = videos[0]
        if int(video.get("width", 0)) != int(expected_width) or int(video.get("height", 0)) != int(expected_height):
            blockers.append(f"dimensions:{video.get('width')}x{video.get('height')}")
        fps = parse_rate(video.get("avg_frame_rate") or video.get("r_frame_rate"))
        if fps is None or abs(fps - float(expected_fps)) > float(fps_tolerance):
            blockers.append(f"fps:{fps}")

    if audio_required:
        if len(audios) < 1:
            blockers.append("audio-missing")
        else:
            sample_rate = int(audios[0].get("sample_rate", 0))
            if sample_rate != int(expected_audio_sample_rate):
                blockers.append(f"audio-sample-rate:{sample_rate}")

    return {
        "schema_version": 1,
        "status": "PASS" if not blockers else "FAIL",
        "blockers": blockers,
        "measured_duration_sec": duration,
        "video_streams": len(videos),
        "audio_streams": len(audios),
        "expected": {
            "duration_sec": float(expected_duration_sec),
            "width": int(expected_width),
            "height": int(expected_height),
            "fps": float(expected_fps),
            "audio_required": bool(audio_required),
            "audio_sample_rate": int(expected_audio_sample_rate),
        },
    }


def bind_media_identity(
    qc_result: dict[str, Any],
    media_path: Path,
    *,
    technical_qc_id: str,
) -> dict[str, Any]:
    if not media_path.is_file():
        raise TechnicalQCError("media file missing")
    out = dict(qc_result)
    out["technical_qc_id"] = technical_qc_id
    out["media_path"] = str(media_path)
    out["media_bytes"] = media_path.stat().st_size
    out["media_sha256"] = file_sha256(media_path)
    return out
