#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from film.whisper_auto_eval import LANG_MAP, build_whisper_receipt

MODEL_SHA256 = "aff26ae408abcba5fbf8813c21e62b0941638c5f6eebfb145be0c9839262a19a"

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def main() -> int:
    ap = argparse.ArgumentParser(description="Run Whisper turbo ASR evaluator for one voice take.")
    ap.add_argument("--asset-id", required=True)
    ap.add_argument("--audio", required=True)
    ap.add_argument("--target-text", required=True)
    ap.add_argument("--language", required=True)
    ap.add_argument("--model-dir", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    audio_path = Path(args.audio).resolve()
    model_dir = Path(args.model_dir).resolve()
    if not audio_path.is_file():
        raise SystemExit("audio missing")
    model_dir.mkdir(parents=True, exist_ok=True)

    import torch
    import whisper
    from imageio_ffmpeg import get_ffmpeg_exe

    ffmpeg_exe=Path(get_ffmpeg_exe()).resolve()
    if not ffmpeg_exe.is_file():
        raise SystemExit("imageio-ffmpeg binary missing")
    ffmpeg_bin=model_dir/".aifilm-bin"
    ffmpeg_bin.mkdir(parents=True,exist_ok=True)
    ffmpeg_link=ffmpeg_bin/"ffmpeg"
    if ffmpeg_link.exists() or ffmpeg_link.is_symlink():
        ffmpeg_link.unlink()
    ffmpeg_link.symlink_to(ffmpeg_exe)
    os.environ["PATH"]=str(ffmpeg_bin)+os.pathsep+os.environ.get("PATH","")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = whisper.load_model("turbo", device=device, download_root=str(model_dir))
    weight = model_dir / "large-v3-turbo.pt"
    if not weight.is_file():
        raise SystemExit("Whisper turbo weight missing after load")
    actual = sha256_file(weight)
    if actual != MODEL_SHA256:
        raise SystemExit(f"Whisper turbo checksum drift: {actual}")

    audio = whisper.load_audio(str(audio_path))
    padded = whisper.pad_or_trim(audio)
    mel = whisper.log_mel_spectrogram(padded, n_mels=model.dims.n_mels).to(model.device)
    _, probs = model.detect_language(mel)
    detected = max(probs, key=probs.get)
    expected = LANG_MAP.get(args.language, args.language)
    result = model.transcribe(
        audio,
        language=expected,
        task="transcribe",
        temperature=0,
        condition_on_previous_text=False,
        fp16=device == "cuda",
    )
    receipt = build_whisper_receipt(
        asset_id=args.asset_id,
        target_text=args.target_text,
        expected_language=args.language,
        transcript=str(result.get("text") or "").strip(),
        detected_language=detected,
        detected_probabilities=probs,
        model_sha256=actual,
    )
    receipt["evidence"]["audio_path"] = str(audio_path)
    receipt["evidence"]["device"] = device
    receipt["evidence"]["ffmpeg"] = str(ffmpeg_exe)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": receipt["status"], "detected_language": detected, "out": str(out)}, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
