import csv,hashlib,json,tempfile,unittest
from io import StringIO
from pathlib import Path
from film.launch_gate import LaunchGateError, digest, make_rate_snapshot, validate_launch_authorization
from film.synthetic_fixtures import build_synthetic_casting_outputs
from film.casting_ingest import ingest_casting_outputs
from film.blind_scoring import ScoreSchema, parse_score_csv, validate_complete_scores, unblind_and_rank
from film.decision_templates import get_template, import_cost_rows
from film.decision_ledger import aggregate_benchmark_records

ROOT=Path(__file__).resolve().parents[2]
JOBS=json.loads((ROOT/"projects/slice01/casting/generation/casting_jobs.json").read_text(encoding="utf-8"))["jobs"]
CONTRACT=json.loads((ROOT/"projects/slice01/casting/reference_contract.json").read_text(encoding="utf-8"))
PROPOSAL=json.loads((ROOT/"model-evaluations/slice01/GPU_RENTAL_PROPOSAL_2026-09-24.json").read_text(encoding="utf-8"))

class Batch008Tests(unittest.TestCase):
    def test_placeholder_authorization_fails_closed(self):
        rates=json.loads((ROOT/"model-evaluations/slice01/rate_snapshot_20260925.json").read_text(encoding="utf-8"))
        receipt=json.loads((ROOT/"model-evaluations/slice01/launch_authorization.placeholder.json").read_text(encoding="utf-8"))
        with self.assertRaisesRegex(LaunchGateError,"not explicitly authorized"):
            validate_launch_authorization(receipt,proposal_digest=digest(PROPOSAL),rate_snapshot=rates,requested_gpu="RTX 5090",requested_max_usd=60)

    def test_valid_synthetic_authorization_is_hash_bound_and_bounded(self):
        rates=make_rate_snapshot("RunPod",{"RTX 5090":0.99},"2026-09-25","https://www.runpod.io/pricing")
        body={"schema_version":1,"authorization_id":"test-auth","status":"AUTHORIZED","authorized_by":"synthetic-test","authorized_at":"2026-09-25T00:00:00Z","expires_at":"2026-09-26T00:00:00Z","proposal_digest":digest(PROPOSAL),"rate_snapshot_digest":rates["snapshot_digest"],"provider":"RunPod","allowed_gpus":["RTX 5090"],"max_total_usd":60.0,"scope":"SYNTHETIC_TEST_ONLY"}
        receipt={**body,"receipt_digest":digest(body)}
        result=validate_launch_authorization(receipt,proposal_digest=digest(PROPOSAL),rate_snapshot=rates,requested_gpu="RTX 5090",requested_max_usd=50)
        self.assertTrue(result["launch_permitted"])
        with self.assertRaisesRegex(LaunchGateError,"exceeds"):
            validate_launch_authorization(receipt,proposal_digest=digest(PROPOSAL),rate_snapshot=rates,requested_gpu="RTX 5090",requested_max_usd=61)

    def test_synthetic_casting_fixture_end_to_end_is_not_production_acceptance(self):
        with tempfile.TemporaryDirectory() as td:
            outputs=build_synthetic_casting_outputs(JOBS,Path(td))
            self.assertEqual(len(outputs),32)
            self.assertTrue(all(row["fixture"] for row in outputs))
            updated,index,public=ingest_casting_outputs(CONTRACT,JOBS,outputs)
            self.assertEqual(updated["status"],"REFERENCES_GENERATED_AWAITING_SCORE")
            self.assertEqual(index["status"],"COMPLETE")
            self.assertEqual(len(index["assets"]),32)
            self.assertTrue(all("SYNTHETIC_PPM" in row["fixture_kind"] for row in outputs))
            schema=ScoreSchema(criteria=("identity_match","within_character_consistency","between_character_separation","style_quality","anatomy_artifact_free","overall"))
            private=json.loads((ROOT/"projects/slice01/casting/generation/blind_map_private.json").read_text(encoding="utf-8"))["mapping"]
            out=StringIO(); w=csv.writer(out,lineterminator="\n"); w.writerow(["blind_id",*schema.criteria,"failure_tags","notes"])
            for item in public["items"]: w.writerow([item["blind_id"],4,4,4,4,4,4,"","SYNTHETIC_FIXTURE"])
            scores=validate_complete_scores(public["items"],parse_score_csv(out.getvalue()),schema)
            ranking=unblind_and_rank(scores,private,group_fields=("model_id","style"))
            self.assertEqual(len(ranking),4)
            self.assertTrue(all(row["overall"]==4.0 for row in ranking))
            self.assertTrue(all(slot["asset_id"] is None for char in updated["characters"].values() for st in char["styles"].values() for slot in st["slots"]))

    def test_decision_template_import_incomplete_does_not_select(self):
        template=get_template("image_casting")
        rows=import_cost_rows([{"run_id":"r","job_id":"j","model_id":"z-image","shot_id":"s1","status":"PASS","elapsed_sec":2,"gpu_peak_memory_mb":1000,"cost_usd":0.01,"quality_overall":4.2,"usable":True}])
        report=aggregate_benchmark_records(rows,expected_models=set(template["expected_models"]),expected_shots={"s1"})
        self.assertEqual(report["status"],"INSUFFICIENT_EVIDENCE")
        self.assertFalse(report["selection_authorized"])
        self.assertIsNone(report["selected_winner"])

    def test_rate_snapshot_exact_current_baseline(self):
        snap=json.loads((ROOT/"model-evaluations/slice01/rate_snapshot_20260925.json").read_text(encoding="utf-8"))
        self.assertEqual(snap["provider"],"RunPod")
        self.assertEqual(snap["rates_usd_per_hour"]["RTX 5090"],0.99)
        self.assertEqual(snap["rates_usd_per_hour"]["RTX Pro 6000"],2.09)
        self.assertEqual(len(snap["snapshot_digest"]),64)

if __name__=="__main__": unittest.main()
