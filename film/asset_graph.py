from __future__ import annotations

from collections import defaultdict, deque
from copy import deepcopy
from typing import Any


class AssetGraphError(ValueError):
    pass


IMMUTABLE_FIELDS = {
    "asset_id",
    "kind",
    "content_sha256",
    "manifest_sha256",
}


def _validate_sha(value: Any, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
        raise AssetGraphError(f"invalid {field}")
    return value


def validate_asset(asset: dict[str, Any]) -> dict[str, Any]:
    missing = sorted(IMMUTABLE_FIELDS - set(asset))
    if missing:
        raise AssetGraphError(f"asset missing fields: {missing}")
    if not isinstance(asset["asset_id"], str) or not asset["asset_id"]:
        raise AssetGraphError("invalid asset_id")
    if not isinstance(asset["kind"], str) or not asset["kind"]:
        raise AssetGraphError("invalid kind")
    _validate_sha(asset["content_sha256"], "content_sha256")
    _validate_sha(asset["manifest_sha256"], "manifest_sha256")
    out = deepcopy(asset)
    out.setdefault("rights_status", "UNKNOWN")
    out.setdefault("publishable", False)
    out.setdefault("approved", False)
    out.setdefault("evidence", False)
    out.setdefault("revoked", False)
    return out


class AssetGraph:
    def __init__(self, assets: list[dict[str, Any]] | None = None, edges: list[dict[str, str]] | None = None):
        self.assets: dict[str, dict[str, Any]] = {}
        self.children: dict[str, set[str]] = defaultdict(set)
        self.parents: dict[str, set[str]] = defaultdict(set)
        for asset in assets or []:
            self.add_asset(asset)
        for edge in edges or []:
            self.add_dependency(edge["parent_asset_id"], edge["child_asset_id"])

    def add_asset(self, asset: dict[str, Any]) -> None:
        normalized = validate_asset(asset)
        asset_id = normalized["asset_id"]
        existing = self.assets.get(asset_id)
        if existing is not None:
            if existing != normalized:
                raise AssetGraphError(f"immutable asset conflict: {asset_id}")
            return
        self.assets[asset_id] = normalized

    def add_dependency(self, parent_asset_id: str, child_asset_id: str) -> None:
        if parent_asset_id == child_asset_id:
            raise AssetGraphError("self dependency")
        if parent_asset_id not in self.assets or child_asset_id not in self.assets:
            raise AssetGraphError("dependency references unknown asset")
        if self._reachable(child_asset_id, parent_asset_id):
            raise AssetGraphError("dependency would create cycle")
        self.children[parent_asset_id].add(child_asset_id)
        self.parents[child_asset_id].add(parent_asset_id)

    def _reachable(self, start: str, target: str) -> bool:
        queue = deque([start])
        seen = set()
        while queue:
            node = queue.popleft()
            if node == target:
                return True
            if node in seen:
                continue
            seen.add(node)
            queue.extend(sorted(self.children.get(node, ())))
        return False

    def descendants(self, asset_ids: set[str]) -> list[str]:
        unknown = sorted(asset_ids - set(self.assets))
        if unknown:
            raise AssetGraphError(f"unknown invalidation roots: {unknown}")
        queue = deque(sorted(asset_ids))
        seen: set[str] = set()
        while queue:
            current = queue.popleft()
            for child in sorted(self.children.get(current, ())):
                if child not in seen and child not in asset_ids:
                    seen.add(child)
                    queue.append(child)
        return sorted(seen)

    def invalidation_plan(
        self,
        changed_asset_ids: set[str],
        *,
        reason: str,
    ) -> dict[str, Any]:
        if not reason.strip():
            raise AssetGraphError("invalidation reason required")
        descendants = self.descendants(changed_asset_ids)
        affected = sorted(set(changed_asset_ids) | set(descendants))
        unaffected = sorted(set(self.assets) - set(affected))
        return {
            "schema_version": 1,
            "reason": reason,
            "roots": sorted(changed_asset_ids),
            "affected_assets": affected,
            "descendants_invalidated": descendants,
            "unaffected_assets": unaffected,
            "regeneration_authorized": False,
        }

    def deletion_impact(
        self,
        asset_ids: set[str],
        *,
        selected_asset_ids: set[str] | None = None,
        evidence_asset_ids: set[str] | None = None,
    ) -> dict[str, Any]:
        unknown = sorted(asset_ids - set(self.assets))
        if unknown:
            raise AssetGraphError(f"unknown delete targets: {unknown}")
        selected = selected_asset_ids or set()
        evidence = evidence_asset_ids or set()
        descendants = self.descendants(asset_ids)
        blockers: list[str] = []
        for asset_id in sorted(asset_ids):
            asset = self.assets[asset_id]
            if asset.get("approved"):
                blockers.append(f"approved:{asset_id}")
            if asset.get("evidence") or asset_id in evidence:
                blockers.append(f"evidence:{asset_id}")
            if asset_id in selected:
                blockers.append(f"selected:{asset_id}")
            if self.children.get(asset_id):
                blockers.append(f"referenced-by-descendants:{asset_id}")
        return {
            "schema_version": 1,
            "targets": sorted(asset_ids),
            "descendants": descendants,
            "blockers": blockers,
            "delete_permitted": not blockers,
            "dry_run_only": True,
        }

    def snapshot(self) -> dict[str, Any]:
        edges = [
            {"parent_asset_id": parent, "child_asset_id": child}
            for parent in sorted(self.children)
            for child in sorted(self.children[parent])
        ]
        return {
            "schema_version": 1,
            "assets": [deepcopy(self.assets[k]) for k in sorted(self.assets)],
            "edges": edges,
        }
