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

from film.auto_eval import aggregate_auto_eval

def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def main() -> int:
    ap = argparse.ArgumentParser(description="Run Whisper auto-eval over the current fixed 12-sample voice packet.")
    ap.add_argument("--runtime-python", required=True)
    ap.add_argument("--model-dir", required=True)
    ap.add_argument("--out-root", default="/home/dragon/ai-film-dev/run-evidence/auto-eval/voice-20260926")
    ap.add_argument("--execute", action="store_true")
    args = ap.parse_args()

    batch = load(ROOT / "model-evaluations/auto-eval/current_batch_20260926.json")
    policy = load(ROOT / batch["policy_ref"])
    out_root = Path(args.out_root).resolve()
    plan = []
    for row in batch["voice_assets"]:
        receipt = out_root / row["asset_id"] / "whisper.json"
        decision = out_root / row["asset_id"] / "decision.json"
        plan.append({
            "asset_id": row["asset_id"],
            "audio": str((ROOT / row["local_path_ref"]).resolve()),
            "target_text": row["target_text"],
            "language": row["language"],
            "cue_fit_metric": float(row["cue_fit_metric"]),
            "receipt": str(receipt),
            "decision": str(decision),
        })
    if not args.execute:
        print(json.dumps({"status": "PLANNED", "sample_count": len(plan), "jobs": plan}, ensure_ascii=False))
        return 0

    results = []
    for item in plan:
        receipt_path = Path(item["receipt"])
        if not receipt_path.is_file():
            receipt_path.parent.mkdir(parents=True, exist_ok=True)
            argv = [
                args.runtime_python,
                str(ROOT / "tools/run_whisper_auto_eval.py"),
                "--asset-id", item["asset_id"],
                "--audio", item["audio"],
                "--target-text", item["target_text"],
                "--language", item["language"],
                "--model-dir", str(Path(args.model_dir).resolve()),
                "--out", str(receipt_path),
            ]
            proc = subprocess.run(argv, cwd=ROOT, text=True, capture_output=True, timeout=900, check=False)
            (receipt_path.parent / "runner.stdout.log").write_text(proc.stdout, encoding="utf-8")
            (receipt_path.parent / "runner.stderr.log").write_text(proc.stderr, encoding="utf-8")
            if proc.returncode != 0:
                raise SystemExit(f"Whisper evaluator failed for {item['asset_id']}: {proc.stderr[-2000:]}")
        receipt = load(receipt_path)
        decision = aggregate_auto_eval(
            policy,
            stage="voice_take",
            asset_id=item["asset_id"],
            receipts=[receipt],
            deterministic_metrics={"cue_fit": item["cue_fit_metric"]},
        )
        decision_path = Path(item["decision"])
        decision_path.write_text(json.dumps(decision, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        results.append({
            "asset_id": item["asset_id"],
            "status": decision["status"],
            "score": decision.get("score"),
            "asr_text_match": decision.get("metrics", {}).get("asr_text_match"),
            "language_match": decision.get("metrics", {}).get("language_match"),
            "cue_fit": item["cue_fit_metric"],
            "receipt": str(receipt_path),
            "decision": str(decision_path),
        })

    counts = {}
    for row in results:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    scores = [float(r["score"]) for r in results if r["score"] is not None]
    summary = {
        "schema_version": 1,
        "batch_id": batch["batch_id"] + "-voice",
        "status": "PASS_AUTO_EVAL_COMPLETE",
        "sample_count": len(results),
        "status_counts": counts,
        "mean_score": round(sum(scores) / len(scores), 6) if scores else None,
        "retry_asset_ids": [r["asset_id"] for r in results if r["status"] == "AUTO_RETRY"],
        "rejected_asset_ids": [r["asset_id"] for r in results if r["status"].startswith("AUTO_REJECT")],
        "human_review_required": False,
        "production_acceptance": False,
        "results": results,
    }
    out_root.mkdir(parents=True, exist_ok=True)
    (out_root / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
