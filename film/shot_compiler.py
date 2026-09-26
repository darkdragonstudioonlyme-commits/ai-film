import json
from .continuity import state_at
from .world_profile import validate_world_profile, world_negative_prompt, world_prompt_fragment, world_visual_prompt_fragment



def compile_visual_prompt(shot, ledger, casting, aspect="9:16", style_override=None, world_profile=None):
    states = {cid: state_at(ledger, cid, shot["story_time"]) for cid in shot.get("characters", [])}
    profiles = {cid: casting["characters"][cid] for cid in shot.get("characters", [])}
    style = style_override or shot.get("style", "benchmark-neutral")
    camera = shot["camera"]
    parts = [
        f"Visual style: {style}.",
        f"Portrait-friendly {aspect} cinematic frame.",
        f"Camera: {camera.get('framing','shot')}, {camera.get('lens_mm','natural')}mm lens, {camera.get('movement','static')} movement.",
        f"Scene action: {shot['action']}",
    ]
    if world_profile is not None:
        parts.append(world_visual_prompt_fragment(world_profile))
    for cid in shot.get("characters", []):
        profile = profiles[cid]
        state = states[cid]
        visual = profile.get("visual", "").strip()
        char = [f"{cid.capitalize()} is a {visual}." if visual else f"Character {cid.capitalize()}."]
        costume = state.get("costume")
        if isinstance(costume, str) and costume.strip():
            char.append(f"Wearing {costume.strip()}.")
        for field, label in (("costume_damage","Costume detail"),("injuries","Visible injury")):
            value = state.get(field)
            if isinstance(value, dict):
                vals = [
                    f"{str(k).replace('_',' ')} {str(v).strip()}"
                    for k,v in value.items() if str(v).strip()
                ]
                if vals:
                    char.append(label + ": " + "; ".join(vals) + ".")
        props = state.get("props")
        if isinstance(props, dict):
            vals = [
                f"{str(k).replace('_',' ')} {str(v).strip()}"
                for k,v in props.items() if str(v).strip()
            ]
            if vals:
                char.append("Scene props include " + "; ".join(vals) + ".")
        parts.append(" ".join(char))
    parts.append(
        "Image only. No written words, subtitles, captions, dialogue text, speech bubbles, "
        "infographic panels, UI overlays, labels, logos, watermarks or typography."
    )
    return " ".join(parts)

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
