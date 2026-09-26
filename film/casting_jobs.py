from __future__ import annotations

import hashlib
import json
from typing import Any

from .world_profile import validate_world_profile, world_negative_prompt, world_prompt_fragment


SLOT_PROMPTS = {
    "face_front": "front-facing head-and-shoulders identity reference, neutral pose, clear facial features",
    "face_3q": "three-quarter head-and-shoulders identity reference, neutral pose, clear facial features",
    "full_body_neutral": "full-body standing identity reference, neutral pose, clear body proportions",
    "expression_neutral": "head-and-shoulders neutral-expression identity reference, relaxed face",
}

STYLE_PROMPTS = {
    "photoreal": "cinematic photorealism, natural skin and materials, realistic anatomy, neutral reference lighting",
    "stylized_3d": "high-end stylized 3D character render, coherent materials, production animation quality, neutral reference lighting",
}


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def active_image_models(matrix: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [
        row for row in matrix.get("models", [])
        if row.get("enabled") and row.get("stage") == "image"
    ]
    rows.sort(key=lambda row: row["model_id"])
    if not rows:
        raise ValueError("no enabled image models")
    for row in rows:
        if row.get("pin_status") != "PINNED":
            raise ValueError(f"image model not pinned: {row.get('model_id')}")
        if row.get("execution_ready"):
            raise ValueError(f"casting compiler expects non-executing model: {row.get('model_id')}")
        if not row.get("source_revision"):
            raise ValueError(f"missing model revision: {row.get('model_id')}")
    return rows


def compile_casting_jobs(
    contract: dict[str, Any],
    matrix: dict[str, Any],
    world_profile: dict[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    if contract.get("status") != "CONTRACT_READY_REFERENCES_NOT_GENERATED":
        raise ValueError("casting reference contract is not in pre-generation state")
    models = active_image_models(matrix)
    world = validate_world_profile(world_profile) if world_profile is not None else None
    jobs: list[dict[str, Any]] = []
    public_items: list[dict[str, Any]] = []
    private_mapping: list[dict[str, Any]] = []

    for character_id in sorted(contract["characters"]):
        character = contract["characters"][character_id]
        target = character["visual_target"]
        for style in sorted(character["styles"]):
            if style not in STYLE_PROMPTS:
                raise ValueError(f"unknown style: {style}")
            slots = character["styles"][style]["slots"]
            for slot_row in slots:
                slot = slot_row["slot"]
                if slot not in SLOT_PROMPTS:
                    raise ValueError(f"unknown casting slot: {slot}")
                for model in models:
                    prompt = f"{target}. {SLOT_PROMPTS[slot]}. {STYLE_PROMPTS[style]}."
                    negative_prompt = "identity drift, age drift, hair drift, anatomy errors, extra fingers, text, watermark"
                    source = {
                        "schema_version": 1,
                        "project_id": contract["project_id"],
                        "character_id": character_id,
                        "style": style,
                        "slot": slot,
                        "model_id": model["model_id"],
                        "model_repo": model["source_repo"],
                        "model_revision": model["source_revision"],
                        "license_gate": model["license_gate"],
                        "visual_target": target,
                    }
                    if world is not None:
                        source["world_profile_id"] = world["profile_id"]
                        source["world_profile"] = world
                        prompt += f" World/period context: {world_prompt_fragment(world)}."
                        negative_prompt += ", " + world_negative_prompt(world)
                    source["prompt"] = prompt + " No text, no watermark."
                    source["negative_prompt"] = negative_prompt
                    source_digest = digest(source)
                    seed = int(source_digest[:8], 16)
                    job_id = "castjob_" + source_digest[:16]
                    blind_id = "cast_" + hashlib.sha256(
                        ("slice01-casting:" + source_digest).encode("utf-8")
                    ).hexdigest()[:12]
                    job = {
                        **source,
                        "job_id": job_id,
                        "job_digest": source_digest,
                        "blind_id": blind_id,
                        "seed": seed,
                        "output_contract": {
                            "kind": "image",
                            "asset_id": None,
                            "asset_sha256": None,
                            "manifest_sha256": None,
                        },
                        "execution_permitted": False,
                    }
                    jobs.append(job)
                    public_items.append(
                        {
                            "blind_id": blind_id,
                            "style": style,
                            "slot": slot,
                            "asset_id": None,
                            "asset_sha256": None,
                        }
                    )
                    private_mapping.append(
                        {
                            "blind_id": blind_id,
                            "job_id": job_id,
                            "character_id": character_id,
                            "model_id": model["model_id"],
                            "model_revision": model["source_revision"],
                            "style": style,
                            "slot": slot,
                            "seed": seed,
                        }
                    )

    if len({row["job_id"] for row in jobs}) != len(jobs):
        raise ValueError("duplicate casting job identity")
    if len({row["blind_id"] for row in jobs}) != len(jobs):
        raise ValueError("duplicate casting blind identity")

    bundle = {
        "schema_version": 1,
        "project_id": contract["project_id"],
        "status": "COMPILED_NOT_EXECUTED",
        "job_count": len(jobs),
        "image_model_count": len(models),
        "slot_count": len(jobs) // len(models),
        "jobs": jobs,
    }
    public = {
        "schema_version": 1,
        "status": "AWAITING_GENERATED_ASSETS",
        "items": public_items,
    }
    private = {
        "schema_version": 1,
        "mapping": private_mapping,
    }
    return jobs, public, private