import json
from pathlib import Path
import unittest

from film.batch_orchestrator import build_argv, validate_config
from film.wan22_ti2v_live import validate_smoke_spec

ROOT=Path(__file__).resolve().parents[2]
TANG=json.loads((ROOT/"model-evaluations/world-capability/wan22_tang_motion_smoke.json").read_text())
PARIS=json.loads((ROOT/"model-evaluations/world-capability/wan22_paris_motion_smoke.json").read_text())
BATCH=json.loads((ROOT/"model-evaluations/world-capability/batch_historical_motion_20260926.json").read_text())
MATRIX=json.loads((ROOT/"model-evaluations/slice01/model_matrix.json").read_text())
SESSION=json.loads((ROOT/"projects/slice01/runtime/gpu_session.json").read_text())
RUNNING_SESSION={**SESSION,"provider_state":"RUNNING"}


class WorldCapabilityMotionTests(unittest.TestCase):
    def test_two_world_motion_smokes_share_bounded_runtime_shape(self):
        self.assertEqual(TANG["frame_num"],17)
        self.assertEqual(PARIS["frame_num"],17)
        self.assertEqual(TANG["sample_steps"],5)
        self.assertEqual(PARIS["sample_steps"],5)
        self.assertEqual(TANG["size"],"704*1280")
        self.assertEqual(PARIS["size"],"704*1280")
        self.assertFalse(TANG["quality_acceptance"])
        self.assertFalse(PARIS["production_acceptance"])

    def test_prompts_preserve_distinct_worlds_without_text_generation(self):
        self.assertIn("Tang-dynasty Chang'an",TANG["prompt"])
        self.assertIn("no written text",TANG["prompt"])
        self.assertIn("Belle Époque Paris",PARIS["prompt"])
        self.assertIn("no newspaper",PARIS["prompt"])
        self.assertIn("no storefront lettering",PARIS["prompt"])
        self.assertNotEqual(TANG["reference_image_sha256"],PARIS["reference_image_sha256"])

    def test_both_specs_pass_existing_wan_admission_and_paid_guard(self):
        for spec in (TANG,PARIS):
            plan=validate_smoke_spec(spec,matrix=MATRIX,gpu_session=RUNNING_SESSION)
            self.assertEqual(plan["status"],"SMOKE_AUTHORIZED_NOT_EXECUTED")
            self.assertEqual(plan["frame_num"],17)
            self.assertEqual(plan["sample_steps"],5)
            self.assertLess(plan["provider_billed_snapshot_usd"]+plan["proposed_max_cost_usd"],plan["budget_cap_usd"])
            self.assertFalse(plan["production_acceptance"])

    def test_batch_uses_shared_wan_adapter_with_per_world_spec_paths(self):
        jobs=validate_config(BATCH)
        self.assertEqual(len(jobs),2)
        self.assertEqual({j["adapter"] for j in jobs},{"wan22-ti2v-live"})
        argv0=build_argv(jobs[0],root=ROOT,execute=True)
        argv1=build_argv(jobs[1],root=ROOT,execute=True)
        self.assertIn("--spec-path",argv0)
        self.assertIn("wan22_tang_motion_smoke.json"," ".join(argv0))
        self.assertIn("wan22_paris_motion_smoke.json"," ".join(argv1))
        self.assertIn("--reference-image",argv0)
        self.assertIn("--execute",argv1)


if __name__=="__main__":
    unittest.main()