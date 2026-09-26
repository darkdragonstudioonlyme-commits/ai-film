import json
from pathlib import Path
import unittest

from film.auto_eval import build_eval_plan, validate_policy, validate_registry

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = json.loads((ROOT / "model-evaluations/auto-eval/evaluator_registry.json").read_text())
POLICY = json.loads((ROOT / "model-evaluations/auto-eval/policy.json").read_text())
BATCH = json.loads((ROOT / "model-evaluations/auto-eval/current_batch_20260926.json").read_text())


class AutoEvalCurrentBatchTests(unittest.TestCase):
    def test_registry_and_policy_are_valid(self):
        registry = validate_registry(REGISTRY)
        policy = validate_policy(POLICY)
        self.assertEqual(registry["status"], "ACTIVE_MULTI_MODEL_AUTO_EVAL")
        self.assertEqual(policy["policy_id"], "auto-eval-ensemble-v1")

    def test_current_batch_has_12_voice_and_4_video_assets(self):
        self.assertEqual(len(BATCH["voice_assets"]), 12)
        self.assertEqual(len({x["asset_id"] for x in BATCH["voice_assets"]}), 12)
        self.assertEqual(len(BATCH["video_assets"]), 4)
        self.assertEqual(len({x["asset_id"] for x in BATCH["video_assets"]}), 4)
        self.assertFalse(BATCH["human_review_required_for_this_batch"])
        self.assertFalse(BATCH["production_acceptance"])
        self.assertFalse(BATCH["publish_authority"])

    def test_voice_assets_are_bound_to_whisper_and_cue_fit(self):
        for row in BATCH["voice_assets"]:
            self.assertEqual(row["stage"], "voice_take")
            self.assertEqual(row["required_evaluators"], ["whisper-turbo-asr"])
            self.assertIn(row["cue_fit_metric"], {0.0, 100.0})
            self.assertTrue((ROOT / row["local_path_ref"]).resolve().is_file())

    def test_video_assets_have_context_and_local_media(self):
        expected = {
            "wan22-sc01-sh04-flux2-ref-v1",
            "wan22-sc01-sh04-zimage-ref-v1",
            "world-tang-changan-motion-v1",
            "world-paris-belle-epoque-motion-v1",
        }
        self.assertEqual({x["asset_id"] for x in BATCH["video_assets"]}, expected)
        for row in BATCH["video_assets"]:
            self.assertEqual(row["stage"], "short_video_take")
            self.assertTrue((ROOT / row["local_path_ref"]).resolve().is_file())
            self.assertTrue((ROOT / row["context_ref"]).is_file())

    def test_short_video_plan_requires_three_model_evaluators_and_no_human(self):
        row = BATCH["video_assets"][0]
        plan = build_eval_plan(
            REGISTRY, POLICY,
            stage=row["stage"],
            asset_id=row["asset_id"],
            asset_path=str((ROOT / row["local_path_ref"]).resolve()),
        )
        self.assertEqual(set(x["evaluator_id"] for x in plan["required_evaluators"]), {
            "vbench-video-v0.1.5",
            "qwen3-vl-2b-semantic",
            "paddleocr-text-artifact",
        })
        self.assertEqual(plan["min_model_evaluators"], 3)
        self.assertFalse(plan["human_review_required"])
        self.assertFalse(plan["production_acceptance"])

    def test_longform_is_the_first_required_human_review_stage(self):
        row = BATCH["video_assets"][0]
        plan = build_eval_plan(
            REGISTRY, POLICY,
            stage="longform_rough_cut",
            asset_id=row["asset_id"],
            asset_path=str((ROOT / row["local_path_ref"]).resolve()),
        )
        self.assertTrue(plan["human_review_required"])
        self.assertFalse(plan["production_acceptance"])


if __name__ == "__main__":
    unittest.main()
