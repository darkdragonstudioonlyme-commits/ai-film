#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from film.image_runner import compile_image_worker_request

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--job",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    job=json.loads(Path(args.job).read_text(encoding="utf-8"))
    matrix=json.loads((ROOT/"model-evaluations/slice01/model_matrix.json").read_text(encoding="utf-8"))
    runtime=json.loads((ROOT/"model-evaluations/slice01/gpu-worker/runtime_lock.json").read_text(encoding="utf-8"))
    req=compile_image_worker_request(job,matrix,runtime)
    out=Path(args.out)
    if not out.is_absolute(): out=ROOT/out
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(req,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"request_digest":req["request_digest"],"execution_permitted":req["execution_permitted"],"provider_resource_created":req["provider_resource_created"]},sort_keys=True))
    return 0
if __name__=="__main__": raise SystemExit(main())
