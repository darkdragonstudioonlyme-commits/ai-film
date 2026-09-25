import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from film.prelaunch import build_prelaunch_bundle

ROOT=Path(__file__).resolve().parents[2]


class Batch005ContractTests(unittest.TestCase):
    def test_prelaunch_bundle_matches_enabled_visual_models(self):
        matrix=json.loads((ROOT/"model-evaluations/slice01/model_matrix.json").read_text(encoding="utf-8"))
        expected={
            m["model_id"] for m in matrix["models"]
            if m.get("enabled") and m.get("stage") in {"image","video"}
        }
        bundle=build_prelaunch_bundle(ROOT)
        self.assertEqual(bundle["mode"],"PRELAUNCH_DRY_RUN_ONLY")
        self.assertFalse(bundle["execution_ready"])
        self.assertFalse(bundle["provider_resource_created"])
        self.assertEqual({m["model_id"] for m in bundle["models"]},expected)
        by_id={m["model_id"]:m for m in matrix["models"]}
        for row in bundle["models"]:
            model=by_id[row["model_id"]]
            self.assertEqual(row["source_revision"],model["source_revision"])
            self.assertFalse(row["execution_ready"])
            self.assertIn(model["source_revision"],row["install_plan"][0]["command"])
            self.assertFalse(row["runner_contract"]["paid_authority_inherited"])

    def test_prelaunch_cli_apply_is_disabled(self):
        proc=subprocess.run(
            [sys.executable,str(ROOT/"tools/build_gpu_prelaunch_bundle.py"),"--apply"],
            cwd=ROOT,text=True,capture_output=True,check=False,
        )
        self.assertNotEqual(proc.returncode,0)
        self.assertIn("intentionally disabled",proc.stderr)

    def test_casting_reference_contract_has_no_fake_assets(self):
        contract=json.loads((ROOT/"projects/slice01/casting/reference_contract.json").read_text(encoding="utf-8"))
        casting=json.loads((ROOT/"projects/slice01/casting.json").read_text(encoding="utf-8"))
        self.assertEqual(set(contract["characters"]),set(casting["characters"]))
        self.assertEqual(contract["status"],"CONTRACT_READY_REFERENCES_NOT_GENERATED")
        self.assertEqual(contract["generated_reference_paths"],[])
        self.assertEqual(len(contract["reference_slots"]),4)
        for char in contract["characters"].values():
            for style in contract["styles"]:
                slots=char["styles"][style]["slots"]
                self.assertEqual(len(slots),4)
                self.assertTrue(all(row["asset_id"] is None and row["manifest_sha256"] is None for row in slots))
        self.assertIn("CALIBRATE",contract["embedding_policy"]["absolute_threshold"])

    def test_casting_eval_packet_is_opaque_and_complete(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)
            subprocess.run(
                [sys.executable,str(ROOT/"tools/build_casting_eval_packet.py"),"--out-dir",str(out)],
                cwd=ROOT,check=True,stdout=subprocess.DEVNULL,
            )
            public=json.loads((out/"blind_items.json").read_text())
            private=json.loads((out/"blind_map_private.json").read_text())
            self.assertEqual(len(public["items"]),16)
            self.assertEqual(len(private["mapping"]),16)
            self.assertTrue(all("character_id" not in row for row in public["items"]))
            self.assertEqual({row["character_id"] for row in private["mapping"]},{"an","linh"})

    def test_voxcpm2_packet_is_multilingual_voice_design_only(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)
            subprocess.run(
                [sys.executable,str(ROOT/"tools/build_voxcpm2_eval_packet.py"),"--out-dir",str(out)],
                cwd=ROOT,check=True,stdout=subprocess.DEVNULL,
            )
            packet=json.loads((out/"eval_packet.json").read_text(encoding="utf-8"))
            private=json.loads((out/"blind_map_private.json").read_text(encoding="utf-8"))
            self.assertEqual(packet["model"]["revision"],"32279effe8c19989596f05d353d1447f51d9e915")
            self.assertEqual(packet["model"]["sample_rate_hz"],48000)
            self.assertEqual(packet["mode"],"voice_design")
            self.assertEqual(len(packet["samples"]),12)
            self.assertEqual({row["language"] for row in packet["samples"]},{"en","zh-CN","vi"})
            self.assertTrue(all(row["reference_audio"] is None and row["mode"]=="voice_design" for row in packet["samples"]))
            self.assertEqual(len({row["voice_group"] for row in packet["samples"]}),2)
            self.assertEqual({row["character_id"] for row in private["mapping"]},{"an","linh"})
            groups={}
            for row in packet["samples"]:
                groups.setdefault(row["voice_group"],set()).add(row["seed"])
            self.assertTrue(all(len(seeds)==1 for seeds in groups.values()))


if __name__=="__main__":
    unittest.main()
