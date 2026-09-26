import json
from pathlib import Path
import tempfile
import unittest

from film.image_keyframe_live import build_evidence,select_probe_job,validate_probe_job
from film.batch_orchestrator import build_argv,validate_config

ROOT=Path(__file__).resolve().parents[2]
SPEC=json.loads((ROOT/"model-evaluations/slice01/video/keyframe_probe_sc01_sh04.json").read_text())
MATRIX=json.loads((ROOT/"model-evaluations/slice01/model_matrix.json").read_text())
RESOURCES=json.loads((ROOT/"model-evaluations/slice01/resource_profiles.json").read_text())
WORKER=json.loads((ROOT/"projects/slice01/runtime/worker_runpod_a40.json").read_text())
SESSION=json.loads((ROOT/"projects/slice01/runtime/gpu_session.json").read_text())
BATCH=json.loads((ROOT/"model-evaluations/slice01/batches/sc01_sh04_portrait_keyframes_20260926.json").read_text())


class ImageKeyframeLiveTests(unittest.TestCase):
    def test_probe_is_balanced_two_model_portrait_pair(self):
        self.assertEqual(SPEC["shot_id"],"sc01_sh04")
        self.assertEqual(SPEC["style"],"photoreal")
        self.assertEqual({j["model_id"] for j in SPEC["jobs"]},{"flux2-klein-4b","z-image"})
        self.assertTrue(all(j["width"]==704 and j["height"]==1280 for j in SPEC["jobs"]))
        self.assertEqual({j["seed"] for j in SPEC["jobs"]},{104})
        self.assertFalse(SPEC["selection_authorized"])
        self.assertFalse(SPEC["quality_acceptance"])

    def test_both_jobs_pass_current_a40_admission_and_budget_guard(self):
        for row in SPEC["jobs"]:
            plan=validate_probe_job(
                SPEC,row,matrix=MATRIX,resources=RESOURCES,worker=WORKER,gpu_session=SESSION
            )
            self.assertEqual(plan["status"],"KEYFRAME_PROBE_AUTHORIZED_NOT_EXECUTED")
            self.assertLess(plan["provider_billed_snapshot_usd"]+plan["proposed_max_cost_usd"],plan["budget_cap_usd"])
            self.assertFalse(plan["selection_authorized"])
            self.assertEqual(plan["quality_status"],"NOT_EVALUATED")

    def test_evidence_hash_binds_output_without_selecting_model(self):
        job=select_probe_job(SPEC,"sc01-sh04-flux2-portrait-v1")
        plan=validate_probe_job(SPEC,job,matrix=MATRIX,resources=RESOURCES,worker=WORKER,gpu_session=SESSION)
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"x.png"; p.write_bytes(b"probe")
            ev=build_evidence(plan,artifact=p,elapsed_sec=2.5,peak_vram_mib=20000)
        self.assertEqual(ev["status"],"PASS_RUNTIME")
        self.assertEqual(ev["quality_status"],"AWAITING_OWNER_SCORING")
        self.assertFalse(ev["selection_authorized"])
        self.assertFalse(ev["production_acceptance"])
        self.assertEqual(len(ev["output"]["sha256"]),64)

    def test_batch_orchestrator_uses_keyframe_adapter_for_both_models(self):
        jobs=validate_config(BATCH)
        self.assertEqual(len(jobs),2)
        self.assertEqual({j["adapter"] for j in jobs},{"image-keyframe-live"})
        for job in jobs:
            argv=build_argv(job,root=ROOT,execute=True)
            self.assertEqual(argv[0],"/workspace/venvs/aifilm/bin/python")
            self.assertEqual(argv[1],str(ROOT/"tools/run_image_keyframe_live.py"))
            self.assertIn("--probe-job-id",argv)
            self.assertIn("--execute",argv)


if __name__=="__main__":
    unittest.main()
