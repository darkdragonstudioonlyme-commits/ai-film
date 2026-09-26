from __future__ import annotations

from collections import defaultdict
from typing import Any


class OwnerReviewError(ValueError):
    pass


def _score_rows(rows: Any, *, kind: str, expected_ids: set[str]) -> list[dict[str, Any]]:
    if not isinstance(rows, list):
        raise OwnerReviewError(f"{kind} scores must be a list")
    normalized=[]
    seen=set()
    for row in rows:
        if not isinstance(row, dict) or row.get("kind")!=kind:
            raise OwnerReviewError(f"invalid {kind} score row")
        item_id=row.get("id")
        if not isinstance(item_id,str) or not item_id:
            raise OwnerReviewError(f"{kind} score id required")
        if item_id in seen:
            raise OwnerReviewError(f"duplicate {kind} score id: {item_id}")
        seen.add(item_id)
        score=row.get("score")
        if isinstance(score,bool) or not isinstance(score,int) or not 0<=score<=8:
            raise OwnerReviewError(f"{kind} score out of 0-8 range: {item_id}")
        notes=row.get("notes","")
        if not isinstance(notes,str):
            raise OwnerReviewError(f"{kind} notes must be text: {item_id}")
        normalized.append({"kind":kind,"id":item_id,"score":score,"notes":notes.strip()})
    missing=sorted(expected_ids-seen)
    extra=sorted(seen-expected_ids)
    if missing or extra:
        raise OwnerReviewError(f"{kind} score population mismatch missing={missing} extra={extra}")
    return sorted(normalized,key=lambda row:row["id"])


def validate_owner_review(
    payload: dict[str,Any],
    *,
    expected_voice_ids: set[str],
    expected_motion_ids: set[str] | None=None,
) -> dict[str,Any]:
    if not isinstance(payload,dict) or payload.get("schema_version")!=1:
        raise OwnerReviewError("unsupported owner review schema")
    scale=payload.get("scale")
    if scale!={"min":0,"max":8}:
        raise OwnerReviewError("owner review scale must be 0-8")
    motion_ids={"motion_A","motion_B"} if expected_motion_ids is None else set(expected_motion_ids)
    voice=_score_rows(payload.get("voice"),kind="voice",expected_ids=set(expected_voice_ids))
    motion=_score_rows(payload.get("motion"),kind="motion",expected_ids=motion_ids)
    return {
        "schema_version":1,
        "review_id":str(payload.get("review_id") or "owner-review"),
        "scale":{"min":0,"max":8},
        "voice":voice,
        "motion":motion,
        "score_set_complete":True,
    }


def summarize_voice(
    normalized: dict[str,Any],
    *,
    voice_metadata: dict[str,dict[str,Any]],
) -> dict[str,Any]:
    by_character=defaultdict(list)
    by_language=defaultdict(list)
    rows=[]
    for row in normalized["voice"]:
        meta=voice_metadata.get(row["id"])
        if meta is None:
            raise OwnerReviewError(f"missing voice metadata: {row['id']}")
        item={**row,**meta}
        rows.append(item)
        by_character[str(meta["character_id"])].append(row["score"])
        by_language[str(meta["language"])].append(row["score"])
    def stats(groups):
        return {
            k:{
                "sample_count":len(v),
                "total":sum(v),
                "mean":round(sum(v)/len(v),6),
            }
            for k,v in sorted(groups.items())
        }
    scores=[r["score"] for r in rows]
    return {
        "sample_count":len(rows),
        "overall_mean":round(sum(scores)/len(scores),6),
        "by_character":stats(by_character),
        "by_language":stats(by_language),
        "rows":rows,
    }


def unblind_and_summarize_motion(
    normalized: dict[str,Any],
    *,
    motion_mapping: dict[str,str],
) -> dict[str,Any]:
    ids={row["id"] for row in normalized["motion"]}
    if set(motion_mapping)!=ids:
        raise OwnerReviewError("motion mapping population mismatch")
    rows=[]
    for row in normalized["motion"]:
        source=motion_mapping.get(row["id"])
        if not isinstance(source,str) or not source.strip():
            raise OwnerReviewError(f"invalid motion mapping: {row['id']}")
        rows.append({**row,"reference_model_id":source.strip()})
    rows.sort(key=lambda r:(-r["score"],r["id"]))
    return {
        "sample_count":len(rows),
        "rows":rows,
        "selection_authorized":False,
        "production_acceptance":False,
    }