from __future__ import annotations

import hashlib
import json
from typing import Any


class RenderCompileError(ValueError):
    pass


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _target_size(aspect: str) -> tuple[int, int]:
    if aspect == "9:16":
        return 720, 1280
    if aspect == "16:9":
        return 1280, 720
    raise RenderCompileError("unsupported aspect")


def compile_ffmpeg_render_spec(
    edit_plan: dict[str, Any],
    asset_catalog: dict[str, dict[str, Any]],
    *,
    output_path: str,
    fps: int = 24,
) -> dict[str, Any]:
    plan_body = {k: v for k, v in edit_plan.items() if k not in {"plan_digest", "status"}}
    if edit_plan.get("plan_digest") != digest(plan_body):
        raise RenderCompileError("edit plan digest mismatch")
    if edit_plan.get("status") != "READY_TO_RENDER":
        raise RenderCompileError("edit plan is not READY_TO_RENDER")
    if edit_plan.get("blockers"):
        raise RenderCompileError("edit plan contains blockers")
    if edit_plan.get("render_authorized") is not False:
        raise RenderCompileError("edit plan unexpectedly carries execution authority")
    if fps <= 0:
        raise RenderCompileError("fps must be positive")
    width, height = _target_size(edit_plan["aspect"])

    video_inputs: list[dict[str, Any]] = []
    audio_inputs: list[dict[str, Any]] = []
    filter_parts: list[str] = []

    for idx, segment in enumerate(edit_plan["segments"]):
        video = segment.get("video")
        if not video or not video.get("asset_id"):
            raise RenderCompileError(f"segment missing video asset: {segment.get('shot_id')}")
        asset_id = video["asset_id"]
        catalog = asset_catalog.get(asset_id)
        if catalog is None:
            raise RenderCompileError(f"video asset missing from catalog: {asset_id}")
        if catalog.get("manifest_sha256") != video.get("manifest_sha256"):
            raise RenderCompileError(f"video manifest mismatch: {asset_id}")
        if not catalog.get("path") or not catalog.get("sha256"):
            raise RenderCompileError(f"video catalog identity incomplete: {asset_id}")
        for field in ("sha256", "manifest_sha256"):
            value = catalog.get(field)
            if not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
                raise RenderCompileError(f"invalid video catalog {field}: {asset_id}")
        duration = float(segment["duration_sec"])
        video_inputs.append({
            "input_index": idx,
            "asset_id": asset_id,
            "path": catalog["path"],
            "sha256": catalog["sha256"],
            "manifest_sha256": catalog["manifest_sha256"],
            "duration_sec": duration,
        })
        filter_parts.append(
            f"[{idx}:v]"
            f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,"
            f"fps={fps},tpad=stop_mode=clone:stop_duration={duration},"
            f"trim=duration={duration},setpts=PTS-STARTPTS[v{idx}]"
        )

    video_labels = "".join(f"[v{i}]" for i in range(len(video_inputs)))
    filter_parts.append(f"{video_labels}concat=n={len(video_inputs)}:v=1:a=0[vout]")

    base_audio_index = len(video_inputs)
    for offset, cue in enumerate(edit_plan.get("dialogue", [])):
        audio = cue.get("audio")
        if not audio or not audio.get("asset_id"):
            raise RenderCompileError(f"dialogue missing audio asset: {cue.get('dialogue_id')}")
        asset_id = audio["asset_id"]
        catalog = asset_catalog.get(asset_id)
        if catalog is None:
            raise RenderCompileError(f"audio asset missing from catalog: {asset_id}")
        if catalog.get("sha256") != audio.get("sha256"):
            raise RenderCompileError(f"audio sha mismatch: {asset_id}")
        if not catalog.get("path"):
            raise RenderCompileError(f"audio catalog path missing: {asset_id}")
        value = catalog.get("sha256")
        if not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
            raise RenderCompileError(f"invalid audio catalog sha256: {asset_id}")
        input_index = base_audio_index + offset
        start_ms = int(round(float(cue["start_sec"]) * 1000))
        budget = float(cue["end_sec"]) - float(cue["start_sec"])
        audio_inputs.append({
            "input_index": input_index,
            "asset_id": asset_id,
            "path": catalog["path"],
            "sha256": catalog["sha256"],
            "start_sec": float(cue["start_sec"]),
            "end_sec": float(cue["end_sec"]),
            "budget_sec": budget,
        })
        filter_parts.append(
            f"[{input_index}:a]"
            f"atrim=duration={budget},asetpts=PTS-STARTPTS,"
            f"adelay={start_ms}|{start_ms}[a{offset}]"
        )

    silence_index = base_audio_index + len(audio_inputs)
    filter_parts.append(f"[{silence_index}:a]atrim=duration={edit_plan['duration_sec']}[asilence]")
    audio_labels = "[asilence]" + "".join(f"[a{i}]" for i in range(len(audio_inputs)))
    filter_parts.append(
        f"{audio_labels}amix=inputs={len(audio_inputs)+1}:duration=longest:normalize=0[aout]"
    )
    filter_complex = ";".join(filter_parts)

    argv = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"]
    for row in video_inputs:
        argv += ["-i", row["path"]]
    for row in audio_inputs:
        argv += ["-i", row["path"]]
    argv += [
        "-f", "lavfi",
        "-t", str(edit_plan["duration_sec"]),
        "-i", "anullsrc=r=48000:cl=stereo",
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-map", "[aout]",
        "-t", str(edit_plan["duration_sec"]),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-r", str(fps),
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "48000",
        "-movflags", "+faststart",
        output_path,
    ]

    spec = {
        "schema_version": 1,
        "edit_plan_digest": edit_plan["plan_digest"],
        "aspect": edit_plan["aspect"],
        "language": edit_plan["language"],
        "duration_sec": edit_plan["duration_sec"],
        "fps": fps,
        "width": width,
        "height": height,
        "video_inputs": video_inputs,
        "audio_inputs": audio_inputs,
        "subtitle_path": edit_plan.get("subtitle_path"),
        "filter_complex": filter_complex,
        "ffmpeg_argv": argv,
        "output_path": output_path,
        "execution_permitted": False,
    }
    spec["spec_digest"] = digest(spec)
    return spec
