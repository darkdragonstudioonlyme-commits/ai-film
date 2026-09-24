import json
import unittest
from pathlib import Path
from film.continuity import state_at

ROOT=Path(__file__).resolve().parents[2]
LEDGER=json.loads((ROOT/"projects/slice01/continuity.json").read_text(encoding="utf-8"))

class ContinuityTests(unittest.TestCase):
    def test_injury_and_costume_damage_persist(self):
        state=state_at(LEDGER,"an","D1_2345")
        self.assertEqual(state["injuries"]["left_forearm"],"wrapped in clean white gauze")
        self.assertIn("left_sleeve",state["costume_damage"])

    def test_unknown_story_time_rejected(self):
        with self.assertRaises(KeyError):
            state_at(LEDGER,"an","D9_missing")

if __name__=="__main__":
    unittest.main()
