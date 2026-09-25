import copy,json,os,tempfile,unittest
from pathlib import Path

from film.spec_transport import SpecTransportError,canonical_digest,export_spec_bundle,import_spec_bundle,verify_spec_bundle
from film.schema_compat import SchemaCompatibilityError,apply_upgrade_plan,plan_schema_compatibility
from film.stage_readiness import ReadinessError,SLICE01_STAGE_DAG,evaluate_stage_readiness

ROOT=Path(__file__).resolve().parents[2]
PACKAGE=json.loads((ROOT/"projects/slice01/production_spec_package.json").read_text(encoding="utf-8"))
SCHEMA_REPORT=json.loads((ROOT/"projects/slice01/schema_compatibility.json").read_text(encoding="utf-8"))
READINESS=json.loads((ROOT/"projects/slice01/readiness/stage_readiness.json").read_text(encoding="utf-8"))

class SpecTransportTests(unittest.TestCase):
    def test_export_verify_import_round_trip(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            bundle=root/"bundle"
            dest=root/"imported"
            manifest=export_spec_bundle(ROOT,PACKAGE,bundle)
            self.assertEqual(manifest["entry_count"],15)
            self.assertEqual(verify_spec_bundle(bundle)["status"],"PASS")
            result=import_spec_bundle(bundle,dest)
            self.assertEqual(result["entry_count"],15)
            self.assertFalse(result["execution_authority"])
            self.assertFalse(result["publish_authority"])
            for entry in PACKAGE["entries"]:
                self.assertTrue((dest/entry["path"]).is_file())
            self.assertFalse((dest/"projects/slice01/runtime").exists())

    def test_tampered_payload_fails_before_import(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); bundle=root/"bundle"; dest=root/"dest"
            export_spec_bundle(ROOT,PACKAGE,bundle)
            target=bundle/"payload"/PACKAGE["entries"][0]["path"]
            target.write_text("tampered",encoding="utf-8")
            self.assertEqual(verify_spec_bundle(bundle)["status"],"FAIL")
            with self.assertRaisesRegex(SpecTransportError,"verification failed"):
                import_spec_bundle(bundle,dest)
            self.assertFalse(dest.exists())

    def test_extra_file_and_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); bundle=root/"bundle"
            export_spec_bundle(ROOT,PACKAGE,bundle)
            (bundle/"payload/extra.txt").write_text("x")
            self.assertEqual(verify_spec_bundle(bundle)["status"],"FAIL")
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); bundle=root/"bundle"
            export_spec_bundle(ROOT,PACKAGE,bundle)
            link=bundle/"payload/link.json"
            os.symlink(bundle/"BUNDLE_MANIFEST.json",link)
            with self.assertRaisesRegex(SpecTransportError,"symlink"):
                verify_spec_bundle(bundle)

    def test_rebuilt_manifest_cannot_smuggle_runtime_path(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); bundle=root/"bundle"
            export_spec_bundle(ROOT,PACKAGE,bundle)
            manifest=json.loads((bundle/"BUNDLE_MANIFEST.json").read_text())
            bad={"path":"projects/slice01/runtime/cost.json","sha256":"a"*64,"bytes":1}
            manifest["entries"].append(bad); manifest["entry_count"]+=1
            body={k:v for k,v in manifest.items() if k!="bundle_digest"}
            manifest["bundle_digest"]=canonical_digest(body)
            (bundle/"BUNDLE_MANIFEST.json").write_text(json.dumps(manifest))
            with self.assertRaisesRegex(SpecTransportError,"forbidden bundle path"):
                verify_spec_bundle(bundle)

class SchemaCompatibilityTests(unittest.TestCase):
    def test_current_report_has_exact_four_legacy_upgrades(self):
        self.assertEqual(SCHEMA_REPORT["status"],"UPGRADE_REQUIRED")
        self.assertEqual(SCHEMA_REPORT["unsupported"],[])
        self.assertFalse(SCHEMA_REPORT["mutations_applied"])
        self.assertEqual(set(SCHEMA_REPORT["upgrade_required"]),{
            "projects/slice01/project.json",
            "projects/slice01/casting.json",
            "projects/slice01/continuity.json",
            "projects/slice01/shots/benchmark_shots.json",
        })

    def test_upgrade_is_dry_run_by_default(self):
        with self.assertRaisesRegex(SchemaCompatibilityError,"dry-run"):
            apply_upgrade_plan({"project_id":"x"},document_type="project",from_version=0)

    def test_authorized_legacy_upgrade_shape(self):
        upgraded=apply_upgrade_plan({"project_id":"x"},document_type="project",from_version=0,authorized=True)
        self.assertEqual(upgraded["schema_version"],1)
        shots=apply_upgrade_plan([{"shot_id":"s1"}],document_type="shots",from_version=0,authorized=True)
        self.assertEqual(shots,{"schema_version":1,"shots":[{"shot_id":"s1"}]})

    def test_future_schema_is_unsupported(self):
        report=plan_schema_compatibility({"x":{"document_type":"project","value":{"schema_version":2}}})
        self.assertEqual(report["status"],"UNSUPPORTED")
        self.assertEqual(report["unsupported"],["x"])
        self.assertFalse(report["mutations_applied"])

class StageReadinessTests(unittest.TestCase):
    def test_current_readiness_has_authorized_casting_and_voice_frontier(self):
        self.assertEqual(READINESS["status"],"HAS_RUNNABLE_STAGE")
        self.assertEqual(set(READINESS["ready_stages"]),{"casting_reference_generation","voice_eval"})
        self.assertEqual(READINESS["blocking_frontier"],[])
        self.assertTrue(READINESS["evidence"]["paid_gpu_authorized"])
        self.assertFalse(READINESS["execution_permitted"])
        by={row["stage_id"]:row for row in READINESS["stages"]}
        for stage_id in ("casting_reference_generation","voice_eval"):
            self.assertEqual(by[stage_id]["status"],"READY")
            self.assertEqual(by[stage_id]["blockers"],[])
            self.assertFalse(by[stage_id]["execution_permitted"])

    def test_removing_paid_authority_blocks_frontier_again(self):
        evidence=copy.deepcopy(READINESS["evidence"])
        evidence["paid_gpu_authorized"]=False
        report=evaluate_stage_readiness(SLICE01_STAGE_DAG,evidence)
        self.assertEqual(report["status"],"NO_RUNNABLE_STAGE")
        self.assertEqual(report["ready_stages"],[])
        frontier={row["stage_id"]:row["blockers"] for row in report["blocking_frontier"]}
        self.assertEqual(set(frontier),{"casting_reference_generation","voice_eval"})
        self.assertEqual(frontier["casting_reference_generation"],["missing-evidence:paid_gpu_authorized"])
        self.assertEqual(frontier["voice_eval"],["missing-evidence:paid_gpu_authorized"])

    def test_missing_source_blocks_downstream(self):
        evidence=copy.deepcopy(READINESS["evidence"])
        evidence["source_packet_ready"]=False
        report=evaluate_stage_readiness(SLICE01_STAGE_DAG,evidence)
        by={row["stage_id"]:row for row in report["stages"]}
        self.assertEqual(by["source_ingestion"]["status"],"READY")
        self.assertEqual(by["screenplay_localization"]["status"],"BLOCKED")
        self.assertIn("upstream-not-complete:source_ingestion",by["screenplay_localization"]["blockers"])

    def test_stage_dependency_cycle_rejected(self):
        bad=[{"stage_id":"a","depends_on":["b"]},{"stage_id":"b","depends_on":["a"]}]
        with self.assertRaisesRegex(ReadinessError,"cycle"):
            evaluate_stage_readiness(bad,{})

if __name__=="__main__": unittest.main()
