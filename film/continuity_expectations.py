from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any

from .continuity import state_at


class ContinuityExpectationError(ValueError):
    pass


def canonical_digest(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def compile_continuity_expectations(
    ledger: dict[str, Any],
    shots: list[dict[str, Any]],
) -> dict[str, Any]:
    shot_ids = [shot.get("shot_id") for shot in shots]
    if any(not shot_id for shot_id in shot_ids) or len(shot_ids) != len(set(shot_ids)):
        raise ContinuityExpectationError("invalid/duplicate shot id")
    rows = []
    for shot in shots:
        characters = {}
        for char_id in shot.get("characters", []):
            try:
                characters[char_id] = state_at(ledger, char_id, shot["story_time"])
            except KeyError as exc:
                raise ContinuityExpectationError(
                    f"cannot reconstruct continuity for {shot['shot_id']}:{char_id}"
                ) from exc
        body = {
            "shot_id": shot["shot_id"],
            "story_time": shot["story_time"],
            "characters": characters,
        }
        rows.append({**body, "expectation_digest": canonical_digest(body)})
    return {
        "schema_version": 1,
        "status": "EXPECTATIONS_READY_NO_VISUAL_OBSERVATIONS",
        "shots": rows,
    }


def _flatten(value: Any, prefix: str = "") -> dict[str, Any]:
    if not isinstance(value, dict):
        return {prefix: value}
    result: dict[str, Any] = {}
    for key in sorted(value):
        path = f"{prefix}.{key}" if prefix else key
        child = value[key]
        if isinstance(child, dict):
            result.update(_flatten(child, path))
        else:
            result[path] = child
    return result


def _suggest_tag(path: str) -> str | None:
    if ".identity.age" in path:
        return "AGE_DRIFT"
    if ".identity.hair" in path:
        return "HAIR_DRIFT"
    if ".identity.build" in path or ".identity.gender" in path:
        return "BODY_DRIFT"
    if ".costume" in path or ".costume_damage" in path:
        return "COSTUME_DRIFT"
    if ".location" in path:
        return "LOCATION_DRIFT"
    return None


def diff_observed_state(
    expectation: dict[str, Any],
    observed: dict[str, Any],
) -> dict[str, Any]:
    if observed.get("shot_id") != expectation.get("shot_id"):
        raise ContinuityExpectationError("observed shot_id mismatch")
    if observed.get("expectation_digest") != expectation.get("expectation_digest"):
        raise ContinuityExpectationError("observed expectation_digest mismatch")
    observed_chars = observed.get("characters")
    if not isinstance(observed_chars, dict):
        raise ContinuityExpectationError("observed characters must be mapping")

    mismatches = []
    tags: set[str] = set()
    expected_chars = expectation.get("characters", {})
    for char_id in sorted(expected_chars):
        if char_id not in observed_chars:
            mismatches.append({
                "path": f"characters.{char_id}",
                "reason": "MISSING_CHARACTER_OBSERVATION",
                "expected": expected_chars[char_id],
                "observed": None,
                "suggested_failure_tag": None,
            })
            continue
        expected_flat = _flatten(expected_chars[char_id], f"characters.{char_id}")
        observed_flat = _flatten(observed_chars[char_id], f"characters.{char_id}")
        for path, expected_value in expected_flat.items():
            if path not in observed_flat:
                tag = _suggest_tag(path)
                mismatches.append({
                    "path": path,
                    "reason": "MISSING_FIELD",
                    "expected": expected_value,
                    "observed": None,
                    "suggested_failure_tag": tag,
                })
                if tag:
                    tags.add(tag)
            elif observed_flat[path] != expected_value:
                tag = _suggest_tag(path)
                mismatches.append({
                    "path": path,
                    "reason": "VALUE_MISMATCH",
                    "expected": expected_value,
                    "observed": observed_flat[path],
                    "suggested_failure_tag": tag,
                })
                if tag:
                    tags.add(tag)

    return {
        "schema_version": 1,
        "shot_id": expectation["shot_id"],
        "expectation_digest": expectation["expectation_digest"],
        "status": "MATCH" if not mismatches else "DRIFT",
        "mismatches": mismatches,
        "suggested_failure_tags": sorted(tags),
        "visual_observation_claimed": True,
    }
