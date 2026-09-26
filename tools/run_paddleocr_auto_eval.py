#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from film.paddleocr_auto_eval import build_receipt

def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def main() -> int:
    ap = argparse.ArgumentParser(description="Run PaddleOCR text-artifact evaluator on sampled video frames.")
    ap.add_argument("--asset-id", required=True)
    ap.add_argument("--video", required=True)
    ap.add_argument("--context")
    ap.add_argument("--sample-fps", type=float, default=4.0)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    video = Path(args.video).resolve()
    if not video.is_file():
        raise SystemExit("video missing")
    allowed = []
    if args.context:
        context = load(Path(args.context))
        allowed = context.get("allowed_text_regex", [])
        if not isinstance(allowed, list):
            raise SystemExit("allowed_text_regex must be a list")

    from imageio_ffmpeg import get_ffmpeg_exe
    ffmpeg_exe=Path(get_ffmpeg_exe()).resolve()
    if not ffmpeg_exe.is_file():
        raise SystemExit("imageio-ffmpeg binary missing")

    with tempfile.TemporaryDirectory(prefix="aifilm-ocr-") as td:
        td = Path(td)
        frame_pattern = td / "frame_%04d.png"
        completed = subprocess.run(
            [
                str(ffmpeg_exe), "-hide_banner", "-loglevel", "error", "-y",
                "-i", str(video), "-vf", f"fps={args.sample_fps}", str(frame_pattern),
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            raise SystemExit("ffmpeg frame sampling failed: " + completed.stderr[-2000:])
        frames = sorted(td.glob("frame_*.png"))
        if not frames:
            raise SystemExit("no OCR frames sampled")

        from paddleocr import PaddleOCR
        ocr = PaddleOCR(
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
            enable_mkldnn=False,
        )
        payloads = []
        for index, frame in enumerate(frames):
            results = list(ocr.predict(str(frame)))
            if not results:
                payloads.append({"res": {"rec_texts": [], "rec_scores": []}})
                continue
            json_path = td / f"ocr_{index:04d}.json"
            results[0].save_to_json(str(json_path))
            payloads.append(json.loads(json_path.read_text(encoding="utf-8")))

        receipt = build_receipt(asset_id=args.asset_id, payloads=payloads, allowed_text_regex=allowed)
        receipt["evidence"]["video_path"] = str(video)
        receipt["evidence"]["sample_fps"] = args.sample_fps
        receipt["evidence"]["sampled_frames"] = len(frames)
        receipt["evidence"]["ffmpeg"] = str(ffmpeg_exe)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": receipt["status"], "hard_fail_tags": receipt["hard_fail_tags"], "out": str(out)}, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
