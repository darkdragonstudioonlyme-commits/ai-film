from __future__ import annotations

from copy import deepcopy
from typing import Any


class ReframePlanError(ValueError):
    pass


ALLOWED_STRATEGIES = {"RERENDER_FROM_SPEC", "OUTPAINT_OR_RERENDER"}


def _valid_sha(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def _normalize_master_asset(asset: dict[str, Any] | None, shot_id: str) -> tuple[dict[str, Any] | None, str | None]:
    if asset is None:
        return None, f"master-asset-unavailable:{shot_id}"
    for field in ("asset_id", "sha256", "manifest_sha256"):
        if not asset.get(field):
            return None, f"master-asset-invalid:{shot_id}:{field}"
    if not _valid_sha(asset["sha256"]) or not _valid_sha(asset["manifest_sha256"]):
        return None, f"master-asset-invalid-hash:{shot_id}"
    return {
        "asset_id": asset["asset_id"],
        "sha256": asset["sha256"],
        "manifest_sha256": asset["manifest_sha256"],
    }, None


def compile_reframe_plan(
    shots: list[dict[str, Any]],
    policy: dict[str, Any],
    *,
    master_assets: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    if policy.get("master_aspect") != "9:16" or policy.get("target_aspect") != "16:9":
        raise ReframePlanError("unsupported master/target aspect policy")
    shot_by_id = {shot["shot_id"]: shot for shot in shots}
    rows = policy.get("shots", [])
    policy_ids = [row.get("shot_id") for row in rows]
    if len(policy_ids) != len(set(policy_ids)) or set(policy_ids) != set(shot_by_id):
        raise ReframePlanError("reframe policy shot population mismatch")

    plan_rows = []
    blockers: list[str] = []
    fallback_count = 0
    for row in rows:
        shot_id = row["shot_id"]
        strategy = row.get("strategy")
        if strategy not in ALLOWED_STRATEGIES:
            raise ReframePlanError(f"unsafe/unsupported reframe strategy: {strategy}")
        protect = row.get("protect", [])
        if not isinstance(protect, list) or not protect:
            raise ReframePlanError(f"missing safe-area protection: {shot_id}")
        shot = shot_by_id[shot_id]
        source_asset = None
        fallback_reason = None
        if strategy == "OUTPAINT_OR_RERENDER":
            source_asset, asset_error = _normalize_master_asset(master_assets.get(shot_id), shot_id)
            if source_asset is not None:
                effective = "OUTPAINT_FROM_MASTER"
            else:
                effective = "RERENDER_FROM_SPEC"
                fallback_reason = asset_error
                fallback_count += 1
        else:
            effective = "RERENDER_FROM_SPEC"

        plan_rows.append({
            "shot_id": shot_id,
            "master_aspect": "9:16",
            "target_aspect": "16:9",
            "policy_strategy": strategy,
            "effective_strategy": effective,
            "fallback_reason": fallback_reason,
            "source_master_asset": source_asset,
            "seed": shot["seed"],
            "story_time": shot["story_time"],
            "characters": list(shot.get("characters", [])),
            "camera": deepcopy(shot["camera"]),
            "action": shot["action"],
            "protect": list(protect),
            "horizontal_intent": row.get("horizontal_intent"),
            "render_authorized": False,
        })
    return {
        "schema_version": 1,
        "project_id": policy["project_id"],
        "master_aspect": "9:16",
        "target_aspect": "16:9",
        "status": "READY_FOR_RENDER_BACKEND",
        "shots": plan_rows,
        "fallback_to_rerender_count": fallback_count,
        "blockers": blockers,
        "render_authorized": False,
    }
