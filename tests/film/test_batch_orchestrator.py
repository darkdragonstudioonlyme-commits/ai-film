import json,tempfile,unittest
from pathlib import Path
from film.batch_orchestrator import BatchOrchestratorError,build_argv,plan_batch,validate_config
ROOT=Path(__file__).resolve().parents[2]
CFG=json.loads((ROOT/"model-evaluations/slice01/batches/voxcpm2_formal_12_20260926.json").read_text())
VIDEO_CFG=json.loads((ROOT/"model-evaluations/slice01/batches/wan22_ti2v_smoke_20260926.json").read_text())

class BatchOrchestratorTests(unittest.TestCase):
    def test_voice_batch_binds_12_existing_adapter_jobs(self):
        jobs=validate_config(CFG)
        self.assertEqual(len(jobs),12)
        self.assertEqual({j["adapter"] for j in jobs},{"voxcpm2-live"})
        self.assertEqual(len({j["work_id"] for j in jobs}),12)
        self.assertTrue(all(j["skip_if_pass"] for j in jobs))

    def test_argv_uses_adapter_not_shell_string(self):
        argv=build_argv(CFG["jobs"][0],root=ROOT,execute=True)
        self.assertEqual(argv[1],str(ROOT/"tools/run_voxcpm2_live.py"))
        self.assertIn("--request-id",argv)
        self.assertIn("--execute",argv)
        self.assertNotIn("sh -c"," ".join(argv))

    def test_video_smoke_uses_wan_adapter_and_explicit_runtime_paths(self):
        jobs=validate_config(VIDEO_CFG)
        self.assertEqual(len(jobs),1)
        self.assertEqual(jobs[0]["adapter"],"wan22-ti2v-live")
        argv=build_argv(jobs[0],root=ROOT,execute=True)
        self.assertEqual(argv[1],str(ROOT/"tools/run_wan22_ti2v_live.py"))
        self.assertIn("--smoke-id",argv)
        self.assertIn("--wan-repo-dir",argv)
        self.assertIn("--reference-image",argv)
        self.assertIn("--execute",argv)

    def test_existing_pass_receipt_is_idempotently_skipped(self):
        with tempfile.TemporaryDirectory() as td:
            receipt=Path(td)/"receipt.json"; receipt.write_text('{"status":"PASS_RUNTIME"}')
            cfg={"schema_version":1,"batch_id":"t","jobs":[{
                "job_id":"j","adapter":"voxcpm2-live","work_id":"r",
                "receipt_path":str(receipt),"model_dir":"/m","skip_if_pass":True}]}
            plan=plan_batch(cfg,root=ROOT)
            self.assertEqual(plan["jobs"][0]["action"],"SKIP_EXISTING_PASS")
            self.assertFalse(plan["new_resource_creation_authorized"])
            self.assertFalse(plan["publish_authority"])

    def test_unknown_adapter_fails_closed(self):
        cfg={"schema_version":1,"batch_id":"t","jobs":[{
            "job_id":"j","adapter":"unknown","work_id":"x","receipt_path":"/tmp/x"}]}
        with self.assertRaisesRegex(BatchOrchestratorError,"unknown adapter"):
            validate_config(cfg)

if __name__=="__main__": unittest.main()