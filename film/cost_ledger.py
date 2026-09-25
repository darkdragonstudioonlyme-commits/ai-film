from __future__ import annotations

from copy import deepcopy
from typing import Any


class CostLedgerError(ValueError):
    pass


CATEGORIES = {
    "COMPUTE_ACCEPTED",
    "COMPUTE_FAILED",
    "COMPUTE_REJECTED_TAKE",
    "STORAGE",
    "TRANSFER",
    "API",
    "OTHER",
}


def new_ledger(project_id: str) -> dict[str, Any]:
    if not project_id:
        raise CostLedgerError("project_id required")
    return {
        "schema_version": 1,
        "project_id": project_id,
        "entries": [],
    }


def append_cost(
    ledger: dict[str, Any],
    *,
    cost_id: str,
    category: str,
    amount_usd: float,
    logical_key: str | None = None,
    attempt_id: str | None = None,
    asset_id: str | None = None,
    note: str = "",
) -> dict[str, Any]:
    if not cost_id:
        raise CostLedgerError("cost_id required")
    if category not in CATEGORIES:
        raise CostLedgerError("unknown cost category")
    amount = float(amount_usd)
    if amount < 0:
        raise CostLedgerError("negative cost")
    if any(row.get("cost_id") == cost_id for row in ledger.get("entries", [])):
        raise CostLedgerError("duplicate cost_id")
    out = deepcopy(ledger)
    out["entries"].append({
        "cost_id": cost_id,
        "category": category,
        "amount_usd": round(amount, 6),
        "logical_key": logical_key,
        "attempt_id": attempt_id,
        "asset_id": asset_id,
        "note": note,
    })
    return out


def summarize_costs(ledger: dict[str, Any]) -> dict[str, Any]:
    by_category = {category: 0.0 for category in sorted(CATEGORIES)}
    by_logical_key: dict[str, float] = {}
    for row in ledger.get("entries", []):
        category = row["category"]
        amount = float(row["amount_usd"])
        by_category[category] = round(by_category.get(category, 0.0) + amount, 6)
        if row.get("logical_key"):
            key = row["logical_key"]
            by_logical_key[key] = round(by_logical_key.get(key, 0.0) + amount, 6)
    total = round(sum(float(row["amount_usd"]) for row in ledger.get("entries", [])), 6)
    return {
        "schema_version": 1,
        "project_id": ledger["project_id"],
        "entry_count": len(ledger.get("entries", [])),
        "total_usd": total,
        "by_category": by_category,
        "by_logical_key": by_logical_key,
    }


def budget_decision(
    ledger: dict[str, Any],
    *,
    budget_usd: float,
    proposed_charge_usd: float = 0.0,
) -> dict[str, Any]:
    budget = float(budget_usd)
    proposed = float(proposed_charge_usd)
    if budget < 0 or proposed < 0:
        raise CostLedgerError("negative budget/proposed charge")
    summary = summarize_costs(ledger)
    projected = round(summary["total_usd"] + proposed, 6)
    remaining = round(budget - summary["total_usd"], 6)
    return {
        "schema_version": 1,
        "project_id": ledger["project_id"],
        "budget_usd": budget,
        "spent_usd": summary["total_usd"],
        "proposed_charge_usd": proposed,
        "projected_usd": projected,
        "remaining_before_charge_usd": remaining,
        "allowed": projected <= budget + 1e-9,
        "all_cost_categories_counted": True,
    }
