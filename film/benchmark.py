from __future__ import annotations

import csv
import hashlib
import json
import os
import signal
from pathlib import Path
from copy import deepcopy
import shutil
import subprocess
import time
from typing import Any, Iterable

RESERVED_OUTPUT_NAMES = {
    "job.json",
    "result.json",
    "runner.stdout.log",
    "runner.stderr.log",
}


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    raw = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    with tmp.open("w", encoding="utf-8") as fh:
        fh.write(raw)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


def _model_index(model_matrix: dict[str, Any]) -> dict[str, dict[str, Any]]:
    models = model_matrix.get("models")
    if not isinstance(models, list):
        raise ValueError("model_matrix.models must be a list")
    result: dict[str, dict[str, Any]] = {}
    for model in models:
        model_id = model.get("model_id")
        if not isinstance(model_id, str) or not model_id:
            raise ValueError("each model requires model_id")
        if model_id in result:
            raise ValueError(f"duplicate model_id: {model_id}")
        result[model_id] = model
    return result


def _shot_index(shots: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for shot in shots:
        shot_id = shot.get("shot_id")
        if not isinstance(shot_id, str) or not shot_id:
            raise ValueError("each shot requires shot_id")
        if shot_id in result:
            raise ValueError(f"duplicate shot_id: {shot_id}")
        result[shot_id] = shot
    return result


def build_jobs(
    model_matrix: dict[str, Any],
    plan: dict[str, Any],
    shots: list[dict[str, Any]],
    *,
    profile_name: str,
    only_models: set[str] | None = None,
    prompt_hashes: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    profiles = plan.get("profiles")
    if not isinstance(profiles, dict) or profile_name not in profiles:
        raise ValueError(f"unknown benchmark profile: {profile_name}")
    profile = profiles[profile_name]
    models = _model_index(model_matrix)
    shot_by_id = _shot_index(shots)

    stages = set(profile.get("stages", []))
    shot_ids = profile.get("shot_ids", [])
    styles = profile.get("styles", [])
    seed_offsets = profile.get("seed_offsets", [0])
    aspect = profile.get("aspect", "9:16")
    resolution = profile.get("resolution", {"width": 720, "height": 1280})

    if not stages or not shot_ids or not styles or not seed_offsets:
        raise ValueError("profile must define stages, shot_ids, styles and seed_offsets")

    selected_models = []
    for model in models.values():
        if not model.get("enabled", False):
            continue
        if model.get("stage") not in stages:
            continue
        if only_models is not None and model["model_id"] not in only_models:
            continue
        selected_models.append(model)

    if not selected_models:
        raise ValueError("profile selected zero enabled models")

    jobs: list[dict[str, Any]] = []
    benchmark_id = plan["benchmark_id"]
    for model in sorted(selected_models, key=lambda x: x["model_id"]):
        for shot_id in shot_ids:
            if shot_id not in shot_by_id:
                raise ValueError(f"profile references unknown shot: {shot_id}")
            shot = shot_by_id[shot_id]
            for style in styles:
                for offset in seed_offsets:
                    if not isinstance(offset, int):
                        raise ValueError("seed_offsets must contain integers")
                    seed = int(shot["seed"]) + offset
                    payload = {
                        "schema_version": 1,
                        "benchmark_id": benchmark_id,
                        "profile": profile_name,
                        "model": {
                            "model_id": model["model_id"],
                            "stage": model["stage"],
                            "family": model.get("family"),
                            "checkpoint": model.get("checkpoint"),
                            "runner_profile": model.get("runner_profile"),
                            "license_gate": model.get("license_gate"),
                            "license_hint": model.get("license_hint"),
                            "execution_ready": bool(model.get("execution_ready", False)),
                        },
                        "shot_id": shot_id,
                        "story_time": shot.get("story_time"),
                        "style": style,
                        "aspect": aspect,
                        "resolution": resolution,
                        "seed": seed,
                        "prompt_source": f"projects/slice01/compiled/{shot_id}.json",
                        "prompt_sha256": (prompt_hashes or {}).get(shot_id),
                        "requirements": list(model.get("requires", [])),
                    }
                    digest = sha256_json(payload)
                    payload["job_digest"] = digest
                    payload["job_id"] = "job_" + digest[:16]
                    payload["blind_id"] = "sample_" + hashlib.sha256(
                        (benchmark_id + ":" + digest).encode("utf-8")
                    ).hexdigest()[:12]
                    jobs.append(payload)
    return jobs



def resolve_requirements(
    job: dict[str, Any],
    reference_index: dict[str, Any] | None,
) -> dict[str, Any]:
    resolved = deepcopy(job)
    shot_refs = {}
    if reference_index:
        shot_refs = reference_index.get("shots", {}).get(job["shot_id"], {})
    found: dict[str, Any] = {}
    missing: list[str] = []
    for requirement in job.get("requirements", []):
        value = shot_refs.get(requirement)
        if value:
            found[requirement] = value
        else:
            missing.append(requirement)
    resolved["resolved_references"] = found
    resolved["blocked_requirements"] = missing
    return resolved

def gpu_memory_used_mb() -> int | None:
    exe = shutil.which("nvidia-smi")
    if not exe:
        return None
    proc = subprocess.run(
        [
            exe,
            "--query-gpu=memory.used",
            "--format=csv,noheader,nounits",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        return None
    values = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if line:
            try:
                values.append(int(line))
            except ValueError:
                return None
    return max(values) if values else None


def collect_artifacts(output_dir: Path) -> list[dict[str, Any]]:
    artifacts: list[dict[str, Any]] = []
    if not output_dir.exists():
        return artifacts
    for path in sorted(p for p in output_dir.rglob("*") if p.is_file()):
        rel = path.relative_to(output_dir).as_posix()
        if path.name in RESERVED_OUTPUT_NAMES:
            continue
        artifacts.append(
            {
                "path": rel,
                "bytes": path.stat().st_size,
                "sha256": file_sha256(path),
            }
        )
    return artifacts


def run_job(
    job: dict[str, Any],
    *,
    runner_cmd: list[str],
    job_dir: Path,
    poll_interval: float = 0.1,
    timeout_sec: float | None = None,
) -> dict[str, Any]:
    if not runner_cmd:
        raise ValueError("runner_cmd is required")
    job_dir.mkdir(parents=True, exist_ok=True)
    output_dir = job_dir / "artifacts"
    output_dir.mkdir(parents=True, exist_ok=True)
    job_path = job_dir / "job.json"
    atomic_json(job_path, job)

    stdout_path = job_dir / "runner.stdout.log"
    stderr_path = job_dir / "runner.stderr.log"
    env = os.environ.copy()
    env.update(
        {
            "AIFILM_JOB_ID": job["job_id"],
            "AIFILM_BENCHMARK_ID": job["benchmark_id"],
            "AIFILM_OUTPUT_DIR": str(output_dir),
        }
    )

    started_wall = time.time()
    started_mono = time.monotonic()
    before_gpu = gpu_memory_used_mb()
    peak_gpu = before_gpu
    timed_out = False

    with stdout_path.open("wb") as stdout_fh, stderr_path.open("wb") as stderr_fh:
        proc = subprocess.Popen(
            [*runner_cmd, str(job_path), str(output_dir)],
            cwd=job_dir,
            stdout=stdout_fh,
            stderr=stderr_fh,
            env=env,
            start_new_session=True,
        )
        while proc.poll() is None:
            current = gpu_memory_used_mb()
            if current is not None:
                peak_gpu = current if peak_gpu is None else max(peak_gpu, current)
            if timeout_sec is not None and time.monotonic() - started_mono > timeout_sec:
                timed_out = True
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                break
            time.sleep(poll_interval)
        exit_code = proc.wait()

    elapsed = time.monotonic() - started_mono
    finished_wall = time.time()
    artifacts = collect_artifacts(output_dir)
    status = "PASS" if exit_code == 0 and not timed_out and artifacts else "FAILED"
    failure = None
    if timed_out:
        failure = "TIMEOUT"
    elif exit_code != 0:
        failure = "RUNNER_EXIT"
    elif not artifacts:
        failure = "NO_ARTIFACTS"

    result = {
        "schema_version": 1,
        "job_id": job["job_id"],
        "job_digest": job["job_digest"],
        "blind_id": job["blind_id"],
        "status": status,
        "failure": failure,
        "exit_code": exit_code,
        "started_unix": started_wall,
        "finished_unix": finished_wall,
        "elapsed_sec": round(elapsed, 6),
        "gpu_memory_before_mb": before_gpu,
        "gpu_peak_memory_mb": peak_gpu,
        "gpu_observation": "NVIDIA_SMI" if peak_gpu is not None else "NOT_AVAILABLE",
        "artifacts": artifacts,
        "runner_stdout": stdout_path.name,
        "runner_stderr": stderr_path.name,
    }
    atomic_json(job_dir / "result.json", result)
    return result


def write_blind_review_bundle(run_dir: Path, jobs: Iterable[dict[str, Any]], results: Iterable[dict[str, Any]]) -> None:
    job_by_id = {job["job_id"]: job for job in jobs}
    result_by_id = {result["job_id"]: result for result in results}
    items = []
    mapping = []
    for job_id in sorted(result_by_id):
        job = job_by_id[job_id]
        result = result_by_id[job_id]
        if result.get("status") != "PASS":
            continue
        items.append(
            {
                "blind_id": job["blind_id"],
                "stage": job["model"]["stage"],
                "shot_id": job["shot_id"],
                "style": job["style"],
                "aspect": job["aspect"],
                "artifacts": result["artifacts"],
            }
        )
        mapping.append(
            {
                "blind_id": job["blind_id"],
                "job_id": job_id,
                "model_id": job["model"]["model_id"],
                "seed": job["seed"],
            }
        )
    atomic_json(run_dir / "blind_review_items.json", {"schema_version": 1, "items": items})
    atomic_json(run_dir / "blind_map_private.json", {"schema_version": 1, "mapping": mapping})

    score_path = run_dir / "blind_scores.csv"
    with score_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                "blind_id",
                "identity_consistency",
                "style_quality",
                "prompt_adherence",
                "motion_quality",
                "temporal_stability",
                "framing",
                "overall",
                "usable",
                "failure_tags",
                "notes",
            ]
        )
        for item in items:
            writer.writerow([item["blind_id"], "", "", "", "", "", "", "", "", "", ""])


def summarize_results(results: Iterable[dict[str, Any]]) -> dict[str, Any]:
    rows = list(results)
    passed = [row for row in rows if row.get("status") == "PASS"]
    failed = [row for row in rows if row.get("status") == "FAILED"]
    blocked = [row for row in rows if row.get("status") == "BLOCKED"]
    elapsed = sum(float(row.get("elapsed_sec", 0)) for row in rows)
    peaks = [row["gpu_peak_memory_mb"] for row in rows if row.get("gpu_peak_memory_mb") is not None]
    return {
        "schema_version": 1,
        "jobs": len(rows),
        "passed": len(passed),
        "failed": len(failed),
        "blocked": len(blocked),
        "elapsed_sec_total": round(elapsed, 6),
        "gpu_peak_memory_mb": max(peaks) if peaks else None,
        "failures": sorted(
            {row.get("failure") for row in failed if row.get("failure")}
        ),
        "blockers": sorted(
            {row.get("failure") for row in blocked if row.get("failure")}
        ),
    }
