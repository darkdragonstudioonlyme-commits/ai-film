#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,subprocess,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

def load(p: Path): return json.loads(p.read_text(encoding="utf-8"))

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--runtime-python",required=True)
    ap.add_argument("--out-root",default="/home/dragon/ai-film-dev/run-evidence/auto-eval/video-20260926")
    ap.add_argument("--execute",action="store_true")
    args=ap.parse_args()
    batch=load(ROOT/"model-evaluations/auto-eval/current_batch_20260926.json")
    out_root=Path(args.out_root).resolve()
    jobs=[]
    for row in batch["video_assets"]:
        video=(ROOT/row["local_path_ref"]).resolve()
        out=out_root/row["asset_id"]/"technical.json"
        jobs.append({
            "asset_id":row["asset_id"],
            "video":str(video),
            "out":str(out),
            "argv":[args.runtime_python,str(ROOT/"tools/run_video_technical_auto_eval.py"),
                    "--asset-id",row["asset_id"],"--video",str(video),"--out",str(out)]
        })
    if not args.execute:
        print(json.dumps({"status":"PLANNED","job_count":len(jobs),"jobs":jobs},ensure_ascii=False))
        return 0
    rows=[]
    for job in jobs:
        out=Path(job["out"])
        if not out.is_file():
            proc=subprocess.run(job["argv"],cwd=ROOT,text=True,capture_output=True,check=False,timeout=300)
            out.parent.mkdir(parents=True,exist_ok=True)
            (out.parent/"technical.stdout.log").write_text(proc.stdout,encoding="utf-8")
            (out.parent/"technical.stderr.log").write_text(proc.stderr,encoding="utf-8")
            if proc.returncode!=0:
                raise SystemExit(f"technical QC failed for {job['asset_id']}: {proc.stderr[-2000:]}")
        rows.append(load(out))
    summary={
        "schema_version":1,
        "status":"PASS_TECHNICAL_QC_COMPLETE",
        "sample_count":len(rows),
        "evaluator_id":"deterministic-video-qc",
        "supplemental_only":True,
        "counts_toward_min_model_evaluators":False,
        "human_review_required":False,
        "production_acceptance":False,
        "results":rows,
    }
    (out_root/"technical_summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
        "status":summary["status"],
        "sample_count":summary["sample_count"],
        "hard_fail_asset_ids":[r["asset_id"] for r in rows if r["hard_fail_tags"]],
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
