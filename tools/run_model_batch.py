#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from film.batch_orchestrator import run_batch

def main()->int:
    ap=argparse.ArgumentParser(description="Run or plan a bounded model batch through model-specific adapters.")
    ap.add_argument("--config",required=True)
    ap.add_argument("--execute",action="store_true")
    ap.add_argument("--batch-root",default="/workspace/runs/model-batches")
    args=ap.parse_args()
    config=json.loads(Path(args.config).read_text(encoding="utf-8"))
    result=run_batch(config,root=ROOT,batch_root=Path(args.batch_root),execute=args.execute)
    print(json.dumps(result,ensure_ascii=False,sort_keys=True))
    return 0 if result.get("status") in {"PLANNED","PASS"} else 2
if __name__=="__main__": raise SystemExit(main())
