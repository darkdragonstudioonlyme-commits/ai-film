from __future__ import annotations

from copy import deepcopy
from typing import Any


class ProductionStateError(ValueError):
    pass


SHOT_TRANSITIONS = {
    "PLANNED": {"READY"},
    "READY": {"GENERATING", "CANCELLED"},
    "GENERATING": {"REVIEW", "READY", "CANCELLED"},
    "REVIEW": {"APPROVED", "READY", "CANCELLED"},
    "APPROVED": {"READY"},
    "CANCELLED": {"READY"},
}

TAKE_TRANSITIONS = {
    "GENERATED": {"QC_PENDING"},
    "QC_PENDING": {"ACCEPTED", "REJECTED"},
    "ACCEPTED": set(),
    "REJECTED": set(),
}


def new_shot(shot_id: str, spec_revision: int) -> dict[str, Any]:
    if not shot_id or spec_revision < 1:
        raise ProductionStateError("invalid shot identity/revision")
    return {
        "shot_id": shot_id,
        "spec_revision": int(spec_revision),
        "state": "PLANNED",
        "version": 1,
        "selection_revision": 0,
        "selected_take_id": None,
    }


def transition_shot(
    shot: dict[str, Any],
    *,
    expected_version: int,
    to_state: str,
) -> dict[str, Any]:
    if int(shot.get("version", 0)) != int(expected_version):
        raise ProductionStateError("stale shot version")
    current = shot.get("state")
    if to_state not in SHOT_TRANSITIONS.get(current, set()):
        raise ProductionStateError(f"invalid shot transition: {current}->{to_state}")
    out = deepcopy(shot)
    out["state"] = to_state
    out["version"] = int(shot["version"]) + 1
    return out


def revise_shot_spec(
    shot: dict[str, Any],
    *,
    expected_version: int,
    new_spec_revision: int,
) -> dict[str, Any]:
    if int(shot.get("version", 0)) != int(expected_version):
        raise ProductionStateError("stale shot version")
    if int(new_spec_revision) <= int(shot.get("spec_revision", 0)):
        raise ProductionStateError("spec revision must increase")
    out = deepcopy(shot)
    out["spec_revision"] = int(new_spec_revision)
    out["version"] = int(shot["version"]) + 1
    out["state"] = "READY"
    out["selected_take_id"] = None
    out["selection_revision"] = int(shot.get("selection_revision", 0))
    return out


def new_take(
    *,
    take_id: str,
    shot_id: str,
    shot_spec_revision: int,
    asset_id: str,
    manifest_sha256: str,
) -> dict[str, Any]:
    if not all((take_id, shot_id, asset_id)):
        raise ProductionStateError("invalid take identity")
    if len(manifest_sha256) != 64:
        raise ProductionStateError("invalid take manifest sha")
    return {
        "take_id": take_id,
        "shot_id": shot_id,
        "shot_spec_revision": int(shot_spec_revision),
        "asset_id": asset_id,
        "manifest_sha256": manifest_sha256,
        "state": "GENERATED",
        "version": 1,
    }


def transition_take(
    take: dict[str, Any],
    *,
    expected_version: int,
    to_state: str,
) -> dict[str, Any]:
    if int(take.get("version", 0)) != int(expected_version):
        raise ProductionStateError("stale take version")
    current = take.get("state")
    if to_state not in TAKE_TRANSITIONS.get(current, set()):
        raise ProductionStateError(f"invalid take transition: {current}->{to_state}")
    out = deepcopy(take)
    out["state"] = to_state
    out["version"] = int(take["version"]) + 1
    return out


def select_take(
    shot: dict[str, Any],
    take: dict[str, Any],
    *,
    expected_shot_version: int,
    actor: str,
    previous_selection: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    if int(shot.get("version", 0)) != int(expected_shot_version):
        raise ProductionStateError("stale shot version")
    if shot.get("state") not in {"REVIEW", "APPROVED"}:
        raise ProductionStateError("shot must be in REVIEW/APPROVED before selection")
    if take.get("state") != "ACCEPTED":
        raise ProductionStateError("take must be ACCEPTED before selection")
    if take.get("shot_id") != shot.get("shot_id"):
        raise ProductionStateError("take belongs to different shot")
    if int(take.get("shot_spec_revision", 0)) != int(shot.get("spec_revision", 0)):
        raise ProductionStateError("take was generated for stale shot spec revision")
    if not actor:
        raise ProductionStateError("selection actor required")
    prior_revision = int(shot.get("selection_revision", 0))
    if previous_selection is not None:
        if int(previous_selection.get("selection_revision", -1)) != prior_revision:
            raise ProductionStateError("selection history does not match shot")
        if previous_selection.get("shot_id") != shot.get("shot_id"):
            raise ProductionStateError("selection history belongs to different shot")
    selection_revision = prior_revision + 1
    selection = {
        "selection_id": f"{shot['shot_id']}:selection:{selection_revision}",
        "shot_id": shot["shot_id"],
        "shot_spec_revision": shot["spec_revision"],
        "selection_revision": selection_revision,
        "take_id": take["take_id"],
        "asset_id": take["asset_id"],
        "manifest_sha256": take["manifest_sha256"],
        "actor": actor,
        "supersedes_selection_id": None if previous_selection is None else previous_selection["selection_id"],
        "immutable": True,
    }
    updated = deepcopy(shot)
    updated["selected_take_id"] = take["take_id"]
    updated["selection_revision"] = selection_revision
    updated["version"] = int(shot["version"]) + 1
    updated["state"] = "APPROVED"
    return updated, selection
