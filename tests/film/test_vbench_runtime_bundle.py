import json
from pathlib import Path
import unittest

from tools.setup_vbench_runtime import build_commands

ROOT=Path(__file__).resolve().parents[2]
LOCK=json.loads((ROOT/"model-evaluations/auto-eval/vbench_runtime_lock.json").read_text())
PENDING=json.loads((ROOT/"model-evaluations/auto-eval/vbench_pending_20260926.json").read_text())


class VBenchRuntimeBundleTests(unittest.TestCase):
    def test_runtime_lock_matches_upstream_cuda_and_custom_dimensions(self):
        self.assertEqual(LOCK["code_repo"],"Vchitect/VBench")
        self.assertEqual(LOCK["code_revision"],"fd18b3d055cb0fc6f066ca90fe2c3c8cbb698490")
        self.assertEqual(LOCK["package"],"vbench==0.1.5")
        self.assertEqual(LOCK["required_torch_cuda"],"12.1")
        self.assertEqual(LOCK["mode"],"custom_input")
        self.assertEqual(set(LOCK["dimensions"]),{
            "subject_consistency","background_consistency","motion_smoothness",
            "dynamic_degree","aesthetic_quality","imaging_quality",
        })
        self.assertFalse(LOCK["detectron2_required_for_selected_dimensions"])
        self.assertFalse(LOCK["new_resource_creation_authorized"])

    def test_setup_plan_pins_cu121_and_exact_repo_revision(self):
        commands=build_commands(LOCK)
        joined=[" ".join(cmd) for cmd in commands]
        self.assertTrue(any("torch==2.5.1" in x and "torchvision==0.20.1" in x and "cu121" in x for x in joined))
        self.assertTrue(any("checkout --detach "+LOCK["code_revision"] in x for x in joined))
        self.assertTrue(any("--no-deps -e "+LOCK["code_dir"] in x for x in joined))
        self.assertTrue(joined[-1].endswith("tools/validate_vbench_runtime.py"))

    def test_pending_gpu_work_is_three_clips_only(self):
        self.assertEqual(PENDING["eligible_count"],3)
        self.assertEqual(len(PENDING["eligible_asset_ids"]),3)
        self.assertNotIn("wan22-sc01-sh04-zimage-ref-v1",PENDING["eligible_asset_ids"])
        self.assertFalse(PENDING["new_resource_creation_authorized"])


if __name__=="__main__":
    unittest.main()
