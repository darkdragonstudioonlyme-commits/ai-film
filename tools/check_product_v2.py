#!/usr/bin/env python3
"""Structural contract for the active product-first control plane."""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

REQUIRED_ROOT = [
    "RESUME.md","BACKLOG.yaml","MILESTONES.md","CONTINUE_PROTOCOL.md",
    "DECISIONS.md","FILM_LEARNINGS.md","PROGRESS_LOG.jsonl",
]
LANGS = {"en","zh-CN","vi"}

def main() -> int:
    root=Path(__file__).resolve().parents[1]
    errors=[]
    state=(root/"PROJECT_STATE.md").read_text(encoding="utf-8")
    if "STATE_VERSION: PRODUCT_V2_" not in state:
        errors.append("state-not-product-v2")
    if "ACTIVE_ROUTER: CONTINUE_PROTOCOL.md" not in state:
        errors.append("router-not-v2")
    if "archive/p00-governance-2026-09-24" not in state:
        errors.append("legacy-baseline-not-declared")
    for rel in REQUIRED_ROOT:
        if not (root/rel).is_file():
            errors.append("missing:"+rel)
    if (root/"RESUME.md").stat().st_size > 4096:
        errors.append("resume-too-large")
    if (root/"CONTINUE_PROTOCOL.md").stat().st_size > 6144:
        errors.append("continue-protocol-too-large")

    backlog=(root/"BACKLOG.yaml").read_text(encoding="utf-8")
    ids=re.findall(r"^- id: (T-[0-9]+)$",backlog,re.M)
    if len(ids)!=len(set(ids)) or len(ids)<4:
        errors.append("backlog-ids")
    if "status: READY" not in backlog:
        errors.append("backlog-no-ready")

    p=root/"projects"/"slice01"
    project=json.loads((p/"project.json").read_text(encoding="utf-8"))
    ledger=json.loads((p/"continuity.json").read_text(encoding="utf-8"))
    casting=json.loads((p/"casting.json").read_text(encoding="utf-8"))
    shots=json.loads((p/"shots"/"benchmark_shots.json").read_text(encoding="utf-8"))
    if project.get("rights",{}).get("source")!="original_generated_for_project":
        errors.append("slice-rights-source")
    if set(project.get("languages",[])) != LANGS:
        errors.append("slice-languages")
    if len(shots)!=8 or len({s.get("shot_id") for s in shots})!=8 or len({s.get("seed") for s in shots})!=8:
        errors.append("benchmark-identity")
    times={x.get("t") for x in ledger.get("timeline",[])}
    for shot in shots:
        if shot.get("story_time") not in times:
            errors.append("unknown-story-time:"+str(shot.get("shot_id")))
        dialogue=shot.get("dialogue")
        if dialogue is not None:
            if set(dialogue)!=LANGS or not shot.get("dialogue_id"):
                errors.append("dialogue-contract:"+str(shot.get("shot_id")))
        for cid in shot.get("characters",[]):
            if cid not in ledger.get("characters",{}) or cid not in casting.get("characters",{}):
                errors.append("character-reference:"+cid)

    designs=list((root/"film"/"design").glob("*.md"))
    if len(designs)!=7:
        errors.append("film-design-count")
    if errors:
        print("PRODUCT_V2_CHECK_FAIL")
        print("\n".join(errors))
        return 1
    print("PRODUCT_V2_CHECK_PASS shots=8 designs=7 languages=en,zh-CN,vi")
    return 0

if __name__=="__main__":
    sys.exit(main())
