import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from film.casting_jobs import compile_casting_jobs
from film.project_scaffold import build_project_scaffold
from film.shot_compiler import compile_shot, compile_visual_prompt
from film.world_profile import (
    WorldProfileError,
    resolve_world_preset,
    validate_preset_catalog,
    validate_world_profile,
)

ROOT = Path(__file__).resolve().parents[2]
P = ROOT / "projects/slice01"
CATALOG = json.loads((ROOT / "production-profiles/world_profiles.json").read_text(encoding="utf-8"))
LEDGER = json.loads((P / "continuity.json").read_text(encoding="utf-8"))
CASTING = json.loads((P / "casting.json").read_text(encoding="utf-8"))
SHOTS = json.loads((P / "shots/benchmark_shots.json").read_text(encoding="utf-8"))
CONTRACT = json.loads((P / "casting/reference_contract.json").read_text(encoding="utf-8"))
MATRIX = json.loads((ROOT / "model-evaluations/slice01/model_matrix.json").read_text(encoding="utf-8"))
SOURCE = json.loads((P / "source/source_packet.json").read_text(encoding="utf-8"))


class WorldProfileTests(unittest.TestCase):
    def test_builtin_catalog_covers_historical_china_and_europe(self):
        catalog = validate_preset_catalog(CATALOG)
        ids = {row["profile_id"] for row in catalog["profiles"]}
        self.assertIn("china_tang_changan_8c", ids)
        self.assertIn("china_ming_jiangnan_16c", ids)
        self.assertIn("europe_victorian_london_1890s", ids)
        self.assertIn("europe_belle_epoque_paris_1900s", ids)
        self.assertIn("europe_contemporary_berlin", ids)

    def test_historical_china_requires_specific_dynasty_and_period(self):
        profile = resolve_world_preset(CATALOG, "china_tang_changan_8c")
        self.assertEqual(profile["period"]["dynasty"], "Tang")
        bad = copy.deepcopy(profile)
        del bad["period"]["dynasty"]
        with self.assertRaisesRegex(WorldProfileError, "dynasty"):
            validate_world_profile(bad)

    def test_europe_requires_specific_country_and_region(self):
        profile = resolve_world_preset(CATALOG, "europe_belle_epoque_paris_1900s")
        bad = copy.deepcopy(profile)
        bad["country"] = "Europe"
        with self.assertRaisesRegex(WorldProfileError, "specific country"):
            validate_world_profile(bad)

    def test_shot_compiler_binds_world_without_overwriting_casting_identity(self):
        world = resolve_world_preset(CATALOG, "china_tang_changan_8c")
        compiled = compile_shot(SHOTS[5], LEDGER, CASTING, world_profile=world)
        self.assertEqual(compiled["world_profile_id"], "china_tang_changan_8c")
        self.assertIn('"dynasty": "Tang"', compiled["prompt"])
        self.assertIn("Vietnamese man, 28", compiled["prompt"])
        self.assertIn("Qing queue hairstyle", compiled["negative_prompt"])
        legacy = compile_shot(SHOTS[5], LEDGER, CASTING)
        self.assertNotIn("world=", legacy["prompt"])
        self.assertNotIn("world_profile_id", legacy)

    def test_visual_prompt_uses_world_context_without_dialogue_or_voice_metadata(self):
        world = resolve_world_preset(CATALOG, "china_tang_changan_8c")
        prompt = compile_visual_prompt(SHOTS[5], LEDGER, CASTING, world_profile=world, style_override="photoreal")
        self.assertIn("Tang dynasty", prompt)
        self.assertIn("Vietnamese", prompt)
        self.assertNotIn("dialogue=", prompt)
        self.assertNotIn("voice", prompt.lower())
        self.assertNotIn("zh-CN", prompt)
        self.assertIn("No written words", prompt)
        self.assertIn("Text-bearing props and signage should be avoided", prompt)
        self.assertIn("badge, sign or label surface is blank and unlettered", prompt)

    def test_casting_jobs_bind_world_and_anachronism_guards(self):
        world = resolve_world_preset(CATALOG, "europe_victorian_london_1890s")
        jobs, _, _ = compile_casting_jobs(CONTRACT, MATRIX, world_profile=world)
        self.assertTrue(jobs)
        self.assertTrue(all(row["world_profile_id"] == world["profile_id"] for row in jobs))
        self.assertIn("late Victorian London", jobs[0]["prompt"])
        self.assertIn("modern cars", jobs[0]["negative_prompt"])
        self.assertIn(CONTRACT["characters"][jobs[0]["character_id"]]["visual_target"], jobs[0]["prompt"])

    def test_scaffold_can_start_from_world_preset(self):
        world = resolve_world_preset(CATALOG, "china_ming_jiangnan_16c")
        scaffold = build_project_scaffold(
            project_id="mingfilm",
            title="Ming Film",
            source_packet=SOURCE,
            world_profile=world,
        )
        self.assertEqual(scaffold["files"]["project.json"]["world_profile_id"], world["profile_id"])
        self.assertEqual(scaffold["files"]["world/world_profile.json"]["period"]["dynasty"], "Ming")
        self.assertEqual(scaffold["files"]["casting.json"]["characters"], {})

    def test_scaffold_cli_accepts_builtin_world_preset(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "periodfilm"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tools/scaffold_project.py"),
                    "--project-id", "periodfilm",
                    "--title", "Period Film",
                    "--source-packet", str(P / "source/source_packet.json"),
                    "--world-preset", "europe_victorian_london_1890s",
                    "--out-dir", str(out),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            profile = json.loads((out / "world/world_profile.json").read_text(encoding="utf-8"))
            self.assertEqual(profile["profile_id"], "europe_victorian_london_1890s")


if __name__ == "__main__":
    unittest.main()