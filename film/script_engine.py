from __future__ import annotations

from copy import deepcopy
from typing import Any


class ScriptContractError(ValueError):
    pass


ALLOWED_SOURCE_KINDS = {"ORIGINAL_PROJECT", "ADAPTATION", "PUBLIC_DOMAIN"}
ALLOWED_ADAPTATION_RIGHTS = {"LICENSED", "CONSENTED", "PUBLIC_DOMAIN"}


def _valid_sha(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def validate_screenplay(
    screenplay: dict[str, Any],
    *,
    min_duration_sec: float = 60.0,
    max_duration_sec: float = 90.0,
) -> dict[str, Any]:
    required = {"project_id", "title", "master_language", "target_duration_sec", "source", "scenes"}
    missing = sorted(required - set(screenplay))
    if missing:
        raise ScriptContractError(f"screenplay missing fields: {missing}")
    if screenplay["master_language"] != "en":
        raise ScriptContractError("slice master language must be en")
    target = float(screenplay["target_duration_sec"])
    if not min_duration_sec <= target <= max_duration_sec:
        raise ScriptContractError("target duration outside vertical-slice range")

    source = screenplay["source"]
    kind = source.get("kind")
    if kind not in ALLOWED_SOURCE_KINDS:
        raise ScriptContractError("invalid source kind")
    for field in ("rights_id", "rights_status", "evidence_ref", "source_identity_sha256"):
        if not source.get(field):
            raise ScriptContractError(f"source missing {field}")
    if not _valid_sha(source["source_identity_sha256"]):
        raise ScriptContractError("invalid source identity sha256")
    if kind == "ORIGINAL_PROJECT" and source["rights_status"] != "ORIGINAL":
        raise ScriptContractError("original project must have ORIGINAL rights status")
    if kind in {"ADAPTATION", "PUBLIC_DOMAIN"} and source["rights_status"] not in ALLOWED_ADAPTATION_RIGHTS:
        raise ScriptContractError("adaptation/public-domain source not rights-cleared")

    scenes = screenplay["scenes"]
    if not isinstance(scenes, list) or not scenes:
        raise ScriptContractError("scenes must be non-empty list")
    scene_ids: set[str] = set()
    beat_ids: set[str] = set()
    dialogue_ids: set[str] = set()
    total = 0.0
    normalized_scenes = []

    for scene in scenes:
        scene_id = scene.get("scene_id")
        if not scene_id or scene_id in scene_ids:
            raise ScriptContractError("invalid/duplicate scene_id")
        scene_ids.add(scene_id)
        for field in ("heading", "purpose", "conflict", "turn", "character_objective"):
            if not str(scene.get(field, "")).strip():
                raise ScriptContractError(f"scene {scene_id} missing {field}")
        duration = float(scene.get("estimated_duration_sec", 0))
        if duration <= 0:
            raise ScriptContractError(f"scene {scene_id} invalid duration")
        beats = scene.get("beats", [])
        if not isinstance(beats, list) or not beats:
            raise ScriptContractError(f"scene {scene_id} has no beats")
        cursor = 0.0
        normalized_beats = []
        for beat in beats:
            beat_id = beat.get("beat_id")
            if not beat_id or beat_id in beat_ids:
                raise ScriptContractError("invalid/duplicate beat_id")
            beat_ids.add(beat_id)
            start = float(beat.get("start_sec", -1))
            end = float(beat.get("end_sec", -1))
            if abs(start - cursor) > 1e-9 or end <= start:
                raise ScriptContractError(f"scene {scene_id} beat timeline not contiguous")
            if not str(beat.get("action", "")).strip():
                raise ScriptContractError(f"beat {beat_id} missing action")
            normalized_beats.append({**deepcopy(beat), "start_sec": start, "end_sec": end})
            cursor = end
        if abs(cursor - duration) > 1e-9:
            raise ScriptContractError(f"scene {scene_id} beat duration mismatch")

        dialogues = scene.get("dialogue", [])
        for line in dialogues:
            dialogue_id = line.get("dialogue_id")
            if not dialogue_id or dialogue_id in dialogue_ids:
                raise ScriptContractError("invalid/duplicate dialogue_id")
            dialogue_ids.add(dialogue_id)
            if not line.get("speaker_id") or not str(line.get("master_text", "")).strip():
                raise ScriptContractError(f"invalid dialogue line: {dialogue_id}")
            if line.get("language") != screenplay["master_language"]:
                raise ScriptContractError(f"dialogue language mismatch: {dialogue_id}")

        normalized_scenes.append({**deepcopy(scene), "beats": normalized_beats, "estimated_duration_sec": duration})
        total += duration

    if abs(total - target) > 1e-9:
        raise ScriptContractError("screenplay scene duration does not match target")
    return {
        "schema_version": 1,
        "project_id": screenplay["project_id"],
        "title": screenplay["title"],
        "master_language": screenplay["master_language"],
        "target_duration_sec": target,
        "source": deepcopy(source),
        "scenes": normalized_scenes,
        "scene_ids": sorted(scene_ids),
        "beat_ids": sorted(beat_ids),
        "dialogue_ids": sorted(dialogue_ids),
    }



def validate_source_rights(
    screenplay: dict[str, Any],
    rights_records: list[dict[str, Any]],
) -> dict[str, Any]:
    normalized = validate_screenplay(screenplay)
    source = normalized["source"]
    rights_id = source["rights_id"]
    matches = [row for row in rights_records if row.get("rights_id") == rights_id]
    if len(matches) != 1:
        raise ScriptContractError(f"source rights record mismatch: {rights_id}")
    record = matches[0]
    if record.get("subject_type") != source.get("subject_type"):
        raise ScriptContractError("source rights subject_type mismatch")
    if record.get("subject_id") != source.get("subject_id"):
        raise ScriptContractError("source rights subject_id mismatch")
    if record.get("status") != source.get("rights_status"):
        raise ScriptContractError("source rights status mismatch")
    if "COMMERCIAL_PUBLICATION" not in record.get("allowed_uses", []):
        raise ScriptContractError("source rights do not permit commercial publication")
    return normalized

def validate_screenplay_against_shots(
    screenplay: dict[str, Any],
    shots: list[dict[str, Any]],
) -> dict[str, Any]:
    normalized = validate_screenplay(screenplay)
    script_dialogue = set(normalized["dialogue_ids"])
    shot_dialogue = {shot["dialogue_id"] for shot in shots if shot.get("dialogue_id")}
    if script_dialogue != shot_dialogue:
        raise ScriptContractError(
            f"screenplay/shot dialogue mismatch script={sorted(script_dialogue)} shots={sorted(shot_dialogue)}"
        )
    speakers = {
        line["dialogue_id"]: line["speaker_id"]
        for scene in normalized["scenes"]
        for line in scene.get("dialogue", [])
    }
    for shot in shots:
        dialogue_id = shot.get("dialogue_id")
        if dialogue_id and speakers[dialogue_id] not in shot.get("characters", []):
            raise ScriptContractError(f"screenplay speaker absent from shot: {dialogue_id}")
    return normalized
