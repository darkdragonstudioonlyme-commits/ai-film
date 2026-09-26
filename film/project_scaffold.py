from __future__ import annotations

from copy import deepcopy
from typing import Any

from .world_profile import validate_world_profile


class ScaffoldError(ValueError):
    pass


FORBIDDEN_PATH_PARTS={"runtime","compiled","delivery","artifacts","run-evidence","secrets","credentials"}
LANGUAGES=("en","zh-CN","vi")


def build_project_scaffold(
    *,
    project_id: str,
    title: str,
    source_packet: dict[str, Any],
    target_seconds: float=75.0,
    master_aspect: str="9:16",
    secondary_aspect: str="16:9",
    world_profile: dict[str, Any] | None=None,
) -> dict[str, Any]:
    if not project_id or "/" in project_id or ".." in project_id:
        raise ScaffoldError("invalid project_id")
    if not title.strip():
        raise ScaffoldError("title required")
    if source_packet.get("tool_authority") is not False or source_packet.get("publish_authority") is not False:
        raise ScaffoldError("source packet authority must be false")
    if not 60.0 <= float(target_seconds) <= 180.0:
        raise ScaffoldError("unsupported scaffold duration")
    world = validate_world_profile(world_profile) if world_profile is not None else None
    project={
        "schema_version":1,
        "project_id":project_id,
        "title":title,
        "status":"DRAFT_NO_GENERATED_MEDIA",
        "target_seconds":float(target_seconds),
        "master_aspect":master_aspect,
        "secondary_aspect":secondary_aspect,
        "languages":list(LANGUAGES),
        "generated_media_status":"EMPTY",
        "runtime_status":"NOT_INITIALIZED",
        "publish_clearance":"NOT_EVALUATED",
    }
    if world is not None:
        project["world_profile_id"] = world["profile_id"]
    files={
        "project.json":project,
        "source/source_packet.json":deepcopy(source_packet),
        "story/screenplay.json":{
            "schema_version":1,"project_id":project_id,"status":"DRAFT_EMPTY","master_language":"en","scenes":[]
        },
        "continuity.json":{
            "schema_version":1,"project_id":project_id,"status":"DRAFT_EMPTY","characters":{},"timeline":[]
        },
        "casting.json":{
            "schema_version":1,"project_id":project_id,"status":"DRAFT_EMPTY","characters":{}
        },
        "shots/shots.json":{
            "schema_version":1,"project_id":project_id,"status":"DRAFT_EMPTY","shots":[]
        },
        "timing/timing.json":{
            "schema_version":1,"project_id":project_id,"status":"DRAFT_EMPTY","fps":24,"shots":[],"dialogue_cues":[]
        },
        "localization/dialogue_bundle.json":{
            "schema_version":1,"project_id":project_id,"status":"DRAFT_EMPTY","master_language":"en","languages":list(LANGUAGES),"lines":[]
        },
        "framing/reframe_policy.json":{
            "schema_version":1,"project_id":project_id,"status":"DRAFT_EMPTY","master_aspect":master_aspect,"target_aspect":secondary_aspect,"shots":[],"render_authorized":False
        },
        "rights/publication_policy.json":{
            "schema_version":1,"project_id":project_id,"status":"DRAFT","required_subjects":[{"subject_type":"source","subject_id":"project-source"}],"publication_action_requires_owner_approval":True
        },
        "rights/rights_register.json":{
            "schema_version":1,"project_id":project_id,"status":"INCOMPLETE_BLOCK_PUBLICATION","records":[{
                "rights_id":"source-ingested","subject_type":"source","subject_id":"project-source",
                "status":source_packet["rights"]["status"],
                "allowed_uses":list(source_packet["rights"]["allowed_uses"]),
                "evidence_ref":source_packet["evidence"]["ref"],
            }]
        },
    }
    if world is not None:
        files["world/world_profile.json"] = deepcopy(world)
    for path in files:
        parts=set(path.split("/"))
        if parts & FORBIDDEN_PATH_PARTS:
            raise ScaffoldError(f"forbidden scaffold path: {path}")
    return {"schema_version":1,"project_id":project_id,"status":"SCAFFOLD_READY_EMPTY_MEDIA","files":files}