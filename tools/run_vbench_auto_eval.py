#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from film.vbench_auto_eval import DIMENSIONS, build_receipt

CODE_REVISION = "fd18b3d055cb0fc6f066ca90fe2c3c8cbb698490"

def main() -> int:
    ap = argparse.ArgumentParser(description="Run VBench custom-input video evaluator.")
    ap.add_argument("--asset-id", required=True)
    ap.add_argument("--video", required=True)
    ap.add_argument("--vbench-repo", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    video = Path(args.video).resolve()
    repo = Path(args.vbench_repo).resolve()
    if not video.is_file():
        raise SystemExit("video missing")
    if not (repo / "evaluate.py").is_file():
        raise SystemExit("VBench evaluate.py missing")
    head = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
    if head != CODE_REVISION:
        raise SystemExit(f"VBench code revision drift: {head}")

    with tempfile.TemporaryDirectory(prefix="aifilm-vbench-") as td:
        td = Path(td)
        videos = td / "videos"
        results = td / "results"
        videos.mkdir()
        results.mkdir()
        local_video = videos / ("asset" + video.suffix.lower())
        try:
            local_video.symlink_to(video)
        except OSError:
            shutil.copy2(video, local_video)
        argv = [
            sys.executable,
            str(repo / "evaluate.py"),
            "--videos_path", str(videos),
            "--output_path", str(results),
            "--dimension", *DIMENSIONS,
            "--mode", "custom_input",
        ]
        completed = subprocess.run(argv, cwd=repo, text=True, capture_output=True, check=False)
        if completed.returncode != 0:
            raise SystemExit("VBench failed: " + completed.stderr[-4000:])
        result_files = sorted(results.glob("*_eval_results.json"))
        if len(result_files) != 1:
            raise SystemExit(f"expected one VBench result file, got {len(result_files)}")
        raw = json.loads(result_files[0].read_text(encoding="utf-8"))
        receipt = build_receipt(asset_id=args.asset_id, results=raw, code_revision=CODE_REVISION)
        receipt["evidence"]["video_path"] = str(video)
        receipt["evidence"]["stdout_tail"] = completed.stdout[-4000:]
        receipt["evidence"]["stderr_tail"] = completed.stderr[-4000:]

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": receipt["status"], "out": str(out)}, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
