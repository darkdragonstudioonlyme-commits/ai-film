#!/usr/bin/env python3
from __future__ import annotations

import argparse,json,subprocess,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from film.video_technical_auto_eval import build_receipt


def main()->int:
    ap=argparse.ArgumentParser(description="Run supplemental deterministic technical QC over one video.")
    ap.add_argument("--asset-id",required=True)
    ap.add_argument("--video",required=True)
    ap.add_argument("--out",required=True)
    ap.add_argument("--size",type=int,default=64)
    args=ap.parse_args()
    video=Path(args.video).resolve()
    if not video.is_file():
        raise SystemExit("video missing")
    if args.size<16 or args.size>256:
        raise SystemExit("invalid analysis size")

    import numpy as np
    from imageio_ffmpeg import get_ffmpeg_exe
    ffmpeg=Path(get_ffmpeg_exe()).resolve()
    if not ffmpeg.is_file():
        raise SystemExit("imageio-ffmpeg binary missing")

    completed=subprocess.run([
        str(ffmpeg),"-hide_banner","-loglevel","error",
        "-i",str(video),
        "-vf",f"scale={args.size}:{args.size}:flags=bilinear,format=gray",
        "-f","rawvideo","-pix_fmt","gray","-vsync","0","-"
    ],stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
    if completed.returncode!=0:
        raise SystemExit("video decode failed: "+completed.stderr.decode("utf-8","replace")[-2000:])
    frame_bytes=args.size*args.size
    raw=completed.stdout
    if not raw or len(raw)%frame_bytes:
        raise SystemExit("decoded frame buffer is empty/misaligned")
    frames=np.frombuffer(raw,dtype=np.uint8).reshape((-1,args.size,args.size)).astype(np.float32)
    means=frames.mean(axis=(1,2))
    black=int((means<5.0).sum())
    if len(frames)>1:
        deltas=np.abs(frames[1:]-frames[:-1]).mean(axis=(1,2))
        freezes=int((deltas<0.75).sum())
        mean_delta=float(deltas.mean())
        max_delta=float(deltas.max())
    else:
        freezes=0; mean_delta=0.0; max_delta=0.0

    receipt=build_receipt(
        asset_id=args.asset_id,
        frame_count=int(len(frames)),
        black_frame_count=black,
        freeze_transition_count=freezes,
        mean_frame_delta=mean_delta,
        max_frame_delta=max_delta,
        mean_luma=float(means.mean()),
        ffmpeg_path=str(ffmpeg),
    )
    receipt["evidence"]["video_path"]=str(video)
    out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
        "status":receipt["status"],
        "asset_id":args.asset_id,
        "frame_count":receipt["evidence"]["frame_count"],
        "black_ratio":receipt["evidence"]["black_frame_ratio"],
        "freeze_ratio":receipt["evidence"]["freeze_transition_ratio"],
        "hard_fail_tags":receipt["hard_fail_tags"],
        "out":str(out),
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
