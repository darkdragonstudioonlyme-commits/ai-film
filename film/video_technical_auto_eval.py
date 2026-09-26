from __future__ import annotations

from typing import Any


class VideoTechnicalAutoEvalError(ValueError):
    pass


def build_receipt(
    *,
    asset_id: str,
    frame_count: int,
    black_frame_count: int,
    freeze_transition_count: int,
    mean_frame_delta: float,
    max_frame_delta: float,
    mean_luma: float,
    ffmpeg_path: str,
) -> dict[str,Any]:
    if not isinstance(asset_id,str) or not asset_id:
        raise VideoTechnicalAutoEvalError("asset_id required")
    if not isinstance(frame_count,int) or frame_count<=0:
        raise VideoTechnicalAutoEvalError("frame_count must be positive")
    if not isinstance(black_frame_count,int) or not 0<=black_frame_count<=frame_count:
        raise VideoTechnicalAutoEvalError("invalid black_frame_count")
    transitions=max(0,frame_count-1)
    if not isinstance(freeze_transition_count,int) or not 0<=freeze_transition_count<=transitions:
        raise VideoTechnicalAutoEvalError("invalid freeze_transition_count")
    for name,value in (
        ("mean_frame_delta",mean_frame_delta),
        ("max_frame_delta",max_frame_delta),
        ("mean_luma",mean_luma),
    ):
        try: value=float(value)
        except (TypeError,ValueError) as exc:
            raise VideoTechnicalAutoEvalError(f"invalid {name}") from exc
        if value<0:
            raise VideoTechnicalAutoEvalError(f"{name} must be nonnegative")
    black_ratio=black_frame_count/frame_count
    freeze_ratio=freeze_transition_count/transitions if transitions else 0.0
    tags=[]
    if black_ratio>=0.80:
        tags.append("BLACK_OR_EMPTY_VIDEO")
    return {
        "schema_version":1,
        "evaluator_id":"deterministic-video-qc",
        "asset_id":asset_id,
        "status":"PASS_DETERMINISTIC_QC",
        "metrics":{
            "decode_integrity":100.0,
            "non_black_frames":round((1.0-black_ratio)*100.0,6),
        },
        "hard_fail_tags":tags,
        "evidence":{
            "frame_count":frame_count,
            "black_frame_count":black_frame_count,
            "black_frame_ratio":round(black_ratio,6),
            "freeze_transition_count":freeze_transition_count,
            "freeze_transition_ratio":round(freeze_ratio,6),
            "mean_frame_delta_0_255":round(float(mean_frame_delta),6),
            "max_frame_delta_0_255":round(float(max_frame_delta),6),
            "mean_luma_0_255":round(float(mean_luma),6),
            "ffmpeg":ffmpeg_path,
        },
        "supplemental_only":True,
        "counts_toward_min_model_evaluators":False,
        "production_acceptance":False,
        "publish_authority":False,
    }
