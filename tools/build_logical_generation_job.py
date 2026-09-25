#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from film.generation_control import logical_generation_key,new_logical_job

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    data=json.loads(Path(args.input).read_text(encoding="utf-8"))
    key=logical_generation_key(
        shot_spec=data["shot_spec"],
        model_identity=data["model_identity"],
        compiled_prompt=data["compiled_prompt"],
        reference_digests=data.get("reference_digests",[]),
        seed_policy=data["seed_policy"],
        workflow_config=data["workflow_config"],
        creative_revision=int(data["creative_revision"]),
    )
    job=new_logical_job(
        logical_key=key,
        max_attempts=int(data["max_attempts"]),
        cost_ceiling_usd=float(data["cost_ceiling_usd"]),
    )
    out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(job,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"logical_key":key,"status":job["status"],"max_attempts":job["max_attempts"],"cost_ceiling_usd":job["cost_ceiling_usd"]},sort_keys=True))
    return 0
if __name__=="__main__": raise SystemExit(main())
