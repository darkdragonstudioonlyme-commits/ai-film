from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .auto_eval import AutoEvalError, aggregate_auto_eval, rank_auto_eval_results


class CurrentVideoEnsembleError(ValueError):
    pass


def _load_receipt(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise CurrentVideoEnsembleError(f"missing evaluator receipt: {path}")
    try:
        value=json.loads(path.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError) as exc:
        raise CurrentVideoEnsembleError(f"invalid evaluator receipt: {path}") from exc
    if not isinstance(value,dict):
        raise CurrentVideoEnsembleError(f"receipt must be object: {path}")
    return value


def finalize_current_video_ensemble(
    *,
    policy: dict[str,Any],
    batch: dict[str,Any],
    pending: dict[str,Any],
    receipt_root: Path,
) -> dict[str,Any]:
    if batch.get("schema_version")!=1:
        raise CurrentVideoEnsembleError("invalid current batch schema")
    assets=batch.get("video_assets")
    if not isinstance(assets,list) or len(assets)!=4:
        raise CurrentVideoEnsembleError("current video population must contain four assets")
    asset_ids=[row.get("asset_id") for row in assets]
    if any(not isinstance(x,str) or not x for x in asset_ids) or len(asset_ids)!=len(set(asset_ids)):
        raise CurrentVideoEnsembleError("invalid current video asset ids")

    if pending.get("schema_version")!=1 or pending.get("evaluator_id")!="vbench-video-v0.1.5":
        raise CurrentVideoEnsembleError("invalid VBench pending set")
    eligible=set(pending.get("eligible_asset_ids",[]))
    skipped_rows=pending.get("skipped_assets",[])
    skipped={row.get("asset_id"):row for row in skipped_rows if isinstance(row,dict)}
    if eligible | set(skipped) != set(asset_ids) or eligible & set(skipped):
        raise CurrentVideoEnsembleError("VBench pending population does not partition current videos")
    if len(eligible)!=3 or len(skipped)!=1:
        raise CurrentVideoEnsembleError("expected three VBench eligible assets and one hard-fail skip")

    results=[]
    receipt_manifest=[]
    for asset_id in asset_ids:
        base=receipt_root/asset_id
        paths={
            "qwen3-vl-2b-semantic":base/"qwen3vl.json",
            "paddleocr-text-artifact":base/"paddleocr.json",
        }
        if asset_id in eligible:
            paths["vbench-video-v0.1.5"]=base/"vbench.json"
        technical_path=base/"technical.json"
        if technical_path.is_file():
            paths["deterministic-video-qc"]=technical_path
        receipts=[]
        for evaluator_id,path in paths.items():
            rec=_load_receipt(path)
            if rec.get("evaluator_id")!=evaluator_id:
                raise CurrentVideoEnsembleError(
                    f"evaluator id mismatch for {asset_id}: expected {evaluator_id}"
                )
            if rec.get("asset_id")!=asset_id:
                raise CurrentVideoEnsembleError(f"receipt asset mismatch: {asset_id}")
            receipts.append(rec)
            receipt_manifest.append({
                "asset_id":asset_id,
                "evaluator_id":evaluator_id,
                "path":str(path),
            })
        try:
            decision=aggregate_auto_eval(
                policy,
                stage="short_video_take",
                asset_id=asset_id,
                receipts=receipts,
            )
        except AutoEvalError as exc:
            raise CurrentVideoEnsembleError(f"aggregation failed for {asset_id}: {exc}") from exc

        if asset_id in skipped:
            expected=set(skipped[asset_id].get("hard_fail_tags",[]))
            triggered=set(decision.get("triggered_hard_fail_tags",[]))
            if decision.get("status")!="AUTO_REJECT_HARD_FAIL" or not expected or not expected.issubset(triggered):
                raise CurrentVideoEnsembleError(f"skipped asset lost terminal hard fail: {asset_id}")
            decision["vbench_execution"]="SKIPPED_TERMINAL_HARD_FAIL"
        else:
            if decision.get("missing_evaluators") or decision.get("failed_evaluators"):
                raise CurrentVideoEnsembleError(f"eligible asset still has evaluator gap: {asset_id}")
            decision["vbench_execution"]="COMPLETED"
        results.append(decision)

    ranked=rank_auto_eval_results(results)
    blocked=[r["asset_id"] for r in ranked if r["status"].startswith("BLOCKED_")]
    if blocked:
        raise CurrentVideoEnsembleError("final ensemble unexpectedly blocked: "+",".join(blocked))
    shortlist=[r["asset_id"] for r in ranked if r["status"]=="AUTO_SHORTLIST"]
    retry=[r["asset_id"] for r in ranked if r["status"]=="AUTO_RETRY"]
    rejected=[r["asset_id"] for r in ranked if r["status"].startswith("AUTO_REJECT")]
    return {
        "schema_version":1,
        "batch_id":batch.get("batch_id")+"-video-final",
        "status":"PASS_AUTO_EVAL_COMPLETE",
        "sample_count":len(ranked),
        "required_video_evaluators":[
            "vbench-video-v0.1.5",
            "qwen3-vl-2b-semantic",
            "paddleocr-text-artifact",
        ],
        "vbench_executed_count":len(eligible),
        "vbench_skipped_hard_fail_count":len(skipped),
        "auto_shortlist_asset_ids":shortlist,
        "auto_retry_asset_ids":retry,
        "auto_reject_asset_ids":rejected,
        "human_review_required":False,
        "production_acceptance":False,
        "publish_authority":False,
        "receipt_manifest":receipt_manifest,
        "results":ranked,
    }
