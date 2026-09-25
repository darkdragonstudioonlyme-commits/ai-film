import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from film.z_image_casting import (
    ZImageCastingError,
    build_output_manifest,
    build_smoke_plan,
    select_smoke_jobs,
    validate_execution_context,
    validate_profile,
)

ROOT=Path(__file__).resolve().parents[2]
PROFILE=json.loads((ROOT/"model-evaluations/slice01/z_image_casting_profile.json").read_text(encoding="utf-8"))
JOBS=json.loads((ROOT/"projects/slice01/casting/generation/casting_jobs.json").read_text(encoding="utf-8"))["jobs"]


class ZImageCastingSmokeRunnerTests(unittest.TestCase):
    def test_profile_and_population_are_fixed_non_authorizing(self):
        profile=validate_profile(PROFILE)
        self.assertEqual((profile["width"],profile["height"]),(1024,1024))
        self.assertEqual(profile["num_inference_steps"],50)
        self.assertEqual(profile["guidance_scale"],4.0)
        self.assertFalse(profile["cfg_normalization"])
        self.assertFalse(profile["low_cpu_mem_usage"])
        self.assertEqual(profile["negative_prompt_mode"],"NATIVE_JOB_NEGATIVE_PROMPT")
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
        self.assertTrue(all(str(row["negative_prompt"]).strip() for row in selected))
        self.assertEqual(selected,select_smoke_jobs(JOBS,PROFILE))

    def test_plan_binds_512_gate_live_runtime_authority_worker_and_budget(self):
        plan=build_smoke_plan(ROOT,PROFILE,JOBS)
        self.assertEqual(plan["status"],"READY_FOR_EXPLICIT_RUNNER_EXECUTION")
        self.assertEqual(len(plan["job_ids"]),4)
        self.assertFalse(plan["execution_permitted_by_plan"])
        self.assertEqual(plan["parameters"]["negative_prompt_mode"],"NATIVE_JOB_NEGATIVE_PROMPT")
        ctx=plan["execution_context"]
        self.assertEqual(ctx["authorization_id"],"T019-RUNPOD-A40-20260925")
        self.assertEqual(ctx["gpu"],"NVIDIA A40")
        self.assertEqual(ctx["rate_usd_per_hour"],0.49)
        self.assertEqual(ctx["runtime_torch"],"2.8.0+cu128")
        self.assertEqual(ctx["runtime_torch_cuda"],"12.8")
        self.assertEqual(ctx["runtime_diffusers"],"0.40.0")
        self.assertEqual(ctx["qualification_gate"],"PASS_512_FULL_GPU")
        self.assertEqual(ctx["worker_id"],"runpod-0h1twwxqw6yx0k-a40")
        self.assertTrue(ctx["budget"]["allowed"])
        self.assertEqual(ctx["budget"]["budget_usd"],60.0)
        self.assertFalse(ctx["new_resource_creation_authorized"])
        self.assertFalse(ctx["publish_authority"])

    def test_missing_512_gate_or_admission_promotion_fails_closed(self):
        runtime_path=ROOT/PROFILE["runtime_lock_ref"]
        worker_path=ROOT/"projects/slice01/runtime/worker_runpod_a40.json"
        runtime_original=runtime_path.read_text(encoding="utf-8")
        worker_original=worker_path.read_text(encoding="utf-8")
        try:
            runtime=json.loads(runtime_original)
            runtime["z_image_qualification"]["formal_1024_smoke_pending"]=False
            runtime_path.write_text(json.dumps(runtime),encoding="utf-8")
            with self.assertRaisesRegex(ZImageCastingError,"512 qualification gate missing"):
                validate_execution_context(ROOT,PROFILE)
        finally:
            runtime_path.write_text(runtime_original,encoding="utf-8")
        try:
            worker=json.loads(worker_original)
            worker["qualified_models"]["z-image"]["admission_ready"]=True
            worker_path.write_text(json.dumps(worker),encoding="utf-8")
            with self.assertRaisesRegex(ZImageCastingError,"must not be admission-ready"):
                validate_execution_context(ROOT,PROFILE)
        finally:
            worker_path.write_text(worker_original,encoding="utf-8")

    def test_output_manifest_binds_negative_prompt_and_remains_non_accepting(self):
        job=select_smoke_jobs(JOBS,PROFILE)[0]
        with tempfile.TemporaryDirectory() as td:
            artifact=Path(td)/"sample.png"
            artifact.write_bytes(b"z-image-formal-smoke-fixture")
            manifest=build_output_manifest(
                job,artifact,
                elapsed_sec=25.0,
                gpu_peak_memory_mb=28000,
                parameters={
                    "width":1024,"height":1024,"num_inference_steps":50,
                    "guidance_scale":4.0,"cfg_normalization":False,
                    "negative_prompt_applied":True,
                },
            )
            self.assertEqual(manifest["job_id"],job["job_id"])
            self.assertEqual(manifest["model_revision"],"04cc4abb7c5069926f75c9bfde9ef43d49423021")
            self.assertEqual(
                manifest["negative_prompt_sha256"],
                hashlib.sha256(job["negative_prompt"].encode("utf-8")).hexdigest(),
            )
            self.assertEqual(len(manifest["asset_sha256"]),64)
            self.assertEqual(len(manifest["manifest_sha256"]),64)
            self.assertFalse(manifest["production_acceptance"])
            self.assertFalse(manifest["selection_authorized"])
            self.assertFalse(manifest["publish_authority"])

    def test_plan_only_cli_requires_no_gpu_or_model_directory(self):
        proc=subprocess.run(
            [sys.executable,str(ROOT/"tools/run_z_image_casting_batch.py")],
            cwd=ROOT,text=True,capture_output=True,check=False,
        )
        self.assertEqual(proc.returncode,0,proc.stderr)
        plan=json.loads(proc.stdout)
        self.assertEqual(plan["status"],"READY_FOR_EXPLICIT_RUNNER_EXECUTION")
        self.assertEqual(plan["planned_jobs"],4)
        self.assertFalse(plan["execution_permitted_by_plan"])
        self.assertEqual(plan["parameters"]["width"],1024)
        self.assertEqual(plan["parameters"]["height"],1024)
        self.assertEqual(plan["parameters"]["num_inference_steps"],50)
        self.assertTrue(plan["parameters"]["negative_prompt_applied"])


if __name__=="__main__":
    unittest.main()
