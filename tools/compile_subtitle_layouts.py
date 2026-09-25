#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from film.subtitle_layout import compile_subtitle_layout

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",default="projects/slice01/subtitles/layout_plans.json")
    args=ap.parse_args()
    timing=json.loads((ROOT/"projects/slice01/timing/timing.json").read_text(encoding="utf-8"))
    shots=json.loads((ROOT/"projects/slice01/shots/benchmark_shots.json").read_text(encoding="utf-8"))
    policy=json.loads((ROOT/"projects/slice01/subtitles/layout_policy.json").read_text(encoding="utf-8"))
    plans=[
        compile_subtitle_layout(timing,shots,language=lang,aspect=aspect,policy=policy)
        for aspect in ("9:16","16:9")
        for lang in ("en","zh-CN","vi")
    ]
    result={"schema_version":1,"status":"TEXT_LAYOUT_PLANS_READY_VISUAL_QC_NOT_RUN","plans":plans}
    out=Path(args.out)
    if not out.is_absolute(): out=ROOT/out
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"plans":len(plans),"blocked":sum(bool(p["blockers"]) for p in plans),"visual_qc":"NOT_RUN"},sort_keys=True))
    return 0
if __name__=="__main__": raise SystemExit(main())
