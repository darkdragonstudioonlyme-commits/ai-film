import json
from pathlib import Path
import unittest

from film.adapters import BACKENDS

ROOT=Path(__file__).resolve().parents[2]


class Batch004ContractTests(unittest.TestCase):
    def test_gpu_runtime_is_pinned_but_non_executing(self):
        runtime=json.loads((ROOT/"model-evaluations/slice01/gpu-worker/runtime_lock.json").read_text(encoding="utf-8"))
        self.assertEqual(runtime["snapshot_date"],"2026-09-25")
        self.assertEqual(runtime["status"],"PINNED_BASE_DRY_RUN_ONLY")
        self.assertFalse(runtime["execution_ready"])
        self.assertEqual(runtime["packages"]["torch"],"2.14.0")
        self.assertEqual(runtime["packages"]["diffusers"],"0.40.0")
        self.assertTrue(all("tbd" not in value.lower() for value in runtime["packages"].values()))
        plan=json.loads((ROOT/"run-evidence/GPU_WORKER_DRYRUN_20260925.json").read_text(encoding="utf-8"))
        self.assertEqual(plan["mode"],"DRY_RUN")
        self.assertFalse(plan["execution_ready"])

    def test_backend_coverage_matches_enabled_visual_candidates(self):
        matrix=json.loads((ROOT/"model-evaluations/slice01/model_matrix.json").read_text(encoding="utf-8"))
        expected={
            m["model_id"] for m in matrix["models"]
            if m.get("enabled") and m.get("stage") in {"image","video"}
        }
        self.assertEqual(set(BACKENDS),expected)

    def test_full_previs_audio_evidence(self):
        evidence=json.loads((ROOT/"run-evidence/PREVIS_AUDIO_20260925.json").read_text(encoding="utf-8"))
        self.assertEqual(evidence["status"],"PASS")
        self.assertEqual(set(evidence["languages"]),{"en","vi"})
        self.assertEqual(len(evidence["clips"]),8)
        self.assertTrue(all(row["fits_cue_budget"] for row in evidence["clips"]))
        self.assertEqual(evidence["voice_source"],"built_in_presets_no_cloning")
        for language in ("en","vi"):
            track=evidence["tracks"][language]
            self.assertEqual(track["duration_sec"],75.0)
            self.assertEqual(len(track["sha256"]),64)
            self.assertEqual(len(track["placements"]),4)

    def test_previs_animatics_bind_exact_audio_tracks(self):
        audio=json.loads((ROOT/"run-evidence/PREVIS_AUDIO_20260925.json").read_text(encoding="utf-8"))
        for language in ("en","vi"):
            evidence=json.loads((ROOT/f"run-evidence/PREVIS_ANIMATIC_{language.upper()}_20260925.json").read_text(encoding="utf-8"))
            self.assertEqual(evidence["status"],"PASS")
            self.assertEqual(evidence["audio_source"]["sha256"],audio["tracks"][language]["sha256"])
            self.assertEqual({row["aspect"] for row in evidence["outputs"]},{"9x16","16x9"})
            for row in evidence["outputs"]:
                self.assertEqual(row["probe"]["duration_sec"],75.0)
                self.assertTrue(row["probe"]["has_audio"])


if __name__=="__main__":
    unittest.main()
