import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from film.voxcpm2_live import (
    VoxCPM2QualificationError,
    build_cost_entry,
    build_output_manifest,
    prepare_voxcpm2_qualification,
    validate_model_dir,
)

ROOT=Path(__file__).resolve().parents[2]
MATRIX=json.loads((ROOT/"model-evaluations/slice01/model_matrix.json").read_text(encoding="utf-8"))
CONFIG=json.loads((ROOT/"model-evaluations/slice01/voice/voxcpm2_eval_config.json").read_text(encoding="utf-8"))
REQUESTS=json.loads((ROOT/"model-evaluations/slice01/voice/requests/requests.json").read_text(encoding="utf-8"))["requests"]
LIVE=json.loads((ROOT/"model-evaluations/slice01/gpu-worker/runtime_lock.runpod_a40.json").read_text(encoding="utf-8"))
PROPOSAL=json.loads((ROOT/"model-evaluations/slice01/GPU_RENTAL_PROPOSAL_2026-09-24.json").read_text(encoding="utf-8"))
PLAN=json.loads((ROOT/"model-evaluations/slice01/GPU_RENTAL_EXECUTION_PLAN_20260925.json").read_text(encoding="utf-8"))
RATES=json.loads((ROOT/"model-evaluations/slice01/rate_snapshot_20260925.json").read_text(encoding="utf-8"))
AUTH=json.loads((ROOT/"model-evaluations/slice01/launch_authorization.active.json").read_text(encoding="utf-8"))
POLICY=json.loads((ROOT/"projects/slice01/runtime/cost_policy.json").read_text(encoding="utf-8"))
LEDGER=json.loads((ROOT/"projects/slice01/runtime/cost_ledger.json").read_text(encoding="utf-8"))

def prepare(request=None,max_runtime_sec=900.0):
    return prepare_voxcpm2_qualification(
        request=request or REQUESTS[0],
        matrix=MATRIX,
        config=CONFIG,
        live_runtime=LIVE,
        proposal=PROPOSAL,
        execution_plan=PLAN,
        rate_snapshot=RATES,
        authorization=AUTH,
        cost_policy=POLICY,
        cost_ledger=LEDGER,
        max_runtime_sec=max_runtime_sec,
    )

class VoxCPM2LiveRunnerTests(unittest.TestCase):
    def test_plan_binds_exact_request_and_paid_authority_without_execution(self):
        plan=prepare()
        self.assertEqual(plan["status"],"QUALIFICATION_AUTHORIZED_NOT_EXECUTED")
        self.assertEqual(plan["model_id"],"voxcpm2")
        self.assertEqual(plan["model_revision"],"32279effe8c19989596f05d353d1447f51d9e915")
        self.assertEqual(plan["package"],"voxcpm==2.0.3")
        self.assertEqual(plan["gpu"],"NVIDIA A40")
        self.assertEqual(plan["reference_audio"],None)
        self.assertFalse(plan["new_resource_creation_authorized"])
        self.assertFalse(plan["publish_authority"])
        self.assertLess(plan["proposed_max_cost_usd"],1.0)
        self.assertGreater(plan["budget_headroom_after_max_usd"],50.0)

    def test_reference_audio_tamper_rejected(self):
        request=copy.deepcopy(REQUESTS[0])
        request["reference_audio"]="forbidden.wav"
        with self.assertRaisesRegex(VoxCPM2QualificationError,"reference audio"):
            prepare(request)

    def test_cloning_gate_tamper_rejected(self):
        config=copy.deepcopy(CONFIG)
        config["voice_cloning_allowed"]=True
        with self.assertRaisesRegex(VoxCPM2QualificationError,"voice cloning"):
            prepare_voxcpm2_qualification(
                request=REQUESTS[0],matrix=MATRIX,config=config,live_runtime=LIVE,
                proposal=PROPOSAL,execution_plan=PLAN,rate_snapshot=RATES,
                authorization=AUTH,cost_policy=POLICY,cost_ledger=LEDGER,
            )

    def test_model_revision_or_package_drift_rejected(self):
        request=copy.deepcopy(REQUESTS[0])
        request["model"]["revision"]="0"*40
        with self.assertRaisesRegex(VoxCPM2QualificationError,"model identity drift"):
            prepare(request)
        request=copy.deepcopy(REQUESTS[0])
        request["model"]["package"]="voxcpm==999"
        with self.assertRaisesRegex(VoxCPM2QualificationError,"model identity drift"):
            prepare(request)

    def test_model_dir_requires_exact_minimum_files(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            required=[
                "config.json","model.safetensors","audiovae.pth","tokenizer.json",
                "tokenizer_config.json","tokenization_voxcpm2.py","special_tokens_map.json",
            ]
            for rel in required:
                p=root/rel; p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes((rel+"\n").encode())
            shape=validate_model_dir(root)
            self.assertEqual(shape["required_file_count"],7)
            self.assertGreater(shape["required_bytes"],0)
            (root/"model.safetensors").unlink()
            with self.assertRaisesRegex(VoxCPM2QualificationError,"missing required files"):
                validate_model_dir(root)

    def test_output_manifest_reports_cue_fit_without_promoting_quality(self):
        request=REQUESTS[0]
        with tempfile.TemporaryDirectory() as td:
            wav=Path(td)/"x.wav"
            wav.write_bytes(b"RIFF"+b"0"*100)
            manifest=build_output_manifest(
                request=request,
                audio_path=wav,
                duration_sec=2.0,
                gpu_peak_memory_mb=1234,
                runtime={"package":"voxcpm==2.0.3"},
            )
            self.assertTrue(manifest["cue_fit"])
            self.assertEqual(manifest["request_digest"],request["request_digest"])
            self.assertEqual(manifest["sample_rate_hz"],48000)

    def test_plan_only_cli_does_not_require_voxcpm_package(self):
        proc=subprocess.run(
            [
                sys.executable,str(ROOT/"tools/run_voxcpm2_live.py"),
                "--request-id",REQUESTS[0]["request_id"],
                "--max-runtime-sec","900",
            ],
            cwd=ROOT,text=True,capture_output=True,check=False,
        )
        self.assertEqual(proc.returncode,0,proc.stderr)
        result=json.loads(proc.stdout)
        self.assertEqual(result["status"],"QUALIFICATION_AUTHORIZED_NOT_EXECUTED")
        self.assertEqual(result["request"]["request_id"],REQUESTS[0]["request_id"])


if __name__=="__main__":
    unittest.main()
