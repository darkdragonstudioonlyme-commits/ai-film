import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]

class SliceIntegrationTests(unittest.TestCase):
    def test_compile_all_benchmark_shots(self):
        subprocess.run([sys.executable,str(ROOT/"tools/compile_slice01.py")],cwd=ROOT,check=True)
        p=ROOT/"projects/slice01/compiled/benchmark_compiled.json"
        data=json.loads(p.read_text(encoding="utf-8"))
        self.assertEqual(len(data),8)
        self.assertEqual([x["shot_id"] for x in data],[f"sc01_sh0{i}" for i in range(1,9)])

if __name__=="__main__":
    unittest.main()
