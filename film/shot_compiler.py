import json
from .continuity import state_at

def compile_shot(shot, ledger, casting, aspect="9:16"):
    states = {cid: state_at(ledger, cid, shot["story_time"]) for cid in shot.get("characters", [])}
    profiles = {cid: casting["characters"][cid] for cid in shot.get("characters", [])}
    parts = [
        f"style={shot.get('style','benchmark-neutral')}",
        f"aspect={aspect}",
        f"camera={json.dumps(shot['camera'],sort_keys=True,ensure_ascii=False)}",
        f"action={shot['action']}",
        f"character_state={json.dumps(states,sort_keys=True,ensure_ascii=False)}",
        f"casting={json.dumps(profiles,sort_keys=True,ensure_ascii=False)}",
    ]
    if shot.get("dialogue"):
        parts.append(f"dialogue={json.dumps(shot['dialogue'],sort_keys=True,ensure_ascii=False)}")
    return {
        "shot_id": shot["shot_id"],
        "story_time": shot["story_time"],
        "dialogue_id": shot.get("dialogue_id"),
        "prompt": " | ".join(parts),
        "negative_prompt": "identity drift, costume drift, extra fingers, text artifacts",
        "references": [profiles[c].get("face_ref") for c in profiles if profiles[c].get("face_ref")],
        "seed": shot["seed"],
        "aspect": aspect,
    }
