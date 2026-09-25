from __future__ import annotations

from copy import deepcopy
from typing import Any


class AudioCueError(ValueError):
    pass


KINDS = {"ambience", "sfx", "music"}
RIGHTS = {"UNKNOWN", "PENDING", "CLEARED", "BLOCKED", "REVOKED"}


def _valid_sha(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def validate_cue_sheet(sheet: dict[str, Any], *, total_duration_sec: float) -> dict[str, Any]:
    if total_duration_sec <= 0:
        raise AudioCueError("total duration must be positive")
    cues = sheet.get("cues")
    if not isinstance(cues, list):
        raise AudioCueError("cues must be a list")
    seen: set[str] = set()
    blockers: list[str] = []
    normalized: list[dict[str, Any]] = []
    for cue in cues:
        cue_id = cue.get("cue_id")
        kind = cue.get("kind")
        if not cue_id or cue_id in seen:
            raise AudioCueError("invalid/duplicate cue_id")
        seen.add(cue_id)
        if kind not in KINDS:
            raise AudioCueError(f"unsupported cue kind: {kind}")
        start = float(cue.get("start_sec", -1))
        end = float(cue.get("end_sec", -1))
        if start < 0 or end <= start or end > total_duration_sec:
            raise AudioCueError(f"cue outside timeline: {cue_id}")
        rights_status = cue.get("rights_status", "UNKNOWN")
        if rights_status not in RIGHTS:
            raise AudioCueError(f"invalid rights status: {cue_id}")
        source_status = cue.get("source_status", "PENDING_ASSET")
        asset = cue.get("asset")
        rights_ref = cue.get("rights_ref")
        if source_status == "BOUND":
            if not isinstance(asset, dict):
                raise AudioCueError(f"bound cue missing asset: {cue_id}")
            for field in ("asset_id", "sha256", "manifest_sha256"):
                if not asset.get(field):
                    raise AudioCueError(f"bound cue missing {field}: {cue_id}")
            if not _valid_sha(asset["sha256"]) or not _valid_sha(asset["manifest_sha256"]):
                raise AudioCueError(f"bound cue invalid hash: {cue_id}")
        elif source_status != "PENDING_ASSET":
            raise AudioCueError(f"invalid source status: {cue_id}")

        if cue.get("required_for_final", True):
            if source_status != "BOUND":
                blockers.append(f"missing-audio-asset:{cue_id}")
            if rights_status != "CLEARED":
                blockers.append(f"rights-not-cleared:{cue_id}:{rights_status}")
            if rights_status == "CLEARED" and not rights_ref:
                blockers.append(f"rights-evidence-missing:{cue_id}")

        normalized.append({
            **deepcopy(cue),
            "start_sec": start,
            "end_sec": end,
            "duration_sec": round(end - start, 6),
        })

    normalized.sort(key=lambda row: (row["start_sec"], row["kind"], row["cue_id"]))
    return {
        "schema_version": 1,
        "project_id": sheet.get("project_id"),
        "total_duration_sec": float(total_duration_sec),
        "status": "READY" if not blockers else "BLOCKED_MISSING_ASSETS_OR_RIGHTS",
        "cues": normalized,
        "blockers": sorted(set(blockers)),
    }
