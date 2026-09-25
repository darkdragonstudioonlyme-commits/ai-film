#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from film.prelaunch import build_prelaunch_bundle


def main() -> int:
    parser=argparse.ArgumentParser(description="Build deterministic visual-model GPU prelaunch bundle. No provider action is performed.")
    parser.add_argument("--out",default="/tmp/aifilm-visual-prelaunch.json")
    parser.add_argument("--apply",action="store_true")
    args=parser.parse_args()
    if args.apply:
        parser.error("--apply is intentionally disabled; T-019 owns paid/provider execution")
    bundle=build_prelaunch_bundle(ROOT)
    out=Path(args.out)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(bundle,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"mode":bundle["mode"],"models":len(bundle["models"]),"execution_ready":bundle["execution_ready"]},sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
