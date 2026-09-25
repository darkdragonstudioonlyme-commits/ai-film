#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from film.asset_graph import AssetGraph

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--graph",required=True)
    ap.add_argument("--changed",action="append",required=True)
    ap.add_argument("--reason",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    graph_data=json.loads(Path(args.graph).read_text(encoding="utf-8"))
    graph=AssetGraph(graph_data.get("assets",[]),graph_data.get("edges",[]))
    plan=graph.invalidation_plan(set(args.changed),reason=args.reason)
    out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(plan,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"affected":len(plan["affected_assets"]),"unaffected":len(plan["unaffected_assets"]),"regeneration_authorized":plan["regeneration_authorized"]},sort_keys=True))
    return 0
if __name__=="__main__": raise SystemExit(main())
