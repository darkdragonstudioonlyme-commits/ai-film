from __future__ import annotations

from copy import deepcopy
from typing import Any


class AutoEvalError(ValueError):
    pass


PASS_RECEIPT_STATUSES={"PASS","PASS_MODEL_EVAL","PASS_RUNTIME_EVAL"}


def _text(value: Any, field: str) -> str:
    if not isinstance(value,str) or not value.strip():
        raise AutoEvalError(f"{field} must be non-empty text")
    return value.strip()


def validate_registry(registry: dict[str,Any]) -> dict[str,Any]:
    if not isinstance(registry,dict) or registry.get("schema_version")!=1:
        raise AutoEvalError("unsupported evaluator registry")
    rows=registry.get("evaluators")
    if not isinstance(rows,list) or not rows:
        raise AutoEvalError("evaluator registry requires evaluators")
    ids=[]
    normalized=[]
    for row in rows:
        if not isinstance(row,dict):
            raise AutoEvalError("evaluator row must be object")
        item=deepcopy(row)
        item["evaluator_id"]=_text(item.get("evaluator_id"),"evaluator_id")
        item["family"]=_text(item.get("family"),"family")
        item["kind"]=_text(item.get("kind"),"kind")
        if not isinstance(item.get("enabled"),bool):
            raise AutoEvalError(f"enabled must be bool: {item['evaluator_id']}")
        item["license_gate"]=_text(item.get("license_gate"),"license_gate")
        if item["enabled"] and item["license_gate"]!="PASS":
            raise AutoEvalError(f"enabled evaluator has uncleared license gate: {item['evaluator_id']}")
        metrics=item.get("metrics")
        if not isinstance(metrics,list) or not metrics or any(not isinstance(x,str) or not x.strip() for x in metrics):
            raise AutoEvalError(f"evaluator metrics invalid: {item['evaluator_id']}")
        if len(metrics)!=len(set(metrics)):
            raise AutoEvalError(f"duplicate evaluator metric: {item['evaluator_id']}")
        required=item.get("required_for",[])
        if not isinstance(required,list) or any(not isinstance(x,str) or not x.strip() for x in required):
            raise AutoEvalError(f"required_for invalid: {item['evaluator_id']}")
        if not isinstance(item.get("execution_ready"),bool):
            raise AutoEvalError(f"execution_ready must be bool: {item['evaluator_id']}")
        ids.append(item["evaluator_id"])
        normalized.append(item)
    if len(ids)!=len(set(ids)):
        raise AutoEvalError("duplicate evaluator_id")
    return {**registry,"evaluators":normalized}


def validate_policy(policy: dict[str,Any]) -> dict[str,Any]:
    if not isinstance(policy,dict) or policy.get("schema_version")!=1:
        raise AutoEvalError("unsupported auto-eval policy")
    stages=policy.get("stages")
    if not isinstance(stages,dict) or not stages:
        raise AutoEvalError("auto-eval policy requires stages")
    global_rules=policy.get("global_rules")
    if not isinstance(global_rules,dict):
        raise AutoEvalError("auto-eval global rules missing")
    scale=global_rules.get("metric_scale")
    if scale!={"min":0.0,"max":100.0}:
        raise AutoEvalError("auto-eval metric scale must be 0-100")
    return policy


def resolve_stage_policy(policy: dict[str,Any], stage: str) -> dict[str,Any]:
    validate_policy(policy)
    stages=policy["stages"]
    if stage not in stages:
        raise AutoEvalError(f"unknown auto-eval stage: {stage}")
    seen=set()
    def resolve(name: str) -> dict[str,Any]:
        if name in seen:
            raise AutoEvalError("auto-eval stage inheritance cycle")
        seen.add(name)
        row=deepcopy(stages[name])
        parent=row.pop("inherits",None)
        if parent is None:
            return row
        if parent not in stages:
            raise AutoEvalError(f"unknown inherited stage: {parent}")
        base=resolve(parent)
        base.update(row)
        return base
    out=resolve(stage)
    required=out.get("required_evaluators")
    weights=out.get("metric_weights")
    if not isinstance(required,list) or not required:
        raise AutoEvalError(f"stage required_evaluators missing: {stage}")
    if not isinstance(weights,dict) or not weights:
        raise AutoEvalError(f"stage metric_weights missing: {stage}")
    total=0.0
    for metric,weight in weights.items():
        _text(metric,"metric name")
        try:
            value=float(weight)
        except (TypeError,ValueError) as exc:
            raise AutoEvalError(f"invalid metric weight: {metric}") from exc
        if value<=0:
            raise AutoEvalError(f"metric weight must be positive: {metric}")
        total+=value
    if abs(total-1.0)>1e-9:
        raise AutoEvalError(f"metric weights must sum to 1.0, got {total}")
    for key in ("auto_shortlist_min","auto_retry_min"):
        value=float(out.get(key,-1))
        if not 0<=value<=100:
            raise AutoEvalError(f"invalid {key}: {stage}")
    if float(out["auto_retry_min"])>float(out["auto_shortlist_min"]):
        raise AutoEvalError(f"retry threshold exceeds shortlist threshold: {stage}")
    return out


def build_eval_plan(
    registry: dict[str,Any],
    policy: dict[str,Any],
    *,
    stage: str,
    asset_id: str,
    asset_path: str,
) -> dict[str,Any]:
    reg=validate_registry(registry)
    stage_policy=resolve_stage_policy(policy,stage)
    asset_id=_text(asset_id,"asset_id")
    asset_path=_text(asset_path,"asset_path")
    by_id={row["evaluator_id"]:row for row in reg["evaluators"]}
    required=stage_policy["required_evaluators"]
    missing=[eid for eid in required if eid not in by_id]
    disabled=[eid for eid in required if eid in by_id and not by_id[eid]["enabled"]]
    setup=[eid for eid in required if eid in by_id and by_id[eid]["enabled"] and not by_id[eid]["execution_ready"]]
    if missing:
        status="BLOCKED_REGISTRY_MISSING"
    elif disabled:
        status="BLOCKED_REQUIRED_EVALUATOR_DISABLED"
    elif setup:
        status="BLOCKED_EVALUATOR_SETUP"
    else:
        status="READY"
    return {
        "schema_version":1,
        "policy_id":policy.get("policy_id"),
        "stage":stage,
        "asset_id":asset_id,
        "asset_path":asset_path,
        "status":status,
        "required_evaluators":[deepcopy(by_id[eid]) for eid in required if eid in by_id],
        "missing_evaluators":missing,
        "disabled_evaluators":disabled,
        "setup_required":setup,
        "min_model_evaluators":int(stage_policy.get("min_model_evaluators",len(required))),
        "human_review_required":bool(stage_policy.get("human_review_required",False)),
        "production_acceptance":False,
        "publish_authority":False,
    }


def validate_receipt(receipt: dict[str,Any]) -> dict[str,Any]:
    if not isinstance(receipt,dict) or receipt.get("schema_version")!=1:
        raise AutoEvalError("unsupported evaluator receipt")
    evaluator_id=_text(receipt.get("evaluator_id"),"receipt evaluator_id")
    asset_id=_text(receipt.get("asset_id"),"receipt asset_id")
    status=_text(receipt.get("status"),"receipt status")
    metrics=receipt.get("metrics",{})
    if not isinstance(metrics,dict):
        raise AutoEvalError(f"receipt metrics must be object: {evaluator_id}")
    normalized={}
    for name,value in metrics.items():
        _text(name,"receipt metric")
        if isinstance(value,bool):
            raise AutoEvalError(f"metric cannot be bool: {name}")
        try:
            score=float(value)
        except (TypeError,ValueError) as exc:
            raise AutoEvalError(f"invalid metric score: {name}") from exc
        if not 0.0<=score<=100.0:
            raise AutoEvalError(f"metric score out of 0-100 range: {name}")
        normalized[name]=round(score,6)
    tags=receipt.get("hard_fail_tags",[])
    if not isinstance(tags,list) or any(not isinstance(x,str) or not x.strip() for x in tags):
        raise AutoEvalError(f"hard_fail_tags invalid: {evaluator_id}")
    return {
        **receipt,
        "evaluator_id":evaluator_id,
        "asset_id":asset_id,
        "status":status,
        "metrics":normalized,
        "hard_fail_tags":sorted(set(x.strip() for x in tags)),
    }


def aggregate_auto_eval(
    policy: dict[str,Any],
    *,
    stage: str,
    asset_id: str,
    receipts: list[dict[str,Any]],
    deterministic_metrics: dict[str,float] | None=None,
) -> dict[str,Any]:
    stage_policy=resolve_stage_policy(policy,stage)
    asset_id=_text(asset_id,"asset_id")
    normalized=[validate_receipt(row) for row in receipts]
    if any(row["asset_id"]!=asset_id for row in normalized):
        raise AutoEvalError("receipt asset population mismatch")
    by_eval={}
    for row in normalized:
        if row["evaluator_id"] in by_eval:
            raise AutoEvalError(f"duplicate evaluator receipt: {row['evaluator_id']}")
        by_eval[row["evaluator_id"]]=row
    required=list(stage_policy["required_evaluators"])
    missing=sorted(set(required)-set(by_eval))
    failed=sorted(
        eid for eid in required
        if eid in by_eval and by_eval[eid]["status"] not in PASS_RECEIPT_STATUSES
    )
    hard_tags=sorted({
        tag for row in normalized
        for tag in row["hard_fail_tags"]
    })
    stage_hard=set(stage_policy.get("hard_fail_tags",[]))
    triggered=sorted(stage_hard & set(hard_tags))

    base={
        "schema_version":1,
        "policy_id":policy.get("policy_id"),
        "stage":stage,
        "asset_id":asset_id,
        "required_evaluators":required,
        "received_evaluators":sorted(by_eval),
        "missing_evaluators":missing,
        "failed_evaluators":failed,
        "hard_fail_tags":hard_tags,
        "triggered_hard_fail_tags":triggered,
        "human_review_required":bool(stage_policy.get("human_review_required",False)),
        "automatic_only":not bool(stage_policy.get("human_review_required",False)),
        "production_acceptance":False,
        "publish_authority":False,
    }
    if triggered:
        return {
            **base,
            "status":"AUTO_REJECT_HARD_FAIL",
            "score":None,
            "auto_shortlist":False,
            "retry_recommended":False,
        }
    if missing or failed:
        return {
            **base,
            "status":"BLOCKED_EVALUATOR_GAP",
            "score":None,
            "auto_shortlist":False,
            "retry_recommended":False,
        }

    metrics={}
    for row in normalized:
        for name,value in row["metrics"].items():
            if name in metrics and abs(metrics[name]-value)>1e-9:
                raise AutoEvalError(f"conflicting metric values: {name}")
            metrics[name]=value
    for name,value in (deterministic_metrics or {}).items():
        if isinstance(value,bool):
            raise AutoEvalError(f"deterministic metric cannot be bool: {name}")
        score=float(value)
        if not 0<=score<=100:
            raise AutoEvalError(f"deterministic metric out of range: {name}")
        if name in metrics and abs(metrics[name]-score)>1e-9:
            raise AutoEvalError(f"conflicting deterministic metric: {name}")
        metrics[name]=round(score,6)

    weights=stage_policy["metric_weights"]
    missing_metrics=sorted(set(weights)-set(metrics))
    if missing_metrics:
        return {
            **base,
            "status":"BLOCKED_MISSING_METRICS",
            "score":None,
            "metrics":metrics,
            "missing_metrics":missing_metrics,
            "auto_shortlist":False,
            "retry_recommended":False,
        }
    score=round(sum(metrics[name]*float(weight) for name,weight in weights.items()),6)
    shortlist=float(stage_policy["auto_shortlist_min"])
    retry=float(stage_policy["auto_retry_min"])
    if score>=shortlist:
        status="AUTO_SHORTLIST"
        auto_shortlist=True
        retry_recommended=False
    elif score>=retry:
        status="AUTO_RETRY"
        auto_shortlist=False
        retry_recommended=True
    else:
        status="AUTO_REJECT_SCORE"
        auto_shortlist=False
        retry_recommended=False
    return {
        **base,
        "status":status,
        "score":score,
        "metrics":{name:metrics[name] for name in sorted(metrics)},
        "metric_weights":deepcopy(weights),
        "auto_shortlist":auto_shortlist,
        "retry_recommended":retry_recommended,
        "auto_shortlist_threshold":shortlist,
        "auto_retry_threshold":retry,
    }


def rank_auto_eval_results(results: list[dict[str,Any]]) -> list[dict[str,Any]]:
    if not isinstance(results,list) or not results:
        raise AutoEvalError("auto-eval results required")
    seen=set()
    rows=[]
    for row in results:
        if not isinstance(row,dict):
            raise AutoEvalError("auto-eval result must be object")
        asset_id=_text(row.get("asset_id"),"result asset_id")
        if asset_id in seen:
            raise AutoEvalError(f"duplicate result asset_id: {asset_id}")
        seen.add(asset_id)
        status=_text(row.get("status"),"result status")
        score=row.get("score")
        if score is not None:
            score=float(score)
            if not 0<=score<=100:
                raise AutoEvalError("result score out of range")
        rows.append({**row,"asset_id":asset_id,"status":status,"score":score})
    priority={
        "AUTO_SHORTLIST":0,
        "AUTO_RETRY":1,
        "AUTO_REJECT_SCORE":2,
        "AUTO_REJECT_HARD_FAIL":3,
        "BLOCKED_MISSING_METRICS":4,
        "BLOCKED_EVALUATOR_GAP":5,
    }
    rows.sort(key=lambda r:(priority.get(r["status"],99),-(r["score"] or -1),r["asset_id"]))
    for index,row in enumerate(rows,1):
        row["auto_rank"]=index
    return rows
