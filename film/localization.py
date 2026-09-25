from __future__ import annotations

from copy import deepcopy
from typing import Any


class LocalizationError(ValueError):
    pass


LANGUAGES = ("en", "zh-CN", "vi")


def validate_localization_bundle(
    bundle: dict[str, Any],
    *,
    expected_dialogue_ids: set[str],
    cue_budgets_sec: dict[str, float],
) -> dict[str, Any]:
    if bundle.get("master_language") != "en":
        raise LocalizationError("master language must be en")
    if tuple(bundle.get("languages", [])) != LANGUAGES:
        raise LocalizationError("language set/order mismatch")
    lines = bundle.get("lines")
    if not isinstance(lines, list):
        raise LocalizationError("lines must be a list")
    ids = [line.get("dialogue_id") for line in lines]
    if len(ids) != len(set(ids)) or set(ids) != expected_dialogue_ids:
        raise LocalizationError(
            f"dialogue population mismatch expected={sorted(expected_dialogue_ids)} actual={sorted(x for x in ids if x)}"
        )

    blockers: list[str] = []
    normalized = []
    for line in lines:
        dialogue_id = line["dialogue_id"]
        if not line.get("character_id"):
            raise LocalizationError(f"missing character_id: {dialogue_id}")
        texts = line.get("texts")
        if not isinstance(texts, dict) or set(texts) != set(LANGUAGES):
            raise LocalizationError(f"text language coverage mismatch: {dialogue_id}")
        for language in LANGUAGES:
            if not str(texts[language]).strip():
                blockers.append(f"missing-text:{dialogue_id}:{language}")
        budget = float(cue_budgets_sec[dialogue_id])
        measurements = line.get("timing_measurements", {})
        if set(measurements) != set(LANGUAGES):
            raise LocalizationError(f"timing measurement coverage mismatch: {dialogue_id}")
        normalized_measurements = {}
        for language in LANGUAGES:
            row = measurements[language]
            duration = row.get("duration_sec")
            status = row.get("status")
            if duration is None:
                if status != "NOT_MEASURED":
                    raise LocalizationError(f"unmeasured timing status mismatch: {dialogue_id}:{language}")
                blockers.append(f"timing-not-measured:{dialogue_id}:{language}")
                normalized_measurements[language] = deepcopy(row)
                continue
            duration = float(duration)
            if duration <= 0:
                raise LocalizationError(f"invalid measured duration: {dialogue_id}:{language}")
            if not row.get("evidence_ref"):
                raise LocalizationError(f"measured timing missing evidence: {dialogue_id}:{language}")
            evidence_sha = row.get("evidence_sha256")
            if not isinstance(evidence_sha, str) or len(evidence_sha) != 64 or any(c not in "0123456789abcdef" for c in evidence_sha):
                raise LocalizationError(f"measured timing evidence hash invalid: {dialogue_id}:{language}")
            if status not in {"PREVIS_MEASURED", "FINAL_MEASURED"}:
                raise LocalizationError(f"invalid timing status: {dialogue_id}:{language}")
            if duration > budget + 1e-9:
                blockers.append(f"timing-over-budget:{dialogue_id}:{language}:{duration}>{budget}")
            normalized_measurements[language] = {**deepcopy(row), "duration_sec": duration}
        normalized.append({
            **deepcopy(line),
            "cue_budget_sec": budget,
            "timing_measurements": normalized_measurements,
        })

    return {
        "schema_version": 1,
        "project_id": bundle.get("project_id"),
        "master_language": "en",
        "languages": list(LANGUAGES),
        "status": "COMPLETE_TIMING_FIT" if not blockers else "PARTIAL_OR_BLOCKED",
        "lines": normalized,
        "blockers": sorted(set(blockers)),
    }
