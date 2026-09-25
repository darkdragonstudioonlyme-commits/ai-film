#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from film.technical_qc import bind_media_identity,evaluate_ffprobe

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--probe",required=True)
    ap.add_argument("--policy",default="projects/slice01/technical_qc_policy.json")
    ap.add_argument("--variant",required=True)
    ap.add_argument("--media")
    ap.add_argument("--technical-qc-id",default="technical-qc")
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    probe=json.loads(Path(args.probe).read_text(encoding="utf-8"))
    policy_path=Path(args.policy)
    if not policy_path.is_absolute(): policy_path=ROOT/policy_path
    policy=json.loads(policy_path.read_text(encoding="utf-8"))
    variant=policy["variants"][args.variant]
    result=evaluate_ffprobe(
        probe,
        expected_duration_sec=policy["duration_sec"],
        expected_width=variant["width"],
        expected_height=variant["height"],
        expected_fps=policy["fps"],
        duration_tolerance_sec=policy["duration_tolerance_sec"],
        fps_tolerance=policy["fps_tolerance"],
        audio_required=policy["audio_required"],
        expected_audio_sample_rate=policy["audio_sample_rate"],
    )
    if args.media:
        result=bind_media_identity(result,Path(args.media),technical_qc_id=args.technical_qc_id)
    out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":result["status"],"blockers":len(result["blockers"])},sort_keys=True))
    return 0 if result["status"]=="PASS" else 2
if __name__=="__main__": raise SystemExit(main())
