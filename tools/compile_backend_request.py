#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from film.adapters import compile_backend_request


def main() -> int:
    parser=argparse.ArgumentParser(description="Compile a benchmark job into a deterministic backend request. No inference is executed.")
    parser.add_argument("--job",required=True)
    parser.add_argument("--out",required=True)
    args=parser.parse_args()
    job=json.loads(Path(args.job).read_text(encoding="utf-8"))
    matrix=json.loads((ROOT/"model-evaluations/slice01/model_matrix.json").read_text(encoding="utf-8"))
    request=compile_backend_request(job,matrix,ROOT)
    out=Path(args.out)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(request,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"job_id":request["job_id"],"model_id":request["model"]["model_id"],"request_digest":request["request_digest"],"execution_permitted":request["execution_permitted"]},sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
