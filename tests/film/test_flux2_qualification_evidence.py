import json
from pathlib import Path
import unittest

from film.admission import evaluate_admission
from film.cost_ledger import budget_decision

ROOT=Path(__file__).resolve().parents[2]
EVIDENCE=json.loads((ROOT/"run-evidence/FLUX2_KLEIN_A40_QUALIFICATION_20260925.json").read_text(encoding="utf-8"))
RESOURCES=json.loads((ROOT/"model-evaluations/slice01/resource_profiles.json").read_text(encoding="utf-8"))
WORKER=json.loads((ROOT/"projects/slice01/runtime/worker_runpod_a40.json").read_text(encoding="utf-8"))
LIVE_RUNTIME=json.loads((ROOT/"model-evaluations/slice01/gpu-worker/runtime_lock.runpod_a40.json").read_text(encoding="utf-8"))
LEDGER=json.loads((ROOT/"projects/slice01/runtime/cost_ledger.json").read_text(encoding="utf-8"))


class Flux2QualificationEvidenceTests(unittest.TestCase):
    def test_curated_evidence_binds_raw_and_artifact_identity(self):
        self.assertEqual(EVIDENCE["status"],"PASS_512_QUALIFICATION")
        self.assertEqual(EVIDENCE["model_revision"],"e7b7dc27f91deacad38e78976d1f2b499d76a294")
        self.assertEqual(EVIDENCE["job_id"],"castjob_d3ec86da4ca6b1fc")
        self.assertEqual(EVIDENCE["raw_evidence"]["sha256"],"494b833da19cc03b9dc4146f0c74eeab0ed0d2adb1fe7f07c9247348c1bbf7df")
        self.assertEqual(EVIDENCE["artifact"]["sha256"],"f1af28a78a13be0bc8f3cb82f591f6c2bfa7046658b51b142c67532dc2871bf9")
        self.assertEqual((EVIDENCE["artifact"]["width"],EVIDENCE["artifact"]["height"]),(512,512))
        self.assertFalse(EVIDENCE["production_acceptance"])
        self.assertFalse(EVIDENCE["selection_authorized"])

    def test_measurements_are_real_but_formal_admission_stays_closed(self):
        self.assertEqual(EVIDENCE["measurements"]["gpu_peak_memory_mb"],16577.0)
        self.assertEqual(EVIDENCE["measurements"]["inference_sec"],1.285966)
        profile=next(row for row in RESOURCES["profiles"] if row["model_id"]=="flux2-klein-4b")
        self.assertEqual(profile["vram_status"],"MEASURED_512_QUALIFICATION")
        self.assertEqual(profile["production_resolution_vram_status"],"UNMEASURED_1024_SMOKE_PENDING")
        self.assertIsNone(profile["required_vram_gb"])
        self.assertFalse(profile["admission_ready"])
        decision=evaluate_admission(profile,WORKER)
        self.assertFalse(decision["admitted"])
        self.assertEqual(decision["reasons"],["PROFILE_NOT_ADMISSION_READY","VRAM_REQUIREMENT_UNMEASURED","VRAM_REQUIREMENT_MISSING"])

    def test_runtime_and_worker_advance_without_claiming_formal_smoke(self):
        qual=LIVE_RUNTIME["flux2_qualification"]
        self.assertEqual(qual["status"],"PASS_512_FULL_GPU")
        self.assertEqual(qual["peak_vram_mib"],16577.0)
        self.assertTrue(qual["formal_1024_smoke_pending"])
        worker=WORKER["qualified_models"]["flux2-klein-4b"]
        self.assertEqual(worker["status"],"PASS_512_QUALIFICATION")
        self.assertTrue(worker["formal_1024_smoke_pending"])
        self.assertEqual(WORKER["model_profile_measurements_status"],"FLUX2_512_MEASURED_1024_PENDING")

    def test_cost_ledger_tracks_bootstrap_plus_qualification_under_cap(self):
        by_id={row["cost_id"]:row for row in LEDGER["entries"]}
        self.assertEqual(set(by_id),{"runpod-a40-bootstrap-estimate-20260925","flux2-castjob_d3ec86da4ca6b1fc-pass"})
        self.assertAlmostEqual(sum(float(row["amount_usd"]) for row in LEDGER["entries"]),0.11165,places=6)
        self.assertAlmostEqual(by_id["flux2-castjob_d3ec86da4ca6b1fc-pass"]["amount_usd"],0.00138,places=6)
        self.assertTrue(budget_decision(LEDGER,budget_usd=60.0,proposed_charge_usd=59.8)["allowed"])
        self.assertFalse(budget_decision(LEDGER,budget_usd=60.0,proposed_charge_usd=59.9)["allowed"])


if __name__=="__main__":
    unittest.main()
