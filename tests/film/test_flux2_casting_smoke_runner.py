import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from film.flux2_casting import (
    Flux2CastingError,
    build_output_manifest,
    build_smoke_plan,
    select_smoke_jobs,
    validate_execution_context,
    validate_profile,
)

ROOT=Path(__file__).resolve().parents[2]
PROFILE=json.loads((ROOT/"model-evaluations/slice01/flux2_casting_profile.json").read_text(encoding="utf-8"))
JOBS=json.loads((ROOT/"projects/slice01/casting/generation/casting_jobs.json").read_text(encoding="utf-8"))["jobs"]


class Flux2CastingSmokeRunnerTests(unittest.TestCase):
    def test_profile_and_population_are_fixed_non_authorizing(self):
        profile=validate_profile(PROFILE)
        self.assertEqual((profile["width"],profile["height"]),(1024,1024))
        self.assertEqual(profile["num_inference_steps"],4)
        self.assertEqual(profile["guidance_scale"],1.0)
        self.assertEqual(profile["gpu"],"NVIDIA A40")
        self.assertFalse(profile["execution_authorized_by_profile"])
        selected=select_smoke_jobs(JOBS,PROFILE)
        self.assertEqual(len(selected),4)
        self.assertEqual(
            {(row["character_id"],row["style"],row["slot"]) for row in selected},
            {
                ("an","photoreal","face_front"),
                ("an","stylized_3d","face_front"),
                ("linh","photoreal","face_front"),
                ("linh","stylized_3d","face_front"),
            },
        )
        self.assertEqual(selected,select_smoke_jobs(JOBS,PROFILE))

    def test_plan_binds_live_runtime_authority_worker_and_budget(self):
        plan=build_smoke_plan(ROOT,PROFILE,JOBS)
        self.assertEqual(plan["status"],"READY_FOR_EXPLICIT_RUNNER_EXECUTION")
        self.assertEqual(len(plan["job_ids"]),4)
        self.assertFalse(plan["execution_permitted_by_plan"])
        ctx=plan["execution_context"]
        self.assertEqual(ctx["authorization_id"],"T019-RUNPOD-A40-20260925")
        self.assertEqual(ctx["gpu"],"NVIDIA A40")
        self.assertEqual(ctx["rate_usd_per_hour"],0.49)
        self.assertEqual(ctx["runtime_status"],"RUNPOD_A40_HOST_BOUND_RUNTIME")
        self.assertEqual(ctx["runtime_torch"],"2.8.0+cu128")
        self.assertEqual(ctx["runtime_torch_cuda"],"12.8")
        self.assertEqual(ctx["runtime_diffusers"],"0.40.0")
        self.assertEqual(ctx["worker_id"],"runpod-0h1twwxqw6yx0k-a40")
        self.assertTrue(ctx["budget"]["allowed"])
        self.assertEqual(ctx["budget"]["budget_usd"],60.0)
        self.assertFalse(ctx["new_resource_creation_authorized"])
        self.assertFalse(ctx["publish_authority"])

    def test_runtime_tamper_fails_closed(self):
        runtime_path=ROOT/PROFILE["runtime_lock_ref"]
        original=runtime_path.read_text(encoding="utf-8")
        try:
            runtime=json.loads(original)
            runtime["target"]["torch"]="9.9.9"
            runtime_path.write_text(json.dumps(runtime),encoding="utf-8")
            with self.assertRaisesRegex(Flux2CastingError,"runtime identity mismatch"):
                validate_execution_context(ROOT,PROFILE)
        finally:
            runtime_path.write_text(original,encoding="utf-8")

    def test_output_manifest_is_hash_bound_and_non_accepting(self):
        job=select_smoke_jobs(JOBS,PROFILE)[0]
        with tempfile.TemporaryDirectory() as td:
            artifact=Path(td)/"sample.png"
            artifact.write_bytes(b"smoke-test-fixture")
            manifest=build_output_manifest(
                job,artifact,
                elapsed_sec=2.5,
                gpu_peak_memory_mb=20415,
                parameters={"width":1024,"height":1024,"num_inference_steps":4,"guidance_scale":1.0},
            )
            self.assertEqual(manifest["job_id"],job["job_id"])
            self.assertEqual(manifest["job_digest"],job["job_digest"])
            self.assertEqual(manifest["model_revision"],"e7b7dc27f91deacad38e78976d1f2b499d76a294")
            self.assertEqual(len(manifest["asset_sha256"]),64)
            self.assertEqual(len(manifest["manifest_sha256"]),64)
            self.assertFalse(manifest["production_acceptance"])
            self.assertFalse(manifest["selection_authorized"])
            self.assertFalse(manifest["publish_authority"])

    def test_plan_only_cli_requires_no_gpu_or_model_directory(self):
        proc=subprocess.run(
            [sys.executable,str(ROOT/"tools/run_flux2_casting_batch.py")],
            cwd=ROOT,text=True,capture_output=True,check=False,
        )
        self.assertEqual(proc.returncode,0,proc.stderr)
        plan=json.loads(proc.stdout)
        self.assertEqual(plan["status"],"READY_FOR_EXPLICIT_RUNNER_EXECUTION")
        self.assertEqual(plan["planned_jobs"],4)
        self.assertFalse(plan["execution_permitted_by_plan"])


if __name__=="__main__":
    unittest.main()
