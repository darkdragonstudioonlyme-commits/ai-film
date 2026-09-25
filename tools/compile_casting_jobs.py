#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from film.casting_jobs import compile_casting_jobs


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Compile deterministic casting-reference jobs without inference.")
    parser.add_argument("--out-dir", default="projects/slice01/casting/generation")
    args = parser.parse_args()

    contract = json.loads((ROOT / "projects/slice01/casting/reference_contract.json").read_text(encoding="utf-8"))
    matrix = json.loads((ROOT / "model-evaluations/slice01/model_matrix.json").read_text(encoding="utf-8"))
    jobs, public, private = compile_casting_jobs(contract, matrix)

    out = Path(args.out_dir)
    if not out.is_absolute():
        out = ROOT / out
    out.mkdir(parents=True, exist_ok=True)
    write_json(out / "casting_jobs.json", {
        "schema_version": 1,
        "status": "COMPILED_NOT_EXECUTED",
        "job_count": len(jobs),
        "jobs": jobs,
    })
    write_json(out / "blind_items.json", public)
    write_json(out / "blind_map_private.json", private)

    score_path = out / "scores.csv"
    criteria = contract["human_scoring"]["criteria"]
    with score_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(["blind_id", *criteria, "failure_tags", "notes"])
        for item in public["items"]:
            writer.writerow([item["blind_id"], *([""] * len(criteria)), "", ""])

    print(json.dumps({
        "status": "COMPILED_NOT_EXECUTED",
        "jobs": len(jobs),
        "blind_items": len(public["items"]),
        "active_models": sorted({job["model_id"] for job in jobs}),
        "out_dir": str(out),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
