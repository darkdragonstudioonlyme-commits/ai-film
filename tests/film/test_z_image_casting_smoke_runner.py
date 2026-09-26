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

    def test_plan_reports_formal_smoke_complete_and_no_rerun(self):
        plan=build_smoke_plan(ROOT,PROFILE,JOBS)
        self.assertEqual(plan["status"],"FORMAL_SMOKE_COMPLETE_NO_RERUN")
        self.assertEqual(len(plan["job_ids"]),4)
        self.assertFalse(plan["execution_permitted_by_plan"])
        self.assertEqual(plan["execution_context"]["qualification_gate"],"PASS_FORMAL_1024_FOUR_JOB")
        self.assertTrue(plan["execution_context"]["formal_smoke_complete"])
        self.assertFalse(plan["execution_context"]["new_resource_creation_authorized"])
        self.assertFalse(plan["execution_context"]["publish_authority"])

    def test_runtime_worker_completion_must_match(self):
        runtime_path=ROOT/PROFILE["runtime_lock_ref"]
        worker_path=ROOT/"projects/slice01/runtime/worker_runpod_a40.json"
        runtime_original=runtime_path.read_text(encoding="utf-8")
        worker_original=worker_path.read_text(encoding="utf-8")
        try:
            runtime=json.loads(runtime_original)
            runtime["z_image_qualification"]["admission_ready"]=False
            runtime_path.write_text(json.dumps(runtime),encoding="utf-8")
            with self.assertRaisesRegex(ZImageCastingError,"gate inconsistent"):
                validate_execution_context(ROOT,PROFILE)
        finally:
            runtime_path.write_text(runtime_original,encoding="utf-8")
        try:
            worker=json.loads(worker_original)
            worker["qualified_models"]["z-image"]["formal_1024_smoke_pending"]=True
            worker_path.write_text(json.dumps(worker),encoding="utf-8")
            with self.assertRaisesRegex(ZImageCastingError,"gate inconsistent"):
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
            self.assertEqual(
                manifest["negative_prompt_sha256"],
                hashlib.sha256(job["negative_prompt"].encode("utf-8")).hexdigest(),
            )
            self.assertFalse(manifest["production_acceptance"])
            self.assertFalse(manifest["selection_authorized"])
            self.assertFalse(manifest["publish_authority"])

    def test_plan_only_cli_reports_complete_and_execute_rerun_is_blocked(self):
        proc=subprocess.run(
            [sys.executable,str(ROOT/"tools/run_z_image_casting_batch.py")],
            cwd=ROOT,text=True,capture_output=True,check=False,
        )
        self.assertEqual(proc.returncode,0,proc.stderr)
        plan=json.loads(proc.stdout)
        self.assertEqual(plan["status"],"FORMAL_SMOKE_COMPLETE_NO_RERUN")
        self.assertEqual(plan["planned_jobs"],4)
        self.assertFalse(plan["execution_permitted_by_plan"])

        proc=subprocess.run(
            [sys.executable,str(ROOT/"tools/run_z_image_casting_batch.py"),"--execute"],
            cwd=ROOT,text=True,capture_output=True,check=False,
        )
        self.assertNotEqual(proc.returncode,0)
        self.assertIn("formal smoke already complete",proc.stderr)


if __name__=="__main__":
    unittest.main()
