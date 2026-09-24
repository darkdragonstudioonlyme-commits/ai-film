#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from film.timing import build_srt, validate_timing, LANGUAGES

PALETTE = [
    "20242b",
    "24303d",
    "2b3038",
    "252936",
    "30313a",
    "26323b",
    "2d2a38",
    "25303a",
]


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_ffmpeg(explicit: str | None) -> Path | None:
    if explicit:
        p = Path(explicit).expanduser().resolve()
        return p if p.is_file() else None
    found = shutil.which("ffmpeg")
    return Path(found).resolve() if found else None


def ffmpeg_version(exe: Path) -> str:
    proc = subprocess.run([str(exe), "-version"], text=True, capture_output=True, check=True)
    return proc.stdout.splitlines()[0].strip()



def probe_media(ffmpeg: Path, path: Path) -> dict:
    proc = subprocess.run(
        [str(ffmpeg), "-hide_banner", "-i", str(path)],
        text=True,
        capture_output=True,
        check=False,
    )
    text = proc.stderr + "\n" + proc.stdout
    duration_match = re.search(r"Duration: (\d+):(\d+):(\d+(?:\.\d+)?)", text)
    video_match = re.search(r"Video:.*?(\d{2,5})x(\d{2,5})", text)
    if not duration_match or not video_match:
        raise RuntimeError("unable to probe rendered animatic")
    duration = (
        int(duration_match.group(1)) * 3600
        + int(duration_match.group(2)) * 60
        + float(duration_match.group(3))
    )
    return {
        "duration_sec": duration,
        "width": int(video_match.group(1)),
        "height": int(video_match.group(2)),
        "has_audio": "Audio:" in text,
    }

def run(cmd: list[str]) -> None:
    proc = subprocess.run(cmd, text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(
            "ffmpeg failed rc="
            + str(proc.returncode)
            + " stderr="
            + proc.stderr[-4000:]
        )


def render_aspect(
    ffmpeg: Path,
    *,
    timeline: list[dict],
    width: int,
    height: int,
    fps: int,
    out_path: Path,
) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="aifilm-animatic-") as td:
        temp = Path(td)
        segments = []
        for idx, row in enumerate(timeline):
            segment = temp / f"{idx:03d}.mp4"
            color = PALETTE[idx % len(PALETTE)]
            duration = float(row["duration_sec"])
            run(
                [
                    str(ffmpeg),
                    "-y",
                    "-hide_banner",
                    "-loglevel",
                    "error",
                    "-f",
                    "lavfi",
                    "-i",
                    f"color=c=0x{color}:s={width}x{height}:r={fps}:d={duration}",
                    "-an",
                    "-c:v",
                    "mpeg4",
                    "-q:v",
                    "5",
                    "-pix_fmt",
                    "yuv420p",
                    "-t",
                    str(duration),
                    str(segment),
                ]
            )
            segments.append(segment)

        concat_file = temp / "concat.txt"
        concat_file.write_text(
            "".join("file '" + str(path).replace("'", "'\\''") + "'\n" for path in segments),
            encoding="utf-8",
        )
        video_only = temp / "video.mp4"
        run(
            [
                str(ffmpeg),
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(concat_file),
                "-c",
                "copy",
                str(video_only),
            ]
        )
        total = sum(float(row["duration_sec"]) for row in timeline)
        run(
            [
                str(ffmpeg),
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-i",
                str(video_only),
                "-f",
                "lavfi",
                "-i",
                "anullsrc=r=48000:cl=stereo",
                "-t",
                str(total),
                "-c:v",
                "copy",
                "-c:a",
                "aac",
                "-b:a",
                "96k",
                "-shortest",
                str(out_path),
            ]
        )
        run(
            [
                str(ffmpeg),
                "-v",
                "error",
                "-i",
                str(out_path),
                "-f",
                "null",
                "-",
            ]
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a timing-only placeholder animatic.")
    parser.add_argument("--out-root", default="artifacts/slice01-animatic")
    parser.add_argument("--ffmpeg")
    parser.add_argument("--aspect", choices=["9:16", "16:9", "both"], default="both")
    parser.add_argument("--plan-only", action="store_true")
    parser.add_argument("--evidence")
    args = parser.parse_args()

    timing_path = ROOT / "projects/slice01/timing/timing.json"
    shots_path = ROOT / "projects/slice01/shots/benchmark_shots.json"
    timing = json.loads(timing_path.read_text(encoding="utf-8"))
    shots = json.loads(shots_path.read_text(encoding="utf-8"))
    validated = validate_timing(timing, shots)

    out_root = Path(args.out_root)
    if not out_root.is_absolute():
        out_root = ROOT / out_root
    out_root.mkdir(parents=True, exist_ok=True)

    subtitle_dir = out_root / "subtitles"
    subtitle_dir.mkdir(parents=True, exist_ok=True)
    for language in LANGUAGES:
        (subtitle_dir / f"{language}.srt").write_text(
            build_srt(timing, shots, language), encoding="utf-8"
        )

    aspects = []
    if args.aspect in {"9:16", "both"}:
        aspects.append(("9x16", 720, 1280))
    if args.aspect in {"16:9", "both"}:
        aspects.append(("16x9", 1280, 720))

    plan = {
        "schema_version": 1,
        "total_duration_sec": validated["total_duration_sec"],
        "fps": validated["fps"],
        "shot_count": len(validated["timeline"]),
        "timeline": validated["timeline"],
        "aspects": [
            {"name": name, "width": width, "height": height}
            for name, width, height in aspects
        ],
        "subtitles": [f"subtitles/{language}.srt" for language in LANGUAGES],
    }
    (out_root / "animatic_plan.json").write_text(
        json.dumps(plan, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    if args.plan_only:
        print(json.dumps({"status": "PLAN_ONLY", **plan}, ensure_ascii=False, sort_keys=True))
        return 0

    ffmpeg = resolve_ffmpeg(args.ffmpeg)
    if ffmpeg is None:
        print("FFMPEG_NOT_FOUND: pass --ffmpeg or install ffmpeg", file=sys.stderr)
        return 2

    outputs = []
    for name, width, height in aspects:
        output = out_root / f"slice01_animatic_{name}.mp4"
        render_aspect(
            ffmpeg,
            timeline=validated["timeline"],
            width=width,
            height=height,
            fps=validated["fps"],
            out_path=output,
        )
        probe = probe_media(ffmpeg, output)
        if probe["width"] != width or probe["height"] != height:
            raise RuntimeError(f"animatic dimensions mismatch: {probe}")
        if abs(probe["duration_sec"] - validated["total_duration_sec"]) > 0.25:
            raise RuntimeError(f"animatic duration mismatch: {probe}")
        if not probe["has_audio"]:
            raise RuntimeError("animatic is missing audio track")
        outputs.append(
            {
                "path": str(output),
                "aspect": name,
                "width": width,
                "height": height,
                "bytes": output.stat().st_size,
                "sha256": file_sha256(output),
                "probe": probe,
            }
        )

    evidence = {
        "schema_version": 1,
        "status": "PASS",
        "ffmpeg": str(ffmpeg),
        "ffmpeg_version": ffmpeg_version(ffmpeg),
        "ffmpeg_sha256": file_sha256(ffmpeg),
        "total_duration_sec_expected": validated["total_duration_sec"],
        "fps": validated["fps"],
        "outputs": outputs,
        "subtitle_files": [
            {
                "language": language,
                "path": str(subtitle_dir / f"{language}.srt"),
                "sha256": file_sha256(subtitle_dir / f"{language}.srt"),
            }
            for language in LANGUAGES
        ],
    }
    (out_root / "animatic_manifest.json").write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if args.evidence:
        evidence_path = Path(args.evidence)
        if not evidence_path.is_absolute():
            evidence_path = ROOT / evidence_path
        evidence_path.parent.mkdir(parents=True, exist_ok=True)
        evidence_path.write_text(
            json.dumps(evidence, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(evidence, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
