from __future__ import annotations

import csv
from dataclasses import dataclass
from io import StringIO
from typing import Any, Iterable


class BlindScoreError(ValueError):
    pass


@dataclass(frozen=True)
class ScoreSchema:
    criteria: tuple[str, ...]
    scale_min: float = 1.0
    scale_max: float = 5.0
    failure_tags_column: str = "failure_tags"
    notes_column: str = "notes"


def parse_score_csv(text: str) -> list[dict[str, str]]:
    reader = csv.DictReader(StringIO(text))
    if not reader.fieldnames or "blind_id" not in reader.fieldnames:
        raise BlindScoreError("score CSV missing blind_id header")
    rows = list(reader)
    ids = [row.get("blind_id", "").strip() for row in rows]
    if any(not blind_id for blind_id in ids):
        raise BlindScoreError("score CSV contains empty blind_id")
    if len(ids) != len(set(ids)):
        raise BlindScoreError("duplicate blind_id in score CSV")
    return rows


def validate_complete_scores(
    public_items: Iterable[dict[str, Any]],
    score_rows: list[dict[str, str]],
    schema: ScoreSchema,
) -> dict[str, dict[str, Any]]:
    items = list(public_items)
    expected_ids = [str(item["blind_id"]) for item in items]
    if len(expected_ids) != len(set(expected_ids)):
        raise BlindScoreError("duplicate blind_id in public items")

    score_by_id = {row["blind_id"].strip(): row for row in score_rows}
    missing = sorted(set(expected_ids) - set(score_by_id))
    extra = sorted(set(score_by_id) - set(expected_ids))
    if missing or extra:
        raise BlindScoreError(f"score population mismatch missing={missing} extra={extra}")

    normalized: dict[str, dict[str, Any]] = {}
    for blind_id in expected_ids:
        row = score_by_id[blind_id]
        values: dict[str, float] = {}
        for criterion in schema.criteria:
            raw = (row.get(criterion) or "").strip()
            if not raw:
                raise BlindScoreError(f"incomplete score {blind_id}:{criterion}")
            try:
                value = float(raw)
            except ValueError as exc:
                raise BlindScoreError(f"invalid score {blind_id}:{criterion}") from exc
            if not schema.scale_min <= value <= schema.scale_max:
                raise BlindScoreError(f"score out of range {blind_id}:{criterion}")
            values[criterion] = value
        normalized[blind_id] = {
            "blind_id": blind_id,
            "scores": values,
            "failure_tags": [
                tag.strip()
                for tag in (row.get(schema.failure_tags_column) or "").split(";")
                if tag.strip()
            ],
            "notes": (row.get(schema.notes_column) or "").strip(),
        }
    return normalized


def unblind_and_rank(
    validated_scores: dict[str, dict[str, Any]],
    private_mapping: Iterable[dict[str, Any]],
    *,
    group_fields: tuple[str, ...],
    overall_field: str = "overall",
) -> list[dict[str, Any]]:
    mapping = list(private_mapping)
    map_by_id = {str(row["blind_id"]): row for row in mapping}
    if len(map_by_id) != len(mapping):
        raise BlindScoreError("duplicate blind_id in private mapping")
    if set(map_by_id) != set(validated_scores):
        raise BlindScoreError("private map population does not match validated scores")

    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    for blind_id, scored in validated_scores.items():
        private = map_by_id[blind_id]
        key = tuple(private.get(field) for field in group_fields)
        groups.setdefault(key, []).append({"private": private, "scored": scored})

    ranked: list[dict[str, Any]] = []
    for key, rows in groups.items():
        if any(value is None for value in key):
            raise BlindScoreError("private mapping missing group field")
        score_names = sorted(next(iter(rows))["scored"]["scores"])
        means = {
            name: round(sum(row["scored"]["scores"][name] for row in rows) / len(rows), 6)
            for name in score_names
        }
        failures = sorted(
            tag
            for row in rows
            for tag in row["scored"]["failure_tags"]
        )
        ranked.append(
            {
                "group": dict(zip(group_fields, key)),
                "sample_count": len(rows),
                "mean_scores": means,
                "failure_tags": failures,
                "overall": means[overall_field],
            }
        )
    ranked.sort(
        key=lambda row: (
            -row["overall"],
            tuple(str(row["group"][field]) for field in group_fields),
        )
    )
    for index, row in enumerate(ranked, 1):
        row["rank"] = index
    return ranked
