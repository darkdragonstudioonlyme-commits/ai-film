#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from film.current_video_ensemble import CurrentVideoEnsembleError, finalize_current_video_ensemble

def load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))

def main()->int:
    ap=argparse.ArgumentParser(description="Finalize current 4-clip video AUTO_EVAL after three eligible VBench receipts are synced locally.")
    ap.add_argument("--receipt-root",default="/home/dragon/ai-film-dev/run-evidence/auto-eval/video-20260926")
    ap.add_argument("--out",default="run-evidence/AUTO_EVAL_VIDEO_FINAL_ENSEMBLE_20260926.json")
    ap.add_argument("--check-only",action="store_true")
    args=ap.parse_args()
    receipt_root=Path(args.receipt_root).resolve()
    try:
        result=finalize_current_video_ensemble(
            policy=load(ROOT/"model-evaluations/auto-eval/policy.json"),
            batch=load(ROOT/"model-evaluations/auto-eval/current_batch_20260926.json"),
            pending=load(ROOT/"model-evaluations/auto-eval/vbench_pending_20260926.json"),
            receipt_root=receipt_root,
        )
    except CurrentVideoEnsembleError as exc:
        print(json.dumps({"status":"BLOCKED","reason":str(exc)},ensure_ascii=False,sort_keys=True))
        return 3
    if not args.check_only:
        out=Path(args.out)
        if not out.is_absolute(): out=ROOT/out
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
        "status":result["status"],
        "shortlist":result["auto_shortlist_asset_ids"],
        "retry":result["auto_retry_asset_ids"],
        "reject":result["auto_reject_asset_ids"],
        "vbench_executed_count":result["vbench_executed_count"],
    },ensure_ascii=False,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
