import json
from pathlib import Path
import unittest

from film.batch_orchestrator import build_argv, validate_config
from film.image_keyframe_live import select_probe_job, validate_probe_job

ROOT=Path(__file__).resolve().parents[2]
SPEC=json.loads((ROOT/"model-evaluations/world-capability/image_probe_historical_v1.json").read_text())
BATCH=json.loads((ROOT/"model-evaluations/world-capability/batch_historical_keyframes_20260926.json").read_text())
MATRIX=json.loads((ROOT/"model-evaluations/slice01/model_matrix.json").read_text())
RESOURCES=json.loads((ROOT/"model-evaluations/slice01/resource_profiles.json").read_text())
WORKER=json.loads((ROOT/"projects/slice01/runtime/worker_runpod_a40.json").read_text())
SESSION=json.loads((ROOT/"projects/slice01/runtime/gpu_session.json").read_text())
RUNNING_SESSION={**SESSION,"provider_state":"RUNNING"}


class WorldCapabilityProbeTests(unittest.TestCase):
    def test_probe_covers_historical_china_and_european_period_cinema(self):
        self.assertEqual(SPEC["status"],"READY_NOT_EXECUTED")
        self.assertFalse(SPEC["selection_authorized"])
        ids={j["world_profile_id"] for j in SPEC["jobs"]}
        self.assertEqual(ids,{"china_tang_changan_8c","europe_belle_epoque_paris_1900s"})
        self.assertEqual({j["model_id"] for j in SPEC["jobs"]},{"flux2-klein-4b"})

    def test_world_prompts_are_specific_and_text_free(self):
        tang=select_probe_job(SPEC,"world-tang-changan-cast-v1")
        paris=select_probe_job(SPEC,"world-paris-belle-epoque-cast-v2")
        self.assertIn("Tang dynasty",tang["prompt"])
        self.assertIn("Chang'an",tang["prompt"])
        self.assertIn("Chinese woman",tang["prompt"])
        self.assertIn("Qing queue hairstyle",tang["negative_prompt"])
        self.assertIn("Belle",paris["prompt"])
        self.assertIn("Paris",paris["prompt"])
        self.assertIn("French man",paris["prompt"])
        self.assertIn("modern cars",paris["negative_prompt"])
        self.assertIn("No newspaper",paris["prompt"])
        self.assertIn("readable typography is added only in post-production",paris["prompt"])
        for row in (tang,paris):
            self.assertIn("No written words",row["prompt"])
            self.assertNotIn("voice",row["prompt"].lower())
            self.assertEqual(row["style"],"photoreal")

    def test_both_jobs_pass_existing_a40_admission_and_budget_guard(self):
        for row in SPEC["jobs"]:
            plan=validate_probe_job(
                SPEC,row,
                matrix=MATRIX,
                resources=RESOURCES,
                worker=WORKER,
                gpu_session=RUNNING_SESSION,
            )
            self.assertEqual(plan["status"],"KEYFRAME_PROBE_AUTHORIZED_NOT_EXECUTED")
            self.assertEqual(plan["model_id"],"flux2-klein-4b")
            self.assertLess(plan["provider_billed_snapshot_usd"]+plan["proposed_max_cost_usd"],plan["budget_cap_usd"])
            self.assertFalse(plan["production_acceptance"])

    def test_batch_passes_spec_path_to_shared_image_adapter(self):
        jobs=validate_config(BATCH)
        self.assertEqual(len(jobs),2)
        for job in jobs:
            argv=build_argv(job,root=ROOT,execute=True)
            self.assertEqual(argv[1],str(ROOT/"tools/run_image_keyframe_live.py"))
            self.assertIn("--spec-path",argv)
            self.assertIn("model-evaluations/world-capability/image_probe_historical_v1.json",argv)
            self.assertIn("--execute",argv)


if __name__=="__main__":
    unittest.main()