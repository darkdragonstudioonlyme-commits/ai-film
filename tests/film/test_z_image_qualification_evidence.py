import json
from pathlib import Path
import unittest

from film.admission import evaluate_admission
from film.cost_ledger import budget_decision

ROOT=Path(__file__).resolve().parents[2]
EVIDENCE=json.loads((ROOT/"run-evidence/Z_IMAGE_A40_QUALIFICATION_20260925.json").read_text(encoding="utf-8"))
RESOURCES=json.loads((ROOT/"model-evaluations/slice01/resource_profiles.json").read_text(encoding="utf-8"))
WORKER=json.loads((ROOT/"projects/slice01/runtime/worker_runpod_a40.json").read_text(encoding="utf-8"))
LIVE_RUNTIME=json.loads((ROOT/"model-evaluations/slice01/gpu-worker/runtime_lock.runpod_a40.json").read_text(encoding="utf-8"))
LEDGER=json.loads((ROOT/"projects/slice01/runtime/cost_ledger.json").read_text(encoding="utf-8"))
MATRIX=json.loads((ROOT/"model-evaluations/slice01/model_matrix.json").read_text(encoding="utf-8"))


class ZImageQualificationEvidenceTests(unittest.TestCase):
    def test_curated_evidence_binds_raw_artifact_and_native_negative_prompt(self):
        self.assertEqual(EVIDENCE["status"],"PASS_512_QUALIFICATION")
        self.assertEqual(EVIDENCE["model_revision"],"04cc4abb7c5069926f75c9bfde9ef43d49423021")
        self.assertEqual(EVIDENCE["job_id"],"castjob_8e02916e0db64eb6")
        self.assertEqual(EVIDENCE["raw_evidence"]["sha256"],"db0dec072f4c77aff01e5cf97d5145ec376b97e32c0d22086d4c8f2659465af4")
        self.assertEqual(EVIDENCE["raw_evidence"]["bytes"],7174)
        self.assertEqual(EVIDENCE["artifact"]["sha256"],"682f2ae66cf262004e5487d809e7c840c8a4fc2e86ba8529f98a446294a2f567")
        self.assertEqual(EVIDENCE["artifact"]["manifest_sha256"],"bd5d32cf802154bf0bb2c4ae2523cef8d0034fc3c0b8f0774a3450d0a4f19a0e")
        self.assertEqual((EVIDENCE["artifact"]["width"],EVIDENCE["artifact"]["height"]),(512,512))
        self.assertTrue(EVIDENCE["qualification"]["negative_prompt_applied"])
        self.assertFalse(EVIDENCE["production_acceptance"])
        self.assertFalse(EVIDENCE["selection_authorized"])
        self.assertFalse(EVIDENCE["publish_authority"])

    def test_historical_512_measurement_remains_exact_while_current_formal_admission_is_ready(self):
        m=EVIDENCE["measurements"]
        self.assertEqual(m["gpu_peak_memory_mb"],21913.0)
        self.assertEqual(m["nvidia_smi_after_load_mib"],20263)
        self.assertAlmostEqual(m["inference_sec"],21.623722,places=6)
        self.assertAlmostEqual(m["elapsed_sec"],34.140679,places=6)
        self.assertFalse(EVIDENCE["admission_ready_after_qualification"])
        profile=next(row for row in RESOURCES["profiles"] if row["model_id"]=="z-image")
        self.assertEqual(profile["vram_status"],"MEASURED")
        self.assertEqual(profile["production_resolution_vram_status"],"MEASURED_1024_FOUR_JOB_SMOKE")
        self.assertEqual(profile["required_vram_gb"],26.0)
        self.assertEqual(profile["vram_reserve_gb"],4.0)
        self.assertTrue(profile["admission_ready"])
        decision=evaluate_admission(profile,WORKER)
        self.assertTrue(decision["admitted"])
        self.assertEqual(decision["reasons"],[])

    def test_runtime_worker_advance_to_formal_pass_while_matrix_keeps_execution_boundary(self):
        qual=LIVE_RUNTIME["z_image_qualification"]
        self.assertEqual(qual["status"],"PASS_FORMAL_1024_FOUR_JOB")
        self.assertEqual(qual["peak_vram_mib"],26227)
        self.assertFalse(qual["formal_1024_smoke_pending"])
        self.assertTrue(qual["admission_ready"])
        self.assertEqual(qual["required_vram_gb"],26.0)
        self.assertEqual(qual["vram_reserve_gb"],4.0)
        worker=WORKER["qualified_models"]["z-image"]
        self.assertEqual(worker["status"],"PASS_FORMAL_1024_FOUR_JOB")
        self.assertEqual(worker["peak_vram_mib"],26227)
        self.assertFalse(worker["formal_1024_smoke_pending"])
        self.assertTrue(worker["admission_ready"])
        matrix=next(row for row in MATRIX["models"] if row["model_id"]=="z-image")
        self.assertFalse(matrix["execution_ready"])

    def test_cost_ledger_tracks_zimage_without_exceeding_cap(self):
        by_id={row["cost_id"]:row for row in LEDGER["entries"]}
        self.assertIn("zimage-castjob_8e02916e0db64eb6-pass",by_id)
        self.assertAlmostEqual(by_id["zimage-castjob_8e02916e0db64eb6-pass"]["amount_usd"],0.004647,places=6)
        self.assertAlmostEqual(sum(float(row["amount_usd"]) for row in LEDGER["entries"]),0.166508,places=6)
        self.assertTrue(budget_decision(LEDGER,budget_usd=60.0,proposed_charge_usd=59.83)["allowed"])
        self.assertFalse(budget_decision(LEDGER,budget_usd=60.0,proposed_charge_usd=59.84)["allowed"])


if __name__=="__main__":
    unittest.main()
