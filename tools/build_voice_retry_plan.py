#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from film.voice_retry import build_retry_plan

def load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",default="model-evaluations/auto-eval/voice_retry_plan_20260926.json")
    args=ap.parse_args()
    requests=load(ROOT/"model-evaluations/slice01/voice/requests/requests.json")["requests"]
    evidence=load(ROOT/"run-evidence/AUTO_EVAL_VOICE_WHISPER_V2_20260926.json")
    plan=build_retry_plan(requests=requests,auto_eval_results=evidence["results"])
    out=ROOT/args.out
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":plan["status"],"retry_count":plan["retry_count"],"out":str(out)},sort_keys=True))
    return 0
if __name__=="__main__": raise SystemExit(main())
