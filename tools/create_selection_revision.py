#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from film.production_state import select_take

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--shot",required=True)
    ap.add_argument("--take",required=True)
    ap.add_argument("--previous-selection")
    ap.add_argument("--actor",required=True)
    ap.add_argument("--out-state",required=True)
    ap.add_argument("--out-selection",required=True)
    args=ap.parse_args()
    shot=json.loads(Path(args.shot).read_text(encoding="utf-8"))
    take=json.loads(Path(args.take).read_text(encoding="utf-8"))
    previous=None if not args.previous_selection else json.loads(Path(args.previous_selection).read_text(encoding="utf-8"))
    updated,selection=select_take(shot,take,expected_shot_version=int(shot["version"]),actor=args.actor,previous_selection=previous)
    Path(args.out_state).write_text(json.dumps(updated,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    Path(args.out_selection).write_text(json.dumps(selection,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"shot_id":updated["shot_id"],"selection_revision":selection["selection_revision"],"take_id":selection["take_id"]},sort_keys=True))
    return 0
if __name__=="__main__": raise SystemExit(main())
