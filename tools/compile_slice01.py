#!/usr/bin/env python3
import json
from pathlib import Path
from film.shot_compiler import compile_shot

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "projects" / "slice01"
ledger = json.loads((P / "continuity.json").read_text(encoding="utf-8"))
casting = json.loads((P / "casting.json").read_text(encoding="utf-8"))
shots = json.loads((P / "shots" / "benchmark_shots.json").read_text(encoding="utf-8"))
out = P / "compiled"
out.mkdir(parents=True, exist_ok=True)
compiled = []
for shot in shots:
    item = compile_shot(shot, ledger, casting)
    compiled.append(item)
    (out / f"{shot['shot_id']}.json").write_text(
        json.dumps(item, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
(out / "benchmark_compiled.json").write_text(
    json.dumps(compiled, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(f"compiled {len(compiled)} shots -> {out}")
