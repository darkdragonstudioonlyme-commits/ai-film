#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from film.auto_eval import aggregate_auto_eval
from film.whisper_auto_eval import build_whisper_receipt

MODEL_SHA256="aff26ae408abcba5fbf8813c21e62b0941638c5f6eebfb145be0c9839262a19a"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    ap=argparse.ArgumentParser(description="Recompute current voice auto-eval from saved Whisper transcripts without inference.")
    ap.add_argument("--source-root",default="/home/dragon/ai-film-dev/run-evidence/auto-eval/voice-20260926")
    ap.add_argument("--out-root",default="/home/dragon/ai-film-dev/run-evidence/auto-eval/voice-20260926-v2")
    args=ap.parse_args()

    source_root=Path(args.source_root).resolve()
    out_root=Path(args.out_root).resolve()
    if source_root==out_root:
        raise SystemExit("out-root must differ from source-root")
    batch=load(ROOT/"model-evaluations/auto-eval/current_batch_20260926.json")
    policy=load(ROOT/batch["policy_ref"])
    source_summary=load(source_root/"summary.json")
    by_asset={row["asset_id"]:row for row in batch["voice_assets"]}
    if set(by_asset)!={row["asset_id"] for row in source_summary["results"]}:
        raise SystemExit("source voice population mismatch")

    results=[]
    for asset_id,row in sorted(by_asset.items()):
        old_path=source_root/asset_id/"whisper.json"
        if not old_path.is_file():
            raise SystemExit(f"missing source receipt: {asset_id}")
        old=load(old_path)
        ev=old.get("evidence",{})
        if ev.get("model_sha256")!=MODEL_SHA256:
            raise SystemExit(f"model checksum drift in source receipt: {asset_id}")
        transcript=ev.get("transcript")
        detected=ev.get("detected_language")
        prob=ev.get("detected_language_probability")
        if not isinstance(transcript,str) or not isinstance(detected,str) or not isinstance(prob,(int,float)):
            raise SystemExit(f"incomplete saved Whisper evidence: {asset_id}")

        expected="zh" if row["language"]=="zh-CN" else row["language"]
        probs={expected:float(prob)}
        receipt=build_whisper_receipt(
            asset_id=asset_id,
            target_text=row["target_text"],
            expected_language=row["language"],
            transcript=transcript,
            detected_language=detected,
            detected_probabilities=probs,
            model_sha256=MODEL_SHA256,
        )
        receipt["evidence"].update({
            "source_receipt_sha256":hashlib.sha256(old_path.read_bytes()).hexdigest(),
            "recomputed_without_inference":True,
            "normalizer_revision":"whisper-text-normalizer-v2",
            "audio_path":ev.get("audio_path"),
            "device":ev.get("device"),
            "ffmpeg":ev.get("ffmpeg"),
        })
        asset_out=out_root/asset_id
        asset_out.mkdir(parents=True,exist_ok=True)
        receipt_path=asset_out/"whisper.json"
        receipt_path.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

        decision=aggregate_auto_eval(
            policy,
            stage="voice_take",
            asset_id=asset_id,
            receipts=[receipt],
            deterministic_metrics={"cue_fit":float(row["cue_fit_metric"])},
        )
        decision_path=asset_out/"decision.json"
        decision_path.write_text(json.dumps(decision,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        results.append({
            "asset_id":asset_id,
            "status":decision["status"],
            "score":decision.get("score"),
            "asr_text_match":decision.get("metrics",{}).get("asr_text_match"),
            "language_match":decision.get("metrics",{}).get("language_match"),
            "cue_fit":float(row["cue_fit_metric"]),
            "receipt":str(receipt_path),
            "decision":str(decision_path),
        })

    counts={}
    for row in results:
        counts[row["status"]]=counts.get(row["status"],0)+1
    scores=[float(row["score"]) for row in results if row["score"] is not None]
    summary={
        "schema_version":1,
        "batch_id":batch["batch_id"]+"-voice-v2",
        "status":"PASS_AUTO_EVAL_RECOMPUTE_COMPLETE",
        "normalizer_revision":"whisper-text-normalizer-v2",
        "source_summary_sha256":hashlib.sha256((source_root/"summary.json").read_bytes()).hexdigest(),
        "sample_count":len(results),
        "status_counts":counts,
        "mean_score":round(sum(scores)/len(scores),6) if scores else None,
        "retry_asset_ids":[r["asset_id"] for r in results if r["status"]=="AUTO_RETRY"],
        "rejected_asset_ids":[r["asset_id"] for r in results if r["status"].startswith("AUTO_REJECT")],
        "human_review_required":False,
        "production_acceptance":False,
        "results":results,
    }
    out_root.mkdir(parents=True,exist_ok=True)
    (out_root/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
