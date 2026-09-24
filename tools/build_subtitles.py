#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from film.timing import LANGUAGES, build_srt, validate_timing


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Build deterministic slice01 subtitles.")
    parser.add_argument("--out-dir", default="projects/slice01/timing/subtitles")
    args = parser.parse_args()

    timing_path = ROOT / "projects/slice01/timing/timing.json"
    shots_path = ROOT / "projects/slice01/shots/benchmark_shots.json"
    timing = json.loads(timing_path.read_text(encoding="utf-8"))
    shots = json.loads(shots_path.read_text(encoding="utf-8"))
    validated = validate_timing(timing, shots)

    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = ROOT / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    outputs = {}
    for language in LANGUAGES:
        path = out_dir / f"{language}.srt"
        path.write_text(build_srt(timing, shots, language), encoding="utf-8")
        outputs[language] = {
            "path": path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),
            "sha256": sha256_file(path),
            "bytes": path.stat().st_size,
        }

    manifest = {
        "schema_version": 1,
        "total_duration_sec": validated["total_duration_sec"],
        "fps": validated["fps"],
        "shot_count": len(validated["timeline"]),
        "dialogue_cue_count": len(validated["dialogue_cues"]),
        "timing_digest": validated["timing_digest"],
        "subtitles": outputs,
    }
    manifest_path = out_dir.parent / "timing_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
