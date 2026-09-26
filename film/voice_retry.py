from __future__ import annotations

from copy import deepcopy
from typing import Any

from .voice_eval import canonical_digest


class VoiceRetryError(ValueError):
    pass


def build_voice_retry_request(
    source_request: dict[str, Any],
    *,
    source_asset_id: str,
    source_status: str,
    source_score: float,
    retry_index: int = 1,
) -> dict[str, Any]:
    if source_status != "AUTO_RETRY":
        raise VoiceRetryError("only AUTO_RETRY sources may produce retry requests")
    if source_request.get("language") != "zh-CN":
        raise VoiceRetryError("current retry policy is only for demonstrated zh-CN cue overflow")
    if source_request.get("reference_audio") is not None:
        raise VoiceRetryError("reference audio must remain disabled")
    if source_request.get("mode") != "voice_design":
        raise VoiceRetryError("retry requires voice_design mode")
    if not isinstance(retry_index,int) or retry_index < 1:
        raise VoiceRetryError("retry_index must be positive")

    cue=float(source_request["cue_budget_sec"])
    if cue <= 0:
        raise VoiceRetryError("invalid cue budget")

    desc=str(source_request["voice_design_description"])
    if "medium-slow pace" not in desc:
        raise VoiceRetryError("source pace premise drift")
    retry_desc=desc.replace(
        "medium-slow pace",
        "concise slightly brisk pace, clear diction, natural phrasing, no rushed syllables",
    )
    out=deepcopy(source_request)
    out.pop("request_id",None)
    out.pop("request_digest",None)
    out.update({
        "schema_version":1,
        "retry_of_request_id":source_request["request_id"],
        "retry_source_asset_id":source_asset_id,
        "retry_source_status":source_status,
        "retry_source_score":round(float(source_score),6),
        "retry_index":retry_index,
        "retry_reason":"CUE_OVERFLOW",
        "voice_design_description":retry_desc,
        "model_input_text":f"({retry_desc}){source_request['target_text']}",
        "seed":int(source_request["seed"]) + 1000 * retry_index,
        "execution_permitted":False,
        "reference_audio":None,
        "production_acceptance":False,
        "publish_authority":False,
    })
    digest_source={k:v for k,v in out.items() if k not in {"production_acceptance","publish_authority"}}
    digest=canonical_digest(digest_source)
    out["request_digest"]=digest
    out["request_id"]="voxretry_"+digest[:16]
    return out


def build_retry_plan(
    *,
    requests: list[dict[str,Any]],
    auto_eval_results: list[dict[str,Any]],
) -> dict[str,Any]:
    by_blind={row["blind_id"]:row for row in requests}
    retries=[]
    for result in auto_eval_results:
        if result.get("status")!="AUTO_RETRY":
            continue
        asset_id=result.get("asset_id")
        source=by_blind.get(asset_id)
        if source is None:
            raise VoiceRetryError(f"missing source request for {asset_id}")
        retries.append(build_voice_retry_request(
            source,
            source_asset_id=asset_id,
            source_status=result["status"],
            source_score=float(result["score"]),
        ))
    retries.sort(key=lambda row:row["request_id"])
    return {
        "schema_version":1,
        "status":"READY_GPU_EXECUTION_PENDING",
        "retry_count":len(retries),
        "requests":retries,
        "human_review_required":False,
        "production_acceptance":False,
        "publish_authority":False,
        "new_resource_creation_authorized":False,
    }
