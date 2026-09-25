import json
from pathlib import Path
import unittest

from film.admission import evaluate_admission
from film.cost_ledger import budget_decision
from film.flux2_klein_live import REQUIRED_MODEL_FILES

ROOT=Path(__file__).resolve().parents[2]
EVIDENCE=json.loads((ROOT/"run-evidence/FLUX2_KLEIN_A40_FORMAL_SMOKE_20260925.json").read_text(encoding="utf-8"))
RESOURCES=json.loads((ROOT/"model-evaluations/slice01/resource_profiles.json").read_text(encoding="utf-8"))
WORKER=json.loads((ROOT/"projects/slice01/runtime/worker_runpod_a40.json").read_text(encoding="utf-8"))
LIVE_RUNTIME=json.loads((ROOT/"model-evaluations/slice01/gpu-worker/runtime_lock.runpod_a40.json").read_text(encoding="utf-8"))
LEDGER=json.loads((ROOT/"projects/slice01/runtime/cost_ledger.json").read_text(encoding="utf-8"))
MATRIX=json.loads((ROOT/"model-evaluations/slice01/model_matrix.json").read_text(encoding="utf-8"))


class Flux2FormalSmokeEvidenceTests(unittest.TestCase):
    def test_four_output_population_is_exact_hash_bound_and_non_accepting(self):
        self.assertEqual(EVIDENCE["status"],"PASS_FORMAL_1024_FOUR_JOB_SMOKE")
        self.assertEqual(EVIDENCE["planned_jobs"],4)
        self.assertEqual(EVIDENCE["passed_jobs"],4)
        self.assertEqual(EVIDENCE["failed_jobs"],0)
        self.assertEqual(len(EVIDENCE["outputs"]),4)
        self.assertEqual({(row["character_id"],row["style"],row["slot"]) for row in EVIDENCE["outputs"]},{
            ("an","photoreal","face_front"),("an","stylized_3d","face_front"),
            ("linh","photoreal","face_front"),("linh","stylized_3d","face_front"),
        })
        self.assertTrue(all(row["width"]==1024 and row["height"]==1024 and len(row["asset_sha256"])==64 and len(row["manifest_sha256"])==64 for row in EVIDENCE["outputs"]))
        self.assertFalse(EVIDENCE["production_acceptance"])
        self.assertFalse(EVIDENCE["selection_authorized"])
        self.assertFalse(EVIDENCE["publish_authority"])

    def test_validator_gap_is_closed_with_all_18_diffusers_files(self):
        self.assertEqual(len(REQUIRED_MODEL_FILES),18)
        self.assertEqual(EVIDENCE["raw_model_snapshot_shape"]["status"],"UNDERCOUNTED_BY_PRE_RUN_VALIDATOR")
        post=EVIDENCE["post_run_model_dir_validation"]
        self.assertEqual(post["status"],"PASS_AFTER_VALIDATOR_FIX")
        self.assertTrue(post["validator_gap_closed"])
        self.assertEqual(post["required_file_count"],18)
        self.assertEqual(post["required_bytes"],15980131745)
        self.assertAlmostEqual(post["required_gib"],14.882657,places=6)

    def test_formal_smoke_promotes_only_resource_admission(self):
        profile=next(row for row in RESOURCES["profiles"] if row["model_id"]=="flux2-klein-4b")
        self.assertEqual(profile["vram_status"],"MEASURED")
        self.assertTrue(profile["admission_ready"])
        self.assertEqual(profile["required_vram_gb"],20.0)
        self.assertEqual(profile["vram_reserve_gb"],4.0)
        decision=evaluate_admission(profile,WORKER)
        self.assertTrue(decision["admitted"])
        self.assertEqual(decision["reasons"],[])
        matrix_model=next(row for row in MATRIX["models"] if row["model_id"]=="flux2-klein-4b")
        self.assertFalse(matrix_model["execution_ready"])

    def test_vram_and_cost_measurements_match_formal_run(self):
        m=EVIDENCE["measurements"]
        self.assertEqual(m["max_torch_peak_memory_mb"],20080.0)
        self.assertEqual(m["max_nvidia_smi_memory_mib"],20415)
        self.assertAlmostEqual(m["mean_job_elapsed_sec"],2.366221,places=6)
        self.assertAlmostEqual(m["median_job_elapsed_sec"],2.239497,places=6)
        self.assertAlmostEqual(m["estimated_compute_cost_usd"],0.0021,places=6)
        self.assertEqual(EVIDENCE["vram_policy"]["admission_threshold_gb"],24.0)

    def test_cost_runtime_worker_state_advance_without_winner_selection(self):
        by_id={row["cost_id"]:row for row in LEDGER["entries"]}
        self.assertEqual(set(by_id),{"runpod-a40-bootstrap-estimate-20260925","flux2-castjob_d3ec86da4ca6b1fc-pass","flux2-formal-smoke-20260925"})
        self.assertAlmostEqual(sum(float(row["amount_usd"]) for row in LEDGER["entries"]),0.11375,places=6)
        self.assertTrue(budget_decision(LEDGER,budget_usd=60.0,proposed_charge_usd=59.88)["allowed"])
        self.assertFalse(budget_decision(LEDGER,budget_usd=60.0,proposed_charge_usd=59.89)["allowed"])
        self.assertEqual(LIVE_RUNTIME["flux2_qualification"]["status"],"PASS_FORMAL_1024_FOUR_JOB")
        self.assertTrue(LIVE_RUNTIME["flux2_qualification"]["admission_ready"])
        self.assertEqual(WORKER["qualified_models"]["flux2-klein-4b"]["status"],"PASS_FORMAL_1024_FOUR_JOB")
        self.assertTrue(WORKER["qualified_models"]["flux2-klein-4b"]["admission_ready"])


if __name__=="__main__":
    unittest.main()
