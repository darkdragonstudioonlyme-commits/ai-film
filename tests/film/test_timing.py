import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from film.timing import build_srt, srt_timestamp, validate_timing

ROOT = Path(__file__).resolve().parents[2]
TIMING = json.loads((ROOT / "projects/slice01/timing/timing.json").read_text(encoding="utf-8"))
SHOTS = json.loads((ROOT / "projects/slice01/shots/benchmark_shots.json").read_text(encoding="utf-8"))


class TimingTests(unittest.TestCase):
    def test_timing_validates_to_75_seconds(self):
        value = validate_timing(TIMING, SHOTS)
        self.assertEqual(value["total_duration_sec"], 75.0)
        self.assertEqual(len(value["timeline"]), 8)
        self.assertEqual(len(value["dialogue_cues"]), 4)

    def test_subtitles_cover_three_languages(self):
        en = build_srt(TIMING, SHOTS, "en")
        zh = build_srt(TIMING, SHOTS, "zh-CN")
        vi = build_srt(TIMING, SHOTS, "vi")
        self.assertIn("Does the 11:40 still stop here?", en)
        self.assertIn("十一点四十的末班车还停这里吗？", zh)
        self.assertIn("Chuyến mười một giờ bốn mươi vẫn dừng ở đây chứ?", vi)
        self.assertEqual(en.count(" --> "), 4)
        self.assertEqual(zh.count(" --> "), 4)
        self.assertEqual(vi.count(" --> "), 4)

    def test_first_dialogue_global_timestamp(self):
        en = build_srt(TIMING, SHOTS, "en")
        self.assertIn("00:00:16,500 --> 00:00:20,000", en)

    def test_invalid_cue_outside_shot_is_rejected(self):
        bad = copy.deepcopy(TIMING)
        bad["dialogue_cues"][0]["end_offset_sec"] = 99
        with self.assertRaises(ValueError):
            validate_timing(bad, SHOTS)

    def test_timestamp_rounding(self):
        self.assertEqual(srt_timestamp(0), "00:00:00,000")
        self.assertEqual(srt_timestamp(75.1234), "00:01:15,123")

    def test_subtitle_cli_writes_deterministic_assets(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "subs"
            subprocess.run(
                [sys.executable, str(ROOT / "tools/build_subtitles.py"), "--out-dir", str(out)],
                cwd=ROOT,
                check=True,
                stdout=subprocess.DEVNULL,
            )
            self.assertTrue((out / "en.srt").is_file())
            self.assertTrue((out / "zh-CN.srt").is_file())
            self.assertTrue((out / "vi.srt").is_file())
            manifest = json.loads((out.parent / "timing_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["total_duration_sec"], 75.0)
            self.assertEqual(manifest["dialogue_cue_count"], 4)


if __name__ == "__main__":
    unittest.main()
