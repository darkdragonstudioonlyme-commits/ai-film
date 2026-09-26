#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from film.shot_compiler import compile_shot


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser(description="Compile a project's shots with optional world/period profile.")
    ap.add_argument("--project-dir", required=True)
    ap.add_argument("--shots", default="shots/shots.json")
    ap.add_argument("--out-dir", default="compiled")
    args = ap.parse_args()

    project = Path(args.project_dir).resolve()
    ledger = load(project / "continuity.json")
    casting = load(project / "casting.json")
    shots_payload = load(project / args.shots)
    shots = shots_payload.get("shots") if isinstance(shots_payload, dict) else shots_payload
    if not isinstance(shots, list) or not shots:
        raise SystemExit("project shots must be a non-empty list")

    world_path = project / "world/world_profile.json"
    world = load(world_path) if world_path.is_file() else None
    project_json = load(project / "project.json")
    aspect = project_json.get("master_aspect", "9:16")

    out = project / args.out_dir
    out.mkdir(parents=True, exist_ok=True)
    compiled = []
    for shot in shots:
        item = compile_shot(shot, ledger, casting, aspect=aspect, world_profile=world)
        compiled.append(item)
        (out / f"{shot['shot_id']}.json").write_text(
            json.dumps(item, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    (out / "compiled_shots.json").write_text(
        json.dumps(compiled, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "project_id": project_json.get("project_id"),
        "shot_count": len(compiled),
        "world_profile_id": world.get("profile_id") if world else None,
        "out_dir": str(out),
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())