import json
from .continuity import state_at
from .world_profile import validate_world_profile, world_negative_prompt, world_prompt_fragment

def compile_shot(shot, ledger, casting, aspect="9:16", world_profile=None):
    states = {cid: state_at(ledger, cid, shot["story_time"]) for cid in shot.get("characters", [])}
    profiles = {cid: casting["characters"][cid] for cid in shot.get("characters", [])}
    world = validate_world_profile(world_profile) if world_profile is not None else None
    parts = [
        f"style={shot.get('style','benchmark-neutral')}",
        f"aspect={aspect}",
        f"camera={json.dumps(shot['camera'],sort_keys=True,ensure_ascii=False)}",
        f"action={shot['action']}",
        f"character_state={json.dumps(states,sort_keys=True,ensure_ascii=False)}",
        f"casting={json.dumps(profiles,sort_keys=True,ensure_ascii=False)}",
    ]
    if world is not None:
        parts.insert(2, f"world={world_prompt_fragment(world)}")
    if shot.get("dialogue"):
        parts.append(f"dialogue={json.dumps(shot['dialogue'],sort_keys=True,ensure_ascii=False)}")
    negative = "identity drift, costume drift, extra fingers, text artifacts"
    if world is not None:
        negative += ", " + world_negative_prompt(world)
    result = {
        "shot_id": shot["shot_id"],
        "story_time": shot["story_time"],
        "dialogue_id": shot.get("dialogue_id"),
        "prompt": " | ".join(parts),
        "negative_prompt": negative,
        "references": [profiles[c].get("face_ref") for c in profiles if profiles[c].get("face_ref")],
        "seed": shot["seed"],
        "aspect": aspect,
    }
    if world is not None:
        result["world_profile_id"] = world["profile_id"]
    return result