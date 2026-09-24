#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from film.benchmark import (
    atomic_json,
    build_jobs,
    file_sha256,
    resolve_requirements,
    run_job,
    summarize_results,
    write_blind_review_bundle,
)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Run or plan the slice01 model benchmark.")
    parser.add_argument("--profile", default="smoke")
    parser.add_argument("--model", action="append", default=[])
    parser.add_argument("--run-id")
    parser.add_argument("--out-root", default="benchmarks/slice01")
    parser.add_argument("--reference-index")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--runner", help="Executable implementing RUNNER_CONTRACT.md")
    parser.add_argument("--max-jobs", type=int)
    parser.add_argument("--timeout-sec", type=float, default=1800.0)
    args = parser.parse_args()

    if args.execute:
        if not args.runner:
            parser.error("--execute requires --runner")
        if args.max_jobs is None or args.max_jobs < 1:
            parser.error("--execute requires --max-jobs >= 1")
    elif args.runner:
        parser.error("--runner has no effect without --execute")

    matrix_path = ROOT / "model-evaluations" / "slice01" / "model_matrix.json"
    plan_path = ROOT / "model-evaluations" / "slice01" / "benchmark_plan.json"
    shots_path = ROOT / "projects" / "slice01" / "shots" / "benchmark_shots.json"
    compiled_path = ROOT / "projects" / "slice01" / "compiled" / "benchmark_compiled.json"

    matrix = load_json(matrix_path)
    plan = load_json(plan_path)
    shots = load_json(shots_path)
    only_models = set(args.model) if args.model else None
    prompt_hashes = {
        shot["shot_id"]: file_sha256(ROOT / "projects" / "slice01" / "compiled" / f"{shot['shot_id']}.json")
        for shot in shots
    }
    jobs = build_jobs(
        matrix,
        plan,
        shots,
        profile_name=args.profile,
        only_models=only_models,
        prompt_hashes=prompt_hashes,
    )

    reference_index = None
    if args.reference_index:
        reference_path = Path(args.reference_index)
        if not reference_path.is_absolute():
            reference_path = ROOT / reference_path
        reference_index = load_json(reference_path)
    jobs = [resolve_requirements(job, reference_index) for job in jobs]

    run_id = args.run_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = Path(args.out_root)
    if not run_dir.is_absolute():
        run_dir = ROOT / run_dir
    run_dir = run_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "schema_version": 1,
        "benchmark_id": plan["benchmark_id"],
        "run_id": run_id,
        "profile": args.profile,
        "mode": "EXECUTE" if args.execute else "DRY_RUN",
        "only_models": sorted(only_models) if only_models else None,
        "source_identity": {
            "model_matrix": {"path": str(matrix_path.relative_to(ROOT)), "sha256": file_sha256(matrix_path)},
            "benchmark_plan": {"path": str(plan_path.relative_to(ROOT)), "sha256": file_sha256(plan_path)},
            "shots": {"path": str(shots_path.relative_to(ROOT)), "sha256": file_sha256(shots_path)},
            "compiled_shots": {"path": str(compiled_path.relative_to(ROOT)), "sha256": file_sha256(compiled_path)},
        },
        "job_count": len(jobs),
        "requirement_blocked_job_count": sum(bool(job["blocked_requirements"]) for job in jobs),
        "model_gate_blocked_job_count": sum(not job["model"]["execution_ready"] for job in jobs),
        "execution_ready_job_count": sum(
            bool(job["model"]["execution_ready"]) and not job["blocked_requirements"]
            for job in jobs
        ),
        "paid_execution_authorized_by_harness": False,
        "note": "The harness does not grant spending authority. External runner execution must already be authorized.",
    }
    atomic_json(run_dir / "run_manifest.json", manifest)

    for job in jobs:
        atomic_json(run_dir / "jobs" / job["job_id"] / "job.json", job)

    if not args.execute:
        atomic_json(
            run_dir / "run_summary.json",
            {
                "schema_version": 1,
                "mode": "DRY_RUN",
                "jobs": len(jobs),
                "requirement_blocked": sum(bool(job["blocked_requirements"]) for job in jobs),
                "model_gate_blocked": sum(not job["model"]["execution_ready"] for job in jobs),
                "ready_to_execute": sum(
                    bool(job["model"]["execution_ready"]) and not job["blocked_requirements"]
                    for job in jobs
                ),
            },
        )
        print(f"planned {len(jobs)} jobs -> {run_dir}")
        return 0

    runner = Path(args.runner).expanduser().resolve()
    if not runner.exists():
        parser.error(f"runner not found: {runner}")
    if not os.access(runner, os.X_OK):
        parser.error(f"runner is not executable: {runner}")

    results = []
    executed = 0
    for job in jobs:
        if executed >= args.max_jobs:
            break
        job_dir = run_dir / "jobs" / job["job_id"]
        if not job["model"]["execution_ready"]:
            result = {
                "schema_version": 1,
                "job_id": job["job_id"],
                "job_digest": job["job_digest"],
                "blind_id": job["blind_id"],
                "status": "BLOCKED",
                "failure": "MODEL_NOT_EXECUTION_READY",
                "missing": [],
                "artifacts": [],
            }
            atomic_json(job_dir / "result.json", result)
            results.append(result)
            executed += 1
            continue
        if job["blocked_requirements"]:
            result = {
                "schema_version": 1,
                "job_id": job["job_id"],
                "job_digest": job["job_digest"],
                "blind_id": job["blind_id"],
                "status": "BLOCKED",
                "failure": "MISSING_REQUIREMENT",
                "missing": job["blocked_requirements"],
                "artifacts": [],
            }
            atomic_json(job_dir / "result.json", result)
            results.append(result)
            executed += 1
            continue
        result = run_job(
            job,
            runner_cmd=[str(runner)],
            job_dir=job_dir,
            timeout_sec=args.timeout_sec,
        )
        results.append(result)
        executed += 1

    summary = summarize_results(results)
    summary["mode"] = "EXECUTE"
    summary["executed_or_blocked"] = executed
    summary["planned_jobs"] = len(jobs)
    atomic_json(run_dir / "run_summary.json", summary)
    write_blind_review_bundle(run_dir, jobs, results)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 1 if summary["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
