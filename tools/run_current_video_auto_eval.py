#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from film.auto_eval import aggregate_auto_eval, rank_auto_eval_results

def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def resolve_asset_path(row: dict, mode: str) -> str:
    key = "local_path_ref" if mode == "local" else "pod_path_ref"
    value = row[key]
    if mode == "local":
        return str((ROOT / value).resolve())
    return value

def main() -> int:
    ap = argparse.ArgumentParser(description="Run/resume multi-model auto-eval over current video takes.")
    ap.add_argument("--asset-path-mode", choices=["local", "pod"], default="local")
    ap.add_argument("--run-evaluator", action="append", choices=["qwen", "vbench", "ocr"], default=[])
    ap.add_argument("--qwen-python")
    ap.add_argument("--qwen-model-dir")
    ap.add_argument("--vbench-python")
    ap.add_argument("--vbench-repo")
    ap.add_argument("--ocr-python")
    ap.add_argument("--out-root", default="/home/dragon/ai-film-dev/run-evidence/auto-eval/video-20260926")
    ap.add_argument("--execute", action="store_true")
    args = ap.parse_args()

    batch = load(ROOT / "model-evaluations/auto-eval/current_batch_20260926.json")
    policy = load(ROOT / batch["policy_ref"])
    out_root = Path(args.out_root).resolve()
    selected = set(args.run_evaluator)
    plan = []

    for row in batch["video_assets"]:
        asset_id = row["asset_id"]
        video = resolve_asset_path(row, args.asset_path_mode)
        context = str((ROOT / row["context_ref"]).resolve())
        base = out_root / asset_id
        jobs = {
            "qwen": {
                "receipt": base / "qwen3vl.json",
                "argv": [
                    args.qwen_python or "<qwen-python>",
                    str(ROOT / "tools/run_qwen3vl_auto_eval.py"),
                    "--asset-id", asset_id,
                    "--video", video,
                    "--context", context,
                    "--model-dir", args.qwen_model_dir or "<qwen-model-dir>",
                    "--out", str(base / "qwen3vl.json"),
                ],
            },
            "vbench": {
                "receipt": base / "vbench.json",
                "argv": [
                    args.vbench_python or "<vbench-python>",
                    str(ROOT / "tools/run_vbench_auto_eval.py"),
                    "--asset-id", asset_id,
                    "--video", video,
                    "--vbench-repo", args.vbench_repo or "<vbench-repo>",
                    "--out", str(base / "vbench.json"),
                ],
            },
            "ocr": {
                "receipt": base / "paddleocr.json",
                "argv": [
                    args.ocr_python or "<ocr-python>",
                    str(ROOT / "tools/run_paddleocr_auto_eval.py"),
                    "--asset-id", asset_id,
                    "--video", video,
                    "--context", context,
                    "--out", str(base / "paddleocr.json"),
                ],
            },
        }
        plan.append({"asset_id": asset_id, "video": video, "context": context, "jobs": jobs})

    if not args.execute:
        print(json.dumps({"status": "PLANNED", "assets": plan}, ensure_ascii=False, default=str))
        return 0

    if "qwen" in selected and (not args.qwen_python or not args.qwen_model_dir):
        raise SystemExit("qwen execution requires --qwen-python and --qwen-model-dir")
    if "vbench" in selected and (not args.vbench_python or not args.vbench_repo):
        raise SystemExit("vbench execution requires --vbench-python and --vbench-repo")
    if "ocr" in selected and not args.ocr_python:
        raise SystemExit("ocr execution requires --ocr-python")

    results = []
    for asset in plan:
        base = out_root / asset["asset_id"]
        base.mkdir(parents=True, exist_ok=True)
        for name, job in asset["jobs"].items():
            receipt_path = Path(job["receipt"])
            if name not in selected or receipt_path.is_file():
                continue
            argv = [str(x) for x in job["argv"]]
            proc = subprocess.run(argv, cwd=ROOT, text=True, capture_output=True, timeout=3600, check=False)
            (base / f"{name}.stdout.log").write_text(proc.stdout, encoding="utf-8")
            (base / f"{name}.stderr.log").write_text(proc.stderr, encoding="utf-8")
            if proc.returncode != 0:
                raise SystemExit(f"{name} evaluator failed for {asset['asset_id']}: {proc.stderr[-3000:]}")

        receipts = []
        for job in asset["jobs"].values():
            path = Path(job["receipt"])
            if path.is_file():
                receipts.append(load(path))
        decision = aggregate_auto_eval(
            policy,
            stage="short_video_take",
            asset_id=asset["asset_id"],
            receipts=receipts,
        )
        decision_path = base / "decision.json"
        decision_path.write_text(json.dumps(decision, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        results.append(decision)

    ranked = rank_auto_eval_results(results)
    counts = {}
    for row in ranked:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    summary = {
        "schema_version": 1,
        "batch_id": batch["batch_id"] + "-video",
        "status": "PASS_AUTO_EVAL_COMPLETE" if all(r["status"] != "BLOCKED_EVALUATOR_GAP" for r in ranked) else "PARTIAL_EVALUATOR_RECEIPTS",
        "sample_count": len(ranked),
        "status_counts": counts,
        "human_review_required": False,
        "production_acceptance": False,
        "results": ranked,
    }
    (out_root / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
