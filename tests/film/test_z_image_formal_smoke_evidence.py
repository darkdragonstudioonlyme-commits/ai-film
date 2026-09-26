import json
from pathlib import Path
import unittest

from film.admission import evaluate_admission
from film.cost_ledger import budget_decision

ROOT=Path(__file__).resolve().parents[2]
EVIDENCE=json.loads((ROOT/"run-evidence/Z_IMAGE_A40_FORMAL_SMOKE_20260926.json").read_text(encoding="utf-8"))
RESOURCES=json.loads((ROOT/"model-evaluations/slice01/resource_profiles.json").read_text(encoding="utf-8"))
WORKER=json.loads((ROOT/"projects/slice01/runtime/worker_runpod_a40.json").read_text(encoding="utf-8"))
LIVE_RUNTIME=json.loads((ROOT/"model-evaluations/slice01/gpu-worker/runtime_lock.runpod_a40.json").read_text(encoding="utf-8"))
LEDGER=json.loads((ROOT/"projects/slice01/runtime/cost_ledger.json").read_text(encoding="utf-8"))
MATRIX=json.loads((ROOT/"model-evaluations/slice01/model_matrix.json").read_text(encoding="utf-8"))


class ZImageFormalSmokeEvidenceTests(unittest.TestCase):
    def test_four_output_population_is_exact_hash_bound_and_non_accepting(self):
        self.assertEqual(EVIDENCE["status"],"PASS_FORMAL_1024_FOUR_JOB_SMOKE")
        self.assertEqual(EVIDENCE["planned_jobs"],4)
        self.assertEqual(EVIDENCE["passed_jobs"],4)
        self.assertEqual(EVIDENCE["failed_jobs"],0)
        self.assertEqual(len(EVIDENCE["outputs"]),4)
        self.assertEqual(
            {(row["character_id"],row["style"],row["slot"]) for row in EVIDENCE["outputs"]},
            {
                ("an","photoreal","face_front"),
                ("an","stylized_3d","face_front"),
                ("linh","photoreal","face_front"),
                ("linh","stylized_3d","face_front"),
            },
        )
        self.assertTrue(all(row["width"]==1024 and row["height"]==1024 for row in EVIDENCE["outputs"]))
        self.assertTrue(all(len(row["asset_sha256"])==64 and len(row["manifest_sha256"])==64 for row in EVIDENCE["outputs"]))
        self.assertFalse(EVIDENCE["production_acceptance"])
        self.assertFalse(EVIDENCE["selection_authorized"])
        self.assertFalse(EVIDENCE["publish_authority"])

    def test_formal_smoke_promotes_only_resource_admission(self):
        profile=next(row for row in RESOURCES["profiles"] if row["model_id"]=="z-image")
        self.assertEqual(profile["vram_status"],"MEASURED")
        self.assertTrue(profile["admission_ready"])
        self.assertEqual(profile["required_vram_gb"],26.0)
        self.assertEqual(profile["vram_reserve_gb"],4.0)
        self.assertEqual(profile["throughput_status"],"MEASURED_1024_FORMAL_SMOKE")
        decision=evaluate_admission(profile,WORKER)
        self.assertTrue(decision["admitted"])
        self.assertEqual(decision["reasons"],[])
        model=next(row for row in MATRIX["models"] if row["model_id"]=="z-image")
        self.assertFalse(model["execution_ready"])

    def test_vram_throughput_cost_and_raw_evidence_match_run(self):
        m=EVIDENCE["measurements"]
        self.assertEqual(m["max_torch_peak_memory_mb"],25892.0)
        self.assertEqual(m["max_nvidia_smi_memory_mib"],26227)
        self.assertAlmostEqual(m["mean_job_elapsed_sec"],86.360403,places=6)
        self.assertAlmostEqual(m["median_job_elapsed_sec"],86.534926,places=6)
        self.assertAlmostEqual(m["elapsed_sec_total"],353.466833,places=6)
        self.assertAlmostEqual(m["estimated_compute_cost_usd"],0.048111,places=6)
        self.assertEqual(EVIDENCE["raw_evidence"]["sha256"],"ce43303ec34682f843b9b4e16ef39a68d40a51fd9e4ff04bd21fb0fbb2a9b942")
        self.assertEqual(EVIDENCE["model_snapshot_shape"]["required_file_count"],18)
        self.assertEqual(EVIDENCE["model_snapshot_shape"]["required_bytes"],20538488559)
        self.assertEqual(EVIDENCE["vram_policy"]["admission_threshold_gb"],30.0)

    def test_runtime_worker_state_is_complete_and_rerun_not_pending(self):
        zrt=LIVE_RUNTIME["z_image_qualification"]
        self.assertEqual(zrt["status"],"PASS_FORMAL_1024_FOUR_JOB")
        self.assertFalse(zrt["formal_1024_smoke_pending"])
        self.assertTrue(zrt["admission_ready"])
        self.assertEqual(zrt["required_vram_gb"],26.0)
        self.assertEqual(zrt["vram_reserve_gb"],4.0)
        zw=WORKER["qualified_models"]["z-image"]
        self.assertEqual(zw["status"],"PASS_FORMAL_1024_FOUR_JOB")
        self.assertFalse(zw["formal_1024_smoke_pending"])
        self.assertTrue(zw["admission_ready"])
        self.assertEqual(WORKER["model_profile_measurements_status"],"FLUX2_ZIMAGE_1024_VOXCPM2_12_WAN22_TI2V_SMOKE_READY")

    def test_cost_ledger_advances_without_winner_selection(self):
        by_id={row["cost_id"]:row for row in LEDGER["entries"]}
        self.assertIn("zimage-formal-smoke-20260926",by_id)
        self.assertAlmostEqual(by_id["zimage-formal-smoke-20260926"]["amount_usd"],0.048111,places=6)
        self.assertAlmostEqual(sum(float(row["amount_usd"]) for row in LEDGER["entries"]),0.455474,places=6)
        self.assertTrue(budget_decision(LEDGER,budget_usd=60.0,proposed_charge_usd=59.5445)["allowed"])
        self.assertFalse(budget_decision(LEDGER,budget_usd=60.0,proposed_charge_usd=59.5446)["allowed"])


if __name__=="__main__":
    unittest.main()