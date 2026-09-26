import json
from pathlib import Path
import unittest

from film.batch_orchestrator import build_argv, validate_config
from film.wan22_ti2v_live import validate_smoke_spec
from tools.run_wan22_quality_live import select_job

ROOT=Path(__file__).resolve().parents[2]
SPEC=json.loads((ROOT/"model-evaluations/slice01/video/wan22_quality_probe_sc01_sh04.json").read_text())
BATCH=json.loads((ROOT/"model-evaluations/slice01/batches/wan22_sc01_sh04_balanced_motion_20260926.json").read_text())
MATRIX=json.loads((ROOT/"model-evaluations/slice01/model_matrix.json").read_text())
SESSION=json.loads((ROOT/"projects/slice01/runtime/gpu_session.json").read_text())
RUNNING_SESSION={**SESSION,"provider_state":"RUNNING"}


class Wan22QualityProbeTests(unittest.TestCase):
    def test_balanced_probe_has_two_reference_models_same_generation_settings(self):
        self.assertEqual(SPEC["frame_num"],25)
        self.assertEqual(SPEC["sample_steps"],8)
        self.assertEqual(SPEC["base_seed"],52004)
        self.assertEqual({j["reference_model_id"] for j in SPEC["jobs"]},{"flux2-klein-4b","z-image"})
        self.assertEqual(len({j["reference_image_sha256"] for j in SPEC["jobs"]}),2)
        self.assertFalse(SPEC["selection_authorized"])
        self.assertFalse(SPEC["quality_acceptance"])

    def test_each_job_passes_same_paid_runtime_guard(self):
        for row in SPEC["jobs"]:
            merged={k:v for k,v in SPEC.items() if k!="jobs"}
            merged.update({
                "smoke_id":row["probe_job_id"],
                "reference_image_sha256":row["reference_image_sha256"],
                "reference_role":row["reference_role"],
                "max_runtime_sec":row["max_runtime_sec"],
            })
            plan=validate_smoke_spec(merged,matrix=MATRIX,gpu_session=RUNNING_SESSION)
            self.assertEqual(plan["frame_num"],25)
            self.assertEqual(plan["sample_steps"],8)
            self.assertFalse(plan["production_acceptance"])

    def test_batch_uses_quality_adapter_and_explicit_runtime(self):
        jobs=validate_config(BATCH)
        self.assertEqual(len(jobs),2)
        self.assertEqual({j["adapter"] for j in jobs},{"wan22-quality-live"})
        argv=build_argv(jobs[0],root=ROOT,execute=True)
        self.assertEqual(argv[1],str(ROOT/"tools/run_wan22_quality_live.py"))
        self.assertIn("--probe-job-id",argv)
        self.assertIn("--wan-repo-dir",argv)
        self.assertIn("--reference-image",argv)
        self.assertIn("--execute",argv)


if __name__=="__main__":
    unittest.main()