#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from film.image_model_blind_compare import (
    build_comparison_packet,
    score_template_csv,
)


def main() -> int:
    ap=argparse.ArgumentParser(description="Build the fixed blind FLUX2-vs-Z-Image comparison packet without selecting a winner.")
    ap.add_argument("--out-dir",default="projects/slice01/casting/formal_comparison")
    args=ap.parse_args()
    flux=json.loads((ROOT/"run-evidence/FLUX2_KLEIN_A40_FORMAL_SMOKE_20260925.json").read_text(encoding="utf-8"))
    zimg=json.loads((ROOT/"run-evidence/Z_IMAGE_A40_FORMAL_SMOKE_20260926.json").read_text(encoding="utf-8"))
    materialization_path=ROOT/"run-evidence/IMAGE_MODEL_BLIND_MATERIALIZATION_20260926.json"
    materialization=json.loads(materialization_path.read_text(encoding="utf-8")) if materialization_path.is_file() else None
    public,private=build_comparison_packet(flux,zimg,materialization)
    out=Path(args.out_dir)
    if not out.is_absolute():
        out=ROOT/out
    out.mkdir(parents=True,exist_ok=True)
    (out/"blind_items.json").write_text(json.dumps(public,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    (out/"blind_map_private.json").write_text(json.dumps(private,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    (out/"scores.csv").write_text(score_template_csv(public),encoding="utf-8")
    print(json.dumps({
        "comparison_id":public["comparison_id"],
        "status":public["status"],
        "sample_count":public["sample_count"],
        "selection_authorized":public["selection_authorized"],
    },sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
