import json
import re
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
MATRIX=json.loads((ROOT/"model-evaluations/slice01/model_matrix.json").read_text(encoding="utf-8"))
PINS=json.loads((ROOT/"model-evaluations/slice01/upstream_pins_2026-09-24.json").read_text(encoding="utf-8"))
TTS=json.loads((ROOT/"run-evidence/CPU_TTS_SMOKE_20260924.json").read_text(encoding="utf-8"))
VOICE=json.loads((ROOT/"projects/slice01/timing/voice_plan.json").read_text(encoding="utf-8"))
RENTAL=json.loads((ROOT/"model-evaluations/slice01/GPU_RENTAL_PROPOSAL_2026-09-24.json").read_text(encoding="utf-8"))


class Batch003ContractTests(unittest.TestCase):
    def test_active_model_pins_are_exact_and_execution_gated(self):
        pins={row["model_id"]:row for row in PINS["models"]}
        pinned=[m for m in MATRIX["models"] if m.get("pin_status")=="PINNED"]
        self.assertEqual(len(pinned),len(MATRIX["models"]))
        for model in pinned:
            self.assertRegex(model["source_revision"],r"^[0-9a-f]{40}$")
            self.assertEqual(model["source_revision"],pins[model["model_id"]]["source_revision"])
            self.assertNotIn("tbd",model["checkpoint"].lower())
            self.assertFalse(model["execution_ready"])

    def test_qwen_21_is_not_commercially_enabled(self):
        qwen=next(m for m in MATRIX["models"] if m["model_id"]=="qwen-image-2.1")
        self.assertFalse(qwen["enabled"])
        self.assertFalse(qwen["commercial_production_allowed"])
        self.assertEqual(qwen["license_hint"],"qwen-research")

    def test_latentsync_license_is_corrected(self):
        latent=next(m for m in MATRIX["models"] if m["model_id"]=="latent-sync")
        self.assertEqual(latent["license_hint"],"openrail++")
        self.assertIn("LEGAL_REVIEW",latent["license_gate"])
        self.assertEqual(latent["pin_status"],"PINNED")
        self.assertRegex(latent["source_revision"],r"^[0-9a-f]{40}$")


    def test_core_visual_candidates_remain_enabled_for_evaluation(self):
        enabled={m["model_id"] for m in MATRIX["models"] if m.get("enabled")}
        self.assertTrue({"z-image","flux2-klein-4b","wan22-ti2v-5b","wan22-i2v-14b","ltx-2.5"} <= enabled)
        for model in MATRIX["models"]:
            if model.get("model_id") in {"z-image","flux2-klein-4b","wan22-ti2v-5b","wan22-i2v-14b"}:
                self.assertEqual(model["commercial_production_allowed"],"UPSTREAM_MODEL_LICENSE_PERMITS")
                self.assertEqual(model["production_gate"],"PENDING_DEPENDENCY_DATASET_AND_PUBLICATION_REVIEW")

    def test_cpu_tts_measured_feasibility(self):
        self.assertEqual(TTS["status"],"PASS")
        self.assertEqual(set(TTS["languages_tested"]),{"en","vi"})
        self.assertEqual(len(TTS["samples"]),4)
        self.assertTrue(all(row["fits_cue_budget"] for row in TTS["samples"]))
        self.assertLess(TTS["rtf_mean"],1.0)
        self.assertEqual(TTS["package_version"],"3.8.3")
        self.assertEqual(TTS["onnxruntime_version"],"1.30.0")

    def test_zh_voice_route_is_multilingual_candidate(self):
        self.assertEqual(VOICE["zh_route"]["model_id"],"voxcpm2")
        self.assertEqual(VOICE["production_multilingual_candidate"]["model_id"],"voxcpm2")
        self.assertEqual(VOICE["cpu_previs_candidate"]["model_id"],"vieneu-v3-turbo")

    def test_rental_proposal_is_non_executing_and_bounded(self):
        computed=round(sum(float(x["compute_ceiling_usd"]) for x in RENTAL["stages"]),2)
        self.assertEqual(computed,99.00)
        self.assertEqual(RENTAL["compute_ceiling_usd"],99.00)
        self.assertEqual(RENTAL["hard_all_in_authorization_cap_usd"],150.00)
        self.assertEqual(RENTAL["initial_execution_subcap_usd"],60.00)
        self.assertLess(RENTAL["initial_execution_subcap_usd"],RENTAL["hard_all_in_authorization_cap_usd"])
        self.assertFalse(RENTAL["launch_authorized"])
        self.assertFalse(RENTAL["spend_authorized"])
        self.assertLess(RENTAL["compute_ceiling_usd"],RENTAL["hard_all_in_authorization_cap_usd"])


if __name__=="__main__":
    unittest.main()
