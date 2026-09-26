import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from film.z_image_live import (
    REQUIRED_MODEL_FILES,
    ZImageQualificationError,
    build_cost_entry,
    build_output_manifest,
    prepare_z_image_qualification,
    validate_model_dir,
)

ROOT=Path(__file__).resolve().parents[2]
MATRIX=json.loads((ROOT/"model-evaluations/slice01/model_matrix.json").read_text())
BASE=json.loads((ROOT/"model-evaluations/slice01/gpu-worker/runtime_lock.json").read_text())
LIVE=json.loads((ROOT/"model-evaluations/slice01/gpu-worker/runtime_lock.runpod_a40.json").read_text())
PROPOSAL=json.loads((ROOT/"model-evaluations/slice01/GPU_RENTAL_PROPOSAL_2026-09-24.json").read_text())
PLAN=json.loads((ROOT/"model-evaluations/slice01/GPU_RENTAL_EXECUTION_PLAN_20260925.json").read_text())
RATES=json.loads((ROOT/"model-evaluations/slice01/rate_snapshot_20260925.json").read_text())
AUTH=json.loads((ROOT/"model-evaluations/slice01/launch_authorization.active.json").read_text())
COST_POLICY=json.loads((ROOT/"projects/slice01/runtime/cost_policy.json").read_text())
LEDGER=json.loads((ROOT/"projects/slice01/runtime/cost_ledger.json").read_text())
JOBS=json.loads((ROOT/"projects/slice01/casting/generation/casting_jobs.json").read_text())["jobs"]
JOB=next(j for j in JOBS if j["job_id"]=="castjob_8e02916e0db64eb6")


def prepare(job=JOB,max_runtime_sec=1800.0,ledger=LEDGER):
    return prepare_z_image_qualification(
        job=job,matrix=MATRIX,base_runtime=BASE,live_runtime=LIVE,
        proposal=PROPOSAL,execution_plan=PLAN,rate_snapshot=RATES,
        authorization=AUTH,cost_policy=COST_POLICY,cost_ledger=ledger,
        max_runtime_sec=max_runtime_sec,
    )


class ZImageLiveRunnerTests(unittest.TestCase):
    def test_plan_binds_exact_authority_model_upstream_params_and_pending_production_gate(self):
        q=prepare()
        self.assertEqual(q["status"],"QUALIFICATION_AUTHORIZED_NOT_EXECUTED")
        self.assertEqual(q["model_id"],"z-image")
        self.assertEqual(q["model_revision"],"04cc4abb7c5069926f75c9bfde9ef43d49423021")
        self.assertEqual(q["authorization_id"],"T019-RUNPOD-A40-20260925")
        self.assertEqual(q["gpu"],"NVIDIA A40")
        self.assertEqual(q["qualification"]["num_inference_steps"],50)
        self.assertEqual(q["qualification"]["guidance_scale"],4.0)
        self.assertFalse(q["qualification"]["cfg_normalization"])
        self.assertFalse(q["qualification"]["low_cpu_mem_usage"])
        self.assertEqual(q["negative_prompt_handling"],"APPLIED_NATIVE_ZIMAGE_PIPELINE_STRING")
        self.assertEqual(q["production_gate"],"PENDING_DEPENDENCY_DATASET_AND_PUBLICATION_REVIEW")
        self.assertAlmostEqual(q["proposed_max_cost_usd"],0.245,places=6)
        self.assertAlmostEqual(q["current_ledger_cost_usd"],0.455474,places=6)
        self.assertFalse(q["new_resource_creation_authorized"])
        self.assertFalse(q["production_acceptance"])
        self.assertFalse(q["selection_authorized"])
        self.assertFalse(q["publish_authority"])
        self.assertFalse(q["request"]["execution_permitted"])

    def test_wrong_revision_and_wrong_model_are_rejected(self):
        bad=copy.deepcopy(JOB)
        bad["model_revision"]="0"*40
        with self.assertRaisesRegex(ZImageQualificationError,"source identity drift"):
            prepare(bad)
        bad=copy.deepcopy(JOB)
        bad["model_id"]="flux2-klein-4b"
        with self.assertRaisesRegex(ZImageQualificationError,"not Z-Image"):
            prepare(bad)

    def test_budget_worst_case_rejected(self):
        with self.assertRaisesRegex(ZImageQualificationError,"exceed project budget"):
            prepare(max_runtime_sec=500000.0)

    def test_model_dir_requires_exact_component_shape(self):
        self.assertEqual(len(REQUIRED_MODEL_FILES),18)
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            with self.assertRaisesRegex(ZImageQualificationError,"missing required files"):
                validate_model_dir(root)
            for rel in REQUIRED_MODEL_FILES:
                p=root/rel
                p.parent.mkdir(parents=True,exist_ok=True)
                p.write_bytes(b"x")
            shape=validate_model_dir(root)
            self.assertEqual(shape["required_file_count"],18)
            self.assertEqual(shape["required_bytes"],18)

    def test_output_manifest_cost_and_plan_only_cli_are_hash_bound(self):
        q=prepare()
        with tempfile.TemporaryDirectory() as td:
            artifact=Path(td)/"z.png"
            artifact.write_bytes(b"fake-z-image-png")
            m=build_output_manifest(
                request=q["request"],artifact_path=artifact,
                elapsed_sec=12.0,gpu_peak_memory_mb=20000,
                runtime={"torch":"2.8.0+cu128","negative_prompt_applied":True},
            )
            self.assertEqual(m["model_id"],"z-image")
            self.assertEqual(m["model_revision"],"04cc4abb7c5069926f75c9bfde9ef43d49423021")
            self.assertEqual(len(m["asset_sha256"]),64)
            self.assertEqual(len(m["manifest_sha256"]),64)
            cost=build_cost_entry(qualification=q,elapsed_sec=12.0,passed=True,asset_id=m["asset_id"])
            self.assertEqual(cost["category"],"COMPUTE_ACCEPTED")
            self.assertAlmostEqual(cost["amount_usd"],round(12*0.49/3600,6),places=6)
        proc=subprocess.run(
            [sys.executable,str(ROOT/"tools/run_z_image_live.py"),"--job-id",JOB["job_id"]],
            cwd=ROOT,text=True,capture_output=True,check=False,
        )
        self.assertEqual(proc.returncode,0,proc.stderr)
        plan=json.loads(proc.stdout)
        self.assertEqual(plan["status"],"QUALIFICATION_AUTHORIZED_NOT_EXECUTED")
        self.assertEqual(plan["model_id"],"z-image")
        self.assertFalse(plan["request"]["execution_permitted"])


if __name__=="__main__":
    unittest.main()