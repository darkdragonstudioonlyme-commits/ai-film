import json
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest

from film.benchmark import (
    build_jobs,
    file_sha256,
    resolve_requirements,
    run_job,
    write_blind_review_bundle,
)

ROOT = Path(__file__).resolve().parents[2]


class BenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.matrix = json.loads(
            (ROOT / "model-evaluations/slice01/model_matrix.json").read_text(encoding="utf-8")
        )
        cls.plan = json.loads(
            (ROOT / "model-evaluations/slice01/benchmark_plan.json").read_text(encoding="utf-8")
        )
        cls.shots = json.loads(
            (ROOT / "projects/slice01/shots/benchmark_shots.json").read_text(encoding="utf-8")
        )
        cls.prompt_hashes = {
            shot["shot_id"]: file_sha256(ROOT / "projects/slice01/compiled" / f"{shot['shot_id']}.json")
            for shot in cls.shots
        }

    def test_smoke_population_is_deterministic(self):
        a = build_jobs(self.matrix, self.plan, self.shots, profile_name="smoke", prompt_hashes=self.prompt_hashes)
        b = build_jobs(self.matrix, self.plan, self.shots, profile_name="smoke", prompt_hashes=self.prompt_hashes)
        self.assertEqual(a, b)
        self.assertEqual(len(a), 4)
        self.assertEqual(len({row["job_id"] for row in a}), 4)
        self.assertTrue(all(row["model"]["stage"] == "image" for row in a))
        self.assertNotIn("qwen-image-2.1",{row["model"]["model_id"] for row in a})
        self.assertTrue(all(len(row["prompt_sha256"]) == 64 for row in a))
        self.assertTrue(all(row["model"]["execution_ready"] is False for row in a))

    def test_keyframe_core_population(self):
        jobs = build_jobs(self.matrix, self.plan, self.shots, profile_name="keyframe_core", prompt_hashes=self.prompt_hashes)
        self.assertEqual(len(jobs), 32)

    def test_video_jobs_expose_missing_reference(self):
        jobs = build_jobs(self.matrix, self.plan, self.shots, profile_name="video_core", prompt_hashes=self.prompt_hashes)
        self.assertEqual(len(jobs), 48)
        resolved = [resolve_requirements(job, None) for job in jobs]
        self.assertTrue(all(row["blocked_requirements"] == ["reference_image"] for row in resolved))

    def _runner(self, root: Path, write_artifact: bool = True, exit_code: int = 0) -> Path:
        script = root / "runner.py"
        body = [
            "#!/usr/bin/env python3",
            "from pathlib import Path",
            "import sys",
            "job=Path(sys.argv[1])",
            "out=Path(sys.argv[2])",
            "out.mkdir(parents=True, exist_ok=True)",
        ]
        if write_artifact:
            body.append("(out/'artifact.bin').write_bytes(job.read_bytes()[:64] or b'x')")
        body.append(f"raise SystemExit({exit_code})")
        script.write_text("\n".join(body) + "\n", encoding="utf-8")
        script.chmod(script.stat().st_mode | stat.S_IXUSR)
        return script

    def test_run_job_records_artifact_hash(self):
        jobs = build_jobs(self.matrix, self.plan, self.shots, profile_name="smoke", prompt_hashes=self.prompt_hashes)
        job = resolve_requirements(jobs[0], None)
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            result = run_job(job, runner_cmd=[str(self._runner(root))], job_dir=root / "job")
            self.assertEqual(result["status"], "PASS")
            self.assertEqual(len(result["artifacts"]), 1)
            self.assertEqual(result["artifacts"][0]["path"], "artifact.bin")
            self.assertEqual(len(result["artifacts"][0]["sha256"]), 64)

    def test_run_job_rejects_empty_success(self):
        jobs = build_jobs(self.matrix, self.plan, self.shots, profile_name="smoke", prompt_hashes=self.prompt_hashes)
        job = resolve_requirements(jobs[0], None)
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            result = run_job(
                job,
                runner_cmd=[str(self._runner(root, write_artifact=False))],
                job_dir=root / "job",
            )
            self.assertEqual(result["status"], "FAILED")
            self.assertEqual(result["failure"], "NO_ARTIFACTS")


    def test_run_job_timeout(self):
        jobs = build_jobs(
            self.matrix,
            self.plan,
            self.shots,
            profile_name="smoke",
            prompt_hashes=self.prompt_hashes,
        )
        job = resolve_requirements(jobs[0], None)
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            runner = root / "slow.py"
            runner.write_text(
                "#!/usr/bin/env python3\n"
                "import time\n"
                "time.sleep(5)\n",
                encoding="utf-8",
            )
            runner.chmod(runner.stat().st_mode | stat.S_IXUSR)
            result = run_job(
                job,
                runner_cmd=[str(runner)],
                job_dir=root / "job",
                timeout_sec=0.05,
                poll_interval=0.01,
            )
            self.assertEqual(result["status"], "FAILED")
            self.assertEqual(result["failure"], "TIMEOUT")

    def test_cli_dry_run_reports_model_gate_block(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "bench"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tools/run_model_benchmark.py"),
                    "--profile",
                    "smoke",
                    "--run-id",
                    "dry-gate-test",
                    "--out-root",
                    str(out),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            summary = json.loads((out / "dry-gate-test" / "run_summary.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["model_gate_blocked"], 4)
            self.assertEqual(summary["requirement_blocked"], 0)
            self.assertEqual(summary["ready_to_execute"], 0)

    def test_cli_execute_gate_blocks_unpinned_model_before_runner(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            marker = root / "runner-invoked"
            runner = root / "runner.py"
            runner.write_text(
                "#!/usr/bin/env python3\n"
                "from pathlib import Path\n"
                f"Path({str(marker)!r}).write_text('invoked')\n",
                encoding="utf-8",
            )
            runner.chmod(runner.stat().st_mode | stat.S_IXUSR)
            out = root / "bench"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tools/run_model_benchmark.py"),
                    "--profile",
                    "smoke",
                    "--execute",
                    "--runner",
                    str(runner),
                    "--max-jobs",
                    "1",
                    "--run-id",
                    "gate-test",
                    "--out-root",
                    str(out),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertFalse(marker.exists())
            summary = json.loads((out / "gate-test" / "run_summary.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["blocked"], 1)
            self.assertEqual(summary["failed"], 0)
            result_files = list((out / "gate-test" / "jobs").glob("*/result.json"))
            self.assertEqual(len(result_files), 1)
            result = json.loads(result_files[0].read_text(encoding="utf-8"))
            self.assertEqual(result["failure"], "MODEL_NOT_EXECUTION_READY")

    def test_blind_bundle_hides_model_identity(self):
        jobs = build_jobs(self.matrix, self.plan, self.shots, profile_name="smoke", prompt_hashes=self.prompt_hashes)
        job = resolve_requirements(jobs[0], None)
        result = {
            "job_id": job["job_id"],
            "status": "PASS",
            "artifacts": [{"path": "artifact.bin", "bytes": 1, "sha256": "0" * 64}],
        }
        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td)
            write_blind_review_bundle(run_dir, [job], [result])
            public = (run_dir / "blind_review_items.json").read_text(encoding="utf-8")
            private = (run_dir / "blind_map_private.json").read_text(encoding="utf-8")
            self.assertNotIn(job["model"]["model_id"], public)
            self.assertIn(job["model"]["model_id"], private)


if __name__ == "__main__":
    unittest.main()
