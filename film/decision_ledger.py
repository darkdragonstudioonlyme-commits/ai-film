from __future__ import annotations

from collections import defaultdict
from typing import Any


class DecisionLedgerError(ValueError):
    pass


def aggregate_benchmark_records(
    records: list[dict[str, Any]],
    *,
    expected_models: set[str] | None = None,
    expected_shots: set[str] | None = None,
) -> dict[str, Any]:
    seen = set()
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in records:
        key = (row.get("run_id"), row.get("job_id"))
        if not all(key):
            raise DecisionLedgerError("record missing run_id/job_id")
        if key in seen:
            raise DecisionLedgerError(f"duplicate benchmark record: {key}")
        seen.add(key)
        model_id = row.get("model_id")
        shot_id = row.get("shot_id")
        if not model_id or not shot_id:
            raise DecisionLedgerError("record missing model_id/shot_id")
        status = row.get("status")
        if status not in {"PASS", "FAILED", "BLOCKED"}:
            raise DecisionLedgerError(f"invalid status: {status}")
        cost = float(row.get("cost_usd", 0))
        if cost < 0:
            raise DecisionLedgerError("negative cost")
        elapsed = float(row.get("elapsed_sec", 0))
        if elapsed < 0:
            raise DecisionLedgerError("negative elapsed")
        groups[model_id].append(row)

    summaries = []
    for model_id in sorted(groups):
        rows = groups[model_id]
        passed = [r for r in rows if r["status"] == "PASS"]
        failed = [r for r in rows if r["status"] == "FAILED"]
        blocked = [r for r in rows if r["status"] == "BLOCKED"]
        quality = [float(r["quality_overall"]) for r in passed if r.get("quality_overall") is not None]
        summaries.append({
            "model_id": model_id,
            "records": len(rows),
            "passed": len(passed),
            "failed": len(failed),
            "blocked": len(blocked),
            "cost_usd": round(sum(float(r.get("cost_usd", 0)) for r in rows), 6),
            "elapsed_sec": round(sum(float(r.get("elapsed_sec", 0)) for r in rows), 6),
            "gpu_peak_memory_mb": max(
                [float(r["gpu_peak_memory_mb"]) for r in rows if r.get("gpu_peak_memory_mb") is not None],
                default=None,
            ),
            "quality_overall_mean": (
                round(sum(quality) / len(quality), 6) if quality else None
            ),
            "usable_rate": (
                round(sum(1 for r in passed if r.get("usable") is True) / len(passed), 6)
                if passed else None
            ),
            "shots": sorted({r["shot_id"] for r in rows}),
        })

    observed_models = {row["model_id"] for row in summaries}
    observed_shots = {shot for row in summaries for shot in row["shots"]}
    missing_models = sorted((expected_models or set()) - observed_models)
    missing_shots = sorted((expected_shots or set()) - observed_shots)
    complete = not missing_models and not missing_shots and all(
        row["quality_overall_mean"] is not None and row["usable_rate"] is not None
        for row in summaries
    )
    report = {
        "schema_version": 1,
        "status": "COMPLETE_COMPARISON" if complete else "INSUFFICIENT_EVIDENCE",
        "record_count": len(records),
        "models": summaries,
        "missing_models": missing_models,
        "missing_shots": missing_shots,
        "total_cost_usd": round(sum(row["cost_usd"] for row in summaries), 6),
    }
    if complete:
        # This is a deterministic evidence ordering, not a purchase/production decision.
        report["evidence_order"] = [
            row["model_id"]
            for row in sorted(
                summaries,
                key=lambda r: (
                    -(r["quality_overall_mean"] or 0),
                    -(r["usable_rate"] or 0),
                    r["cost_usd"],
                    r["elapsed_sec"],
                    r["model_id"],
                ),
            )
        ]
    else:
        report["evidence_order"] = []
    report["selected_winner"] = None
    report["selection_authorized"] = False
    return report
