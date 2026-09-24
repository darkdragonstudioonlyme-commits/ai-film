import json
import unittest
from pathlib import Path
from film.shot_compiler import compile_shot

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/"projects"/"slice01"
LEDGER=json.loads((P/"continuity.json").read_text(encoding="utf-8"))
CASTING=json.loads((P/"casting.json").read_text(encoding="utf-8"))
SHOTS=json.loads((P/"shots/benchmark_shots.json").read_text(encoding="utf-8"))

class ShotCompilerTests(unittest.TestCase):
    def test_compiler_is_deterministic(self):
        a=compile_shot(SHOTS[5],LEDGER,CASTING)
        b=compile_shot(SHOTS[5],LEDGER,CASTING)
        self.assertEqual(a,b)
        self.assertIn("clean white gauze",a["prompt"])
        self.assertEqual(a["aspect"],"9:16")
        self.assertEqual(a["dialogue_id"],"dlg_003")

    def test_fixed_benchmark_has_eight_shots(self):
        self.assertEqual(len(SHOTS),8)
        self.assertEqual(len({s["seed"] for s in SHOTS}),8)

if __name__=="__main__":
    unittest.main()
