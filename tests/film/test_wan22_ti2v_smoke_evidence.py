import json
from pathlib import Path
import unittest

from film.admission import evaluate_admission

ROOT=Path(__file__).resolve().parents[2]
EV=json.loads((ROOT/"run-evidence/WAN22_TI2V_A40_SMOKE_20260926.json").read_text())
RESOURCES=json.loads((ROOT/"model-evaluations/slice01/resource_profiles.json").read_text())
WORKER=json.loads((ROOT/"projects/slice01/runtime/worker_runpod_a40.json").read_text())
LEDGER=json.loads((ROOT/"projects/slice01/runtime/cost_ledger.json").read_text())


class Wan22TI2VSmokeEvidenceTests(unittest.TestCase):
    def test_smoke_is_exact_pinned_runtime_and_non_quality(self):
        self.assertEqual(EV["status"],"PASS_RUNTIME_SMOKE")
        self.assertEqual(EV["model_id"],"wan22-ti2v-5b")
        self.assertEqual(EV["model_revision"],"921dbaf3f1674a56f47e83fb80a34bac8a8f203e")
        self.assertEqual(EV["code_revision"],"1ea34ff48f87168174e12956e200b1d908b1c5ff")
        self.assertEqual(EV["frame_num"],17)
        self.assertEqual(EV["sample_steps"],5)
        self.assertEqual(EV["returncode"],0)
        self.assertEqual(EV["quality_status"],"NOT_EVALUATED")
        self.assertFalse(EV["quality_acceptance"])
        self.assertFalse(EV["production_acceptance"])

    def test_measured_resources_and_output_are_hash_bound(self):
        self.assertEqual(EV["peak_vram_mib"],31883.0)
        self.assertAlmostEqual(EV["elapsed_sec"],266.384005,places=6)
        self.assertAlmostEqual(EV["estimated_execution_cost_usd"],0.036258,places=6)
        self.assertEqual(EV["ffprobe"]["streams"][0]["codec_name"],"h264")
        self.assertEqual(EV["ffprobe"]["streams"][0]["r_frame_rate"],"24/1")
        self.assertEqual(EV["output"]["bytes"],985395)
        self.assertEqual(
            EV["output"]["sha256"],
            "7d672b975757e2f6472ec9652a2af7e3611f2fa7f1dfba59995b18d4855e8366",
        )
        self.assertEqual(EV["local_sync"]["status"],"PASS_HASH_VERIFIED")
        self.assertEqual(EV["local_sync"]["sha256"],EV["output"]["sha256"])

    def test_wan_profile_is_admitted_but_quality_pending(self):
        profile=next(row for row in RESOURCES["profiles"] if row["model_id"]=="wan22-ti2v-5b")
        self.assertEqual(profile["vram_status"],"MEASURED")
        self.assertEqual(profile["required_vram_gb"],32.0)
        self.assertEqual(profile["vram_reserve_gb"],4.0)
        self.assertEqual(profile["smoke_peak_vram_mib"],31883.0)
        self.assertTrue(profile["admission_ready"])
        self.assertEqual(profile["quality_status"],"AWAITING_OWNER_SCORING")
        self.assertFalse(profile["production_acceptance"])
        decision=evaluate_admission(profile,WORKER)
        self.assertTrue(decision["admitted"])
        self.assertEqual(decision["reasons"],[])

    def test_worker_and_cost_ledger_include_smoke_once(self):
        wan=WORKER["qualified_models"]["wan22-ti2v-5b"]
        self.assertEqual(wan["status"],"PASS_RUNTIME_SMOKE_17F_5STEP")
        self.assertEqual(wan["peak_vram_mib"],31883)
        self.assertTrue(wan["admission_ready"])
        rows=[r for r in LEDGER["entries"] if r["cost_id"]=="wan22-ti2v-5b-a40-smoke-v1-pass"]
        self.assertEqual(len(rows),1)
        self.assertAlmostEqual(rows[0]["amount_usd"],0.036258,places=6)
        self.assertAlmostEqual(sum(float(r["amount_usd"]) for r in LEDGER["entries"]),0.455474,places=6)


if __name__=="__main__":
    unittest.main()