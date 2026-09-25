from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any


def _asset_bytes(job: dict[str, Any]) -> bytes:
    # Tiny deterministic PPM text fixture. This is test material, never a production image.
    seed = int(job["seed"]) % 255
    r = seed
    g = (seed * 3) % 255
    b = (seed * 7) % 255
    return f"P3\n2 2\n255\n{r} {g} {b} {r} {g} {b}\n{r} {g} {b} {r} {g} {b}\n".encode("ascii")


def build_synthetic_casting_outputs(jobs: list[dict[str, Any]], out_dir: Path) -> list[dict[str, Any]]:
    out_dir.mkdir(parents=True, exist_ok=True)
    manifests = []
    for job in jobs:
        asset_id = "synthetic_" + job["job_id"]
        path = out_dir / f"{asset_id}.ppm"
        raw = _asset_bytes(job)
        path.write_bytes(raw)
        asset_sha = hashlib.sha256(raw).hexdigest()
        manifest_body = (
            f"{job['job_id']}|{job['job_digest']}|{job['model_id']}|"
            f"{job['model_revision']}|{job['seed']}|{asset_sha}"
        ).encode("utf-8")
        manifest_sha = hashlib.sha256(manifest_body).hexdigest()
        manifests.append({
            "fixture": True,
            "fixture_kind": "SYNTHETIC_PPM_NOT_PRODUCTION_ASSET",
            "job_id": job["job_id"],
            "job_digest": job["job_digest"],
            "blind_id": job["blind_id"],
            "asset_id": asset_id,
            "asset_path": str(path),
            "asset_sha256": asset_sha,
            "manifest_sha256": manifest_sha,
            "model_id": job["model_id"],
            "model_revision": job["model_revision"],
            "seed": job["seed"],
        })
    return manifests
