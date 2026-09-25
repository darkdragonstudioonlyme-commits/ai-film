#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from film.queue_control import dispatch_next

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--queue",default="projects/slice01/runtime/queue_state.json")
    ap.add_argument("--worker",required=True)
    ap.add_argument("--active",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    qpath=Path(args.queue)
    if not qpath.is_absolute(): qpath=ROOT/qpath
    queue=json.loads(qpath.read_text(encoding="utf-8"))
    profiles=json.loads((ROOT/"model-evaluations/slice01/resource_profiles.json").read_text(encoding="utf-8"))
    by={row["profile_id"]:row for row in profiles["profiles"]}
    worker=json.loads(Path(args.worker).read_text(encoding="utf-8"))
    active=json.loads(Path(args.active).read_text(encoding="utf-8"))
    updated,job,blocked=dispatch_next(queue,worker=worker,admission_profiles=by,active_by_project=active)
    out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps({"queue":updated,"dispatched":job,"blocked":blocked},ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"dispatched":None if job is None else job["job_id"],"blocked":len(blocked)},sort_keys=True))
    return 0
if __name__=="__main__": raise SystemExit(main())
