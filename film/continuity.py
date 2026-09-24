from copy import deepcopy

def _apply(state, event):
    kind = event["type"]
    if kind in {"costume", "hair", "emotion", "location"}:
        state[kind] = event["value"]
    elif kind in {"injury_add", "injury_update"}:
        state.setdefault("injuries", {})[event["part"]] = event["desc"]
    elif kind == "injury_remove":
        state.setdefault("injuries", {}).pop(event["part"], None)
    elif kind == "costume_damage":
        state.setdefault("costume_damage", {})[event["part"]] = event["desc"]
    elif kind == "prop_add":
        state.setdefault("props", {})[event["prop"]] = event.get("state", "present")
    elif kind == "prop_remove":
        state.setdefault("props", {}).pop(event["prop"], None)
    return state

def state_at(ledger, char_id, story_time):
    char = ledger["characters"][char_id]
    state = deepcopy(char.get("baseline", {}))
    state["identity"] = deepcopy(char.get("identity", {}))
    found = False
    for point in ledger.get("timeline", []):
        for event in point.get("events", []):
            if event.get("char") == char_id:
                _apply(state, event)
        if point["t"] == story_time:
            found = True
            break
    if not found:
        raise KeyError(f"unknown story_time: {story_time}")
    return state
