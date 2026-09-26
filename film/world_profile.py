from __future__ import annotations

from copy import deepcopy
import json
from typing import Any


class WorldProfileError(ValueError):
    pass


SETTING_FAMILIES = {"historical_china", "european_cinema", "custom"}
LIST_FIELDS = (
    "visual_language",
    "wardrobe_rules",
    "architecture_rules",
    "prop_rules",
    "environment_rules",
    "cinematography",
    "avoid",
)


def _nonempty_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise WorldProfileError(f"{field} must be non-empty text")
    return value.strip()


def _clean_list(profile: dict[str, Any], field: str) -> list[str]:
    rows = profile.get(field, [])
    if not isinstance(rows, list) or any(not isinstance(x, str) or not x.strip() for x in rows):
        raise WorldProfileError(f"{field} must be a list of non-empty strings")
    cleaned = [x.strip() for x in rows]
    if len(cleaned) != len(set(cleaned)):
        raise WorldProfileError(f"{field} contains duplicates")
    return cleaned


def validate_world_profile(profile: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(profile, dict):
        raise WorldProfileError("world profile must be an object")
    out = deepcopy(profile)
    if out.get("schema_version") != 1:
        raise WorldProfileError("unsupported world profile schema_version")
    out["profile_id"] = _nonempty_text(out.get("profile_id"), "profile_id")
    family = _nonempty_text(out.get("setting_family"), "setting_family")
    if family not in SETTING_FAMILIES:
        raise WorldProfileError(f"unsupported setting_family: {family}")
    out["setting_family"] = family
    out["country"] = _nonempty_text(out.get("country"), "country")
    out["region"] = _nonempty_text(out.get("region"), "region")

    period = out.get("period")
    if not isinstance(period, dict):
        raise WorldProfileError("period must be an object")
    period = deepcopy(period)
    period["mode"] = _nonempty_text(period.get("mode"), "period.mode")
    if period["mode"] not in {"historical", "contemporary"}:
        raise WorldProfileError("period.mode must be historical or contemporary")
    period["label"] = _nonempty_text(period.get("label"), "period.label")
    if period["mode"] == "historical":
        start = period.get("start_year")
        end = period.get("end_year")
        if not isinstance(start, int) or not isinstance(end, int) or start > end:
            raise WorldProfileError("historical period requires valid integer start_year/end_year")
    out["period"] = period

    if family == "historical_china":
        if out["country"].casefold() != "china":
            raise WorldProfileError("historical_china profile country must be China")
        if period["mode"] != "historical":
            raise WorldProfileError("historical_china requires historical period")
        period["dynasty"] = _nonempty_text(period.get("dynasty"), "period.dynasty")
    elif family == "european_cinema":
        if out["country"].casefold() in {"europe", "european"}:
            raise WorldProfileError("european_cinema requires a specific country, not generic Europe")
        if out["region"].casefold() in {"europe", "european"}:
            raise WorldProfileError("european_cinema requires a specific region/city")
    out["period"] = period

    for field in LIST_FIELDS:
        out[field] = _clean_list(out, field)
    if not out["visual_language"]:
        raise WorldProfileError("visual_language must not be empty")
    if not out["wardrobe_rules"]:
        raise WorldProfileError("wardrobe_rules must not be empty")
    if not out["architecture_rules"]:
        raise WorldProfileError("architecture_rules must not be empty")
    if not out["avoid"]:
        raise WorldProfileError("avoid must not be empty")

    out["casting_policy"] = _nonempty_text(
        out.get(
            "casting_policy",
            "Character identity comes from casting; the world profile constrains period, wardrobe, environment and material culture.",
        ),
        "casting_policy",
    )
    return out


def world_prompt_payload(profile: dict[str, Any]) -> dict[str, Any]:
    p = validate_world_profile(profile)
    return {
        "profile_id": p["profile_id"],
        "setting_family": p["setting_family"],
        "country": p["country"],
        "region": p["region"],
        "period": p["period"],
        "visual_language": p["visual_language"],
        "wardrobe_rules": p["wardrobe_rules"],
        "architecture_rules": p["architecture_rules"],
        "prop_rules": p["prop_rules"],
        "environment_rules": p["environment_rules"],
        "cinematography": p["cinematography"],
        "casting_policy": p["casting_policy"],
    }


def world_prompt_fragment(profile: dict[str, Any]) -> str:
    return json.dumps(world_prompt_payload(profile), ensure_ascii=False, sort_keys=True)


def world_negative_prompt(profile: dict[str, Any]) -> str:
    p = validate_world_profile(profile)
    return ", ".join(p["avoid"])


def validate_preset_catalog(catalog: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(catalog, dict) or catalog.get("schema_version") != 1:
        raise WorldProfileError("invalid world profile catalog")
    profiles = catalog.get("profiles")
    if not isinstance(profiles, list) or not profiles:
        raise WorldProfileError("world profile catalog requires profiles")
    normalized = [validate_world_profile(row) for row in profiles]
    ids = [row["profile_id"] for row in normalized]
    if len(ids) != len(set(ids)):
        raise WorldProfileError("duplicate world profile_id")
    return {"schema_version": 1, "profiles": normalized}


def resolve_world_preset(catalog: dict[str, Any], profile_id: str) -> dict[str, Any]:
    normalized = validate_preset_catalog(catalog)
    rows = [row for row in normalized["profiles"] if row["profile_id"] == profile_id]
    if len(rows) != 1:
        raise WorldProfileError(f"unknown world preset: {profile_id}")
    return rows[0]

def world_visual_prompt_fragment(profile: dict[str, Any]) -> str:
    p = validate_world_profile(profile)
    period = p["period"]
    parts = [
        f"Setting: {period['label']} in {p['region']}, {p['country']}.",
        *p["visual_language"],
    ]
    if p["wardrobe_rules"]:
        parts.append("Wardrobe: " + "; ".join(p["wardrobe_rules"]) + ".")
    if p["architecture_rules"]:
        parts.append("Architecture: " + "; ".join(p["architecture_rules"]) + ".")
    if p["prop_rules"]:
        parts.append("Props and material culture: " + "; ".join(p["prop_rules"]) + ".")
    if p["environment_rules"]:
        parts.append("Environment: " + "; ".join(p["environment_rules"]) + ".")
    if p["cinematography"]:
        parts.append("Cinematography: " + "; ".join(p["cinematography"]) + ".")
    parts.append("Text-bearing props and signage should be avoided unless story-essential; otherwise keep those surfaces blank or defocused and add readable typography in post-production.")
    parts.append(p["casting_policy"])
    return " ".join(parts)