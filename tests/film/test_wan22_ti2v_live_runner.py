import copy
import json
from pathlib import Path
import unittest

from film.wan22_ti2v_live import (
    CODE_REVISION,
    MODEL_REVISION,
    Wan22TI2VError,
    build_generate_argv,
    validate_smoke_spec,
)

ROOT = Path(__file__).resolve().parents[2]
SPEC = json.loads((ROOT / "model-evaluations/slice01/video/wan22_ti2v_smoke.json").read_text())
MATRIX = json.loads((ROOT / "model-evaluations/slice01/model_matrix.json").read_text())
SESSION = json.loads((ROOT / "projects/slice01/runtime/gpu_session.json").read_text())


class Wan22TI2VLiveRunnerTests(unittest.TestCase):
    def test_plan_binds_exact_model_code_reference_and_paid_budget(self):
        plan = validate_smoke_spec(SPEC, matrix=MATRIX, gpu_session=SESSION)
        self.assertEqual(plan["status"], "SMOKE_AUTHORIZED_NOT_EXECUTED")
        self.assertEqual(plan["model_revision"], MODEL_REVISION)
        self.assertEqual(plan["code_revision"], CODE_REVISION)
        self.assertEqual(plan["frame_num"], 17)
        self.assertEqual(plan["sample_steps"], 5)
        self.assertFalse(plan["quality_acceptance"])
        self.assertFalse(plan["production_acceptance"])
        self.assertFalse(plan["new_resource_creation_authorized"])
        self.assertLess(
            plan["provider_billed_snapshot_usd"] + plan["proposed_max_cost_usd"],
            plan["budget_cap_usd"],
        )

    def test_plan_rejects_runtime_or_selection_drift(self):
        bad = copy.deepcopy(SPEC)
        bad["reference_role"] = "SELECTED_PRODUCTION_CAST"
        with self.assertRaisesRegex(Wan22TI2VError, "reference image role"):
            validate_smoke_spec(bad, matrix=MATRIX, gpu_session=SESSION)
        bad = copy.deepcopy(SPEC)
        bad["offload_model"] = False
        with self.assertRaisesRegex(Wan22TI2VError, "offload_model"):
            validate_smoke_spec(bad, matrix=MATRIX, gpu_session=SESSION)

    def test_generate_argv_is_official_single_gpu_i2v_shape(self):
        argv = build_generate_argv(
            SPEC,
            python_exe="/usr/bin/python3",
            wan_repo_dir=Path("/workspace/wan2.2-src"),
            model_dir=Path("/workspace/models/wan22-ti2v-5b"),
            reference_image=Path("/workspace/artifacts/blind-comparison/cmp_4720d9887d35.png"),
            output_file=Path("/workspace/runs/out.mp4"),
        )
        text = " ".join(argv)
        self.assertIn("generate.py", text)
        self.assertIn("--task ti2v-5B", text)
        self.assertIn("--size 704*1280", text)
        self.assertIn("--offload_model True", text)
        self.assertIn("--convert_model_dtype", argv)
        self.assertIn("--t5_cpu", argv)
        self.assertIn("--frame_num 17", text)
        self.assertIn("--sample_steps 5", text)
        self.assertNotIn("--use_prompt_extend", argv)


if __name__ == "__main__":
    unittest.main()