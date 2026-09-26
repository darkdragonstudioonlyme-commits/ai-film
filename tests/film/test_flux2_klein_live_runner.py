import copy
import json
from pathlib import Path
import tempfile
import unittest

from film.flux2_klein_live import (
    Flux2KleinQualificationError,
    REQUIRED_MODEL_FILES,
    build_cost_entry,
    build_output_manifest,
    prepare_flux2_qualification,
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
JOB=next(j for j in JOBS if j["model_id"]=="flux2-klein-4b")

def prepare(job=JOB,max_runtime_sec=1800.0,ledger=LEDGER):
    return prepare_flux2_qualification(
        job=job,matrix=MATRIX,base_runtime=BASE,live_runtime=LIVE,
        proposal=PROPOSAL,execution_plan=PLAN,rate_snapshot=RATES,
        authorization=AUTH,cost_policy=COST_POLICY,cost_ledger=ledger,
        max_runtime_sec=max_runtime_sec,
    )

class Flux2KleinLiveRunnerTests(unittest.TestCase):
    def test_plan_binds_exact_authority_model_and_budget(self):
        q=prepare()
        self.assertEqual(q["status"],"QUALIFICATION_AUTHORIZED_NOT_EXECUTED")
        self.assertEqual(q["model_revision"],"e7b7dc27f91deacad38e78976d1f2b499d76a294")
        self.assertEqual(q["authorization_id"],"T019-RUNPOD-A40-20260925")
        self.assertEqual(q["gpu"],"NVIDIA A40")
        self.assertEqual(q["qualification"]["num_inference_steps"],4)
        self.assertEqual(q["qualification"]["guidance_scale"],1.0)
        self.assertAlmostEqual(q["proposed_max_cost_usd"],0.245,places=6)
        self.assertAlmostEqual(q["current_ledger_cost_usd"],0.166508,places=6)
        self.assertFalse(q["new_resource_creation_authorized"])
        self.assertFalse(q["publish_authority"])
        self.assertFalse(q["request"]["execution_permitted"])

    def test_wrong_revision_rejected(self):
        bad=copy.deepcopy(JOB)
        bad["model_revision"]="0"*40
        with self.assertRaisesRegex(Flux2KleinQualificationError,"source identity drift"):
            prepare(bad)

    def test_budget_worst_case_rejected(self):
        with self.assertRaisesRegex(Flux2KleinQualificationError,"exceed project budget"):
            prepare(max_runtime_sec=500000.0)

    def test_model_dir_requires_exact_component_shape(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            with self.assertRaisesRegex(Flux2KleinQualificationError,"missing required files"):
                validate_model_dir(root)
            for rel in REQUIRED_MODEL_FILES:
                p=root/rel
                p.parent.mkdir(parents=True,exist_ok=True)
                p.write_bytes(b"x")
            shape=validate_model_dir(root)
            self.assertEqual(shape["required_file_count"],18)
            self.assertEqual(shape["required_bytes"],18)

    def test_output_manifest_validates_and_cost_entry_tracks_pass_fail(self):
        q=prepare()
        with tempfile.TemporaryDirectory() as td:
            artifact=Path(td)/"x.png"
            artifact.write_bytes(b"fake-png-bytes")
            m=build_output_manifest(
                request=q["request"],artifact_path=artifact,elapsed_sec=10.0,
                gpu_peak_memory_mb=1234.0,runtime={"torch":"2.8.0+cu128"},
            )
            self.assertEqual(m["model_id"],"flux2-klein-4b")
            self.assertEqual(len(m["asset_sha256"]),64)
            self.assertEqual(len(m["manifest_sha256"]),64)
            passed=build_cost_entry(qualification=q,elapsed_sec=10.0,passed=True,asset_id=m["asset_id"])
            failed=build_cost_entry(qualification=q,elapsed_sec=10.0,passed=False,asset_id=None)
            self.assertEqual(passed["category"],"COMPUTE_ACCEPTED")
            self.assertEqual(failed["category"],"COMPUTE_FAILED")
            self.assertAlmostEqual(passed["amount_usd"],round(10*0.49/3600,6),places=6)

if __name__=="__main__":
    unittest.main()
