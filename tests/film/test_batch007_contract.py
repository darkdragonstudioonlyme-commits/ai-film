import copy, json, tempfile, unittest
from pathlib import Path
from film.image_runner import RunnerContractError, compile_image_worker_request, validate_image_output_manifest
from film.casting_ingest import CastingIngestError, ingest_casting_outputs
from film.decision_ledger import DecisionLedgerError, aggregate_benchmark_records

ROOT=Path(__file__).resolve().parents[2]
MATRIX=json.loads((ROOT/"model-evaluations/slice01/model_matrix.json").read_text(encoding="utf-8"))
RUNTIME=json.loads((ROOT/"model-evaluations/slice01/gpu-worker/runtime_lock.json").read_text(encoding="utf-8"))
JOBS=json.loads((ROOT/"projects/slice01/casting/generation/casting_jobs.json").read_text(encoding="utf-8"))["jobs"]
CONTRACT=json.loads((ROOT/"projects/slice01/casting/reference_contract.json").read_text(encoding="utf-8"))

class Batch007Tests(unittest.TestCase):
    def test_image_worker_request_is_deterministic_and_nonexecuting(self):
        a=compile_image_worker_request(JOBS[0],MATRIX,RUNTIME)
        b=compile_image_worker_request(JOBS[0],MATRIX,RUNTIME)
        self.assertEqual(a,b)
        self.assertFalse(a["execution_permitted"])
        self.assertFalse(a["provider_resource_created"])
        self.assertFalse(a["paid_authority_inherited"])
        self.assertEqual(len(a["request_digest"]),64)

    def test_image_output_manifest_must_bind_exact_request(self):
        req=compile_image_worker_request(JOBS[0],MATRIX,RUNTIME)
        m={
            "request_digest":req["request_digest"],"job_id":req["job_id"],"job_digest":req["job_digest"],
            "blind_id":req["blind_id"],"asset_id":"asset_1","asset_path":"outputs/a.png",
            "asset_sha256":"a"*64,"manifest_sha256":"b"*64,"model_id":req["model"]["model_id"],
            "model_revision":req["model"]["revision"],"seed":req["seed"],"elapsed_sec":2.0,"gpu_peak_memory_mb":20000,
        }
        self.assertEqual(validate_image_output_manifest(req,m)["asset_id"],"asset_1")
        bad=dict(m,job_digest="0"*64)
        with self.assertRaisesRegex(RunnerContractError,"job_digest"):
            validate_image_output_manifest(req,bad)

    def test_casting_ingest_never_selects_a_winner(self):
        job=JOBS[0]
        m={
            "job_id":job["job_id"],"job_digest":job["job_digest"],"blind_id":job["blind_id"],
            "asset_id":"asset_1","asset_path":"outputs/a.png","asset_sha256":"a"*64,"manifest_sha256":"b"*64,
            "model_id":job["model_id"],"model_revision":job["model_revision"],"seed":job["seed"],
        }
        updated,index,public=ingest_casting_outputs(CONTRACT,JOBS,[m])
        self.assertEqual(updated["status"],"PARTIAL_REFERENCES_GENERATED")
        self.assertEqual(len(index["assets"]),1)
        self.assertEqual(index["status"],"PARTIAL")
        self.assertEqual(sum(1 for x in public["items"] if x["asset_id"]),1)
        # original slot remains unselected until scoring/acceptance
        slot=updated["characters"][job["character_id"]]["styles"][job["style"]]["slots"]
        self.assertTrue(all(x["asset_id"] is None for x in slot))

    def test_casting_ingest_rejects_tampered_identity(self):
        job=JOBS[0]
        m={"job_id":job["job_id"],"job_digest":"0"*64,"blind_id":job["blind_id"],"asset_id":"x","asset_path":"a.png","asset_sha256":"a"*64,"manifest_sha256":"b"*64,"model_id":job["model_id"],"model_revision":job["model_revision"],"seed":job["seed"]}
        with self.assertRaisesRegex(CastingIngestError,"job_digest"):
            ingest_casting_outputs(CONTRACT,JOBS,[m])

    def test_decision_report_fails_closed_on_incomplete_evidence(self):
        records=[{"run_id":"r1","job_id":"j1","model_id":"z-image","shot_id":"s1","status":"PASS","cost_usd":0.1,"elapsed_sec":3.0,"gpu_peak_memory_mb":1000}]
        report=aggregate_benchmark_records(records,expected_models={"z-image","flux2-klein-4b"},expected_shots={"s1","s2"})
        self.assertEqual(report["status"],"INSUFFICIENT_EVIDENCE")
        self.assertEqual(report["evidence_order"],[])
        self.assertIsNone(report["selected_winner"])
        self.assertFalse(report["selection_authorized"])

    def test_decision_report_orders_complete_evidence_without_selecting(self):
        records=[
          {"run_id":"r1","job_id":"j1","model_id":"z-image","shot_id":"s1","status":"PASS","cost_usd":0.2,"elapsed_sec":4.0,"gpu_peak_memory_mb":1000,"quality_overall":4.5,"usable":True},
          {"run_id":"r1","job_id":"j2","model_id":"flux2-klein-4b","shot_id":"s1","status":"PASS","cost_usd":0.1,"elapsed_sec":3.0,"gpu_peak_memory_mb":900,"quality_overall":4.0,"usable":True},
        ]
        report=aggregate_benchmark_records(records,expected_models={"z-image","flux2-klein-4b"},expected_shots={"s1"})
        self.assertEqual(report["status"],"COMPLETE_COMPARISON")
        self.assertEqual(report["evidence_order"][0],"z-image")
        self.assertIsNone(report["selected_winner"])
        self.assertFalse(report["selection_authorized"])

    def test_duplicate_ledger_record_rejected(self):
        row={"run_id":"r1","job_id":"j1","model_id":"z-image","shot_id":"s1","status":"BLOCKED","cost_usd":0,"elapsed_sec":0}
        with self.assertRaisesRegex(DecisionLedgerError,"duplicate"):
            aggregate_benchmark_records([row,row])

if __name__=="__main__": unittest.main()
