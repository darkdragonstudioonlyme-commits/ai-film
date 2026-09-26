from __future__ import annotations

import hashlib
import json
from typing import Any


class LongformReviewError(ValueError):
    pass


def canonical_digest(value: Any) -> str:
    raw=json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def validate_policy(policy: dict[str,Any]) -> dict[str,Any]:
    if not isinstance(policy,dict) or policy.get("schema_version")!=1:
        raise LongformReviewError("unsupported longform review policy")
    scale=policy.get("scale")
    if scale!={"min":0,"max":8}:
        raise LongformReviewError("longform review scale must be 0-8")
    stages=policy.get("stages")
    if not isinstance(stages,dict):
        raise LongformReviewError("longform review stages missing")
    for stage in ("longform_rough_cut","final_cut"):
        row=stages.get(stage)
        if not isinstance(row,dict) or row.get("human_review_required") is not True:
            raise LongformReviewError(f"human review required for {stage}")
        criteria=row.get("criteria")
        if not isinstance(criteria,list) or not criteria or len(criteria)!=len(set(criteria)):
            raise LongformReviewError(f"invalid criteria for {stage}")
        if "overall" not in criteria:
            raise LongformReviewError(f"overall criterion missing for {stage}")
        if row.get("production_acceptance") is not False or row.get("publish_authority") is not False:
            raise LongformReviewError(f"{stage} policy must not auto-accept/publish")
    cal=policy.get("calibration",{})
    if int(cal.get("minimum_reviewed_cuts_for_weight_suggestion",0))<2:
        raise LongformReviewError("calibration minimum too small")
    if cal.get("automatic_policy_mutation") is not False:
        raise LongformReviewError("automatic policy mutation must remain disabled")
    return policy


def build_review_packet(
    policy: dict[str,Any],
    *,
    stage: str,
    project_id: str,
    media_qc: dict[str,Any],
    auto_eval_summary_refs: list[str],
) -> dict[str,Any]:
    policy=validate_policy(policy)
    if stage not in policy["stages"]:
        raise LongformReviewError("unsupported longform review stage")
    if not isinstance(project_id,str) or not project_id.strip():
        raise LongformReviewError("project_id required")
    if not isinstance(media_qc,dict):
        raise LongformReviewError("media_qc required")
    sha=media_qc.get("sha256")
    duration=media_qc.get("duration_sec")
    if not isinstance(sha,str) or len(sha)!=64:
        raise LongformReviewError("media sha256 required")
    try:
        duration=float(duration)
    except (TypeError,ValueError) as exc:
        raise LongformReviewError("media duration required") from exc
    if duration<=0:
        raise LongformReviewError("media duration must be positive")
    if not isinstance(auto_eval_summary_refs,list) or not auto_eval_summary_refs or any(not isinstance(x,str) or not x.strip() for x in auto_eval_summary_refs):
        raise LongformReviewError("auto_eval_summary_refs required")

    criteria=list(policy["stages"][stage]["criteria"])
    identity={
        "project_id":project_id.strip(),
        "stage":stage,
        "media_sha256":sha,
        "duration_sec":round(duration,6),
        "auto_eval_summary_refs":list(auto_eval_summary_refs),
    }
    review_id="longform_"+canonical_digest(identity)[:16]
    return {
        "schema_version":1,
        "review_id":review_id,
        **identity,
        "scale":{"min":0,"max":8},
        "criteria":criteria,
        "scores":{name:None for name in criteria},
        "notes":"",
        "human_review_required":True,
        "calibration_label":True,
        "production_acceptance":False,
        "publish_authority":False,
    }


def ingest_owner_review(
    policy: dict[str,Any],
    packet: dict[str,Any],
    completed: dict[str,Any],
) -> dict[str,Any]:
    policy=validate_policy(policy)
    if not isinstance(packet,dict) or packet.get("schema_version")!=1:
        raise LongformReviewError("invalid longform review packet")
    if completed.get("review_id")!=packet.get("review_id"):
        raise LongformReviewError("review_id mismatch")
    if completed.get("media_sha256")!=packet.get("media_sha256"):
        raise LongformReviewError("media identity mismatch")
    if completed.get("scale")!={"min":0,"max":8}:
        raise LongformReviewError("completed review scale must be 0-8")
    expected=set(packet.get("criteria",[]))
    scores=completed.get("scores")
    if not isinstance(scores,dict) or set(scores)!=expected:
        raise LongformReviewError("completed score population mismatch")
    normalized={}
    for name in packet["criteria"]:
        value=scores[name]
        if isinstance(value,bool) or not isinstance(value,int) or not 0<=value<=8:
            raise LongformReviewError(f"score out of 0-8 range: {name}")
        normalized[name]=value
    notes=completed.get("notes","")
    if not isinstance(notes,str):
        raise LongformReviewError("notes must be text")
    mean=round(sum(normalized.values())/len(normalized),6)
    return {
        "schema_version":1,
        "review_id":packet["review_id"],
        "project_id":packet["project_id"],
        "stage":packet["stage"],
        "media_sha256":packet["media_sha256"],
        "duration_sec":packet["duration_sec"],
        "scale":{"min":0,"max":8},
        "scores":normalized,
        "mean_score":mean,
        "overall_score":normalized["overall"],
        "notes":notes.strip(),
        "auto_eval_summary_refs":packet["auto_eval_summary_refs"],
        "calibration_label":True,
        "production_acceptance":False,
        "publish_authority":False,
    }


def calibration_status(policy: dict[str,Any], dataset_rows: list[dict[str,Any]]) -> dict[str,Any]:
    policy=validate_policy(policy)
    unique={row.get("review_id") for row in dataset_rows if isinstance(row,dict) and row.get("calibration_label") is True}
    unique.discard(None)
    required=int(policy["calibration"]["minimum_reviewed_cuts_for_weight_suggestion"])
    return {
        "reviewed_cut_count":len(unique),
        "minimum_required":required,
        "status":"READY_FOR_WEIGHT_SUGGESTION" if len(unique)>=required else "COLLECT_MORE_LONGFORM_LABELS",
        "automatic_policy_mutation":False,
    }
