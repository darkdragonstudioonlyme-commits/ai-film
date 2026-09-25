#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from film.blind_scoring import BlindScoreError, ScoreSchema, parse_score_csv, unblind_and_rank, validate_complete_scores


CASTING_SCHEMA = ScoreSchema(criteria=(
    "identity_match",
    "within_character_consistency",
    "between_character_separation",
    "style_quality",
    "anatomy_artifact_free",
    "overall",
))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate complete blind casting scores before unblinding/ranking.")
    parser.add_argument("--eval-dir", default="projects/slice01/casting/generation")
    parser.add_argument("--scores")
    parser.add_argument("--out")
    args = parser.parse_args()

    eval_dir = Path(args.eval_dir)
    if not eval_dir.is_absolute():
        eval_dir = ROOT / eval_dir
    public_path = eval_dir / "blind_items.json"
    score_path = Path(args.scores) if args.scores else eval_dir / "scores.csv"
    if not score_path.is_absolute():
        score_path = ROOT / score_path

    public = json.loads(public_path.read_text(encoding="utf-8"))
    score_rows = parse_score_csv(score_path.read_text(encoding="utf-8"))
    validated = validate_complete_scores(public["items"], score_rows, CASTING_SCHEMA)
    if any(not item.get("asset_id") or not item.get("asset_sha256") for item in public["items"]):
        raise BlindScoreError("casting asset identity incomplete; generated assets must be bound before unblinding")

    # Deliberately load the private map only after score completeness and public asset binding pass.
    private = json.loads((eval_dir / "blind_map_private.json").read_text(encoding="utf-8"))
    ranking = unblind_and_rank(
        validated,
        private["mapping"],
        group_fields=("model_id", "style"),
    )
    result = {
        "schema_version": 1,
        "status": "UNBLINDED_AFTER_COMPLETE_SCORING",
        "scored_items": len(validated),
        "ranking": ranking,
    }
    out_path = Path(args.out) if args.out else eval_dir / "ranking.json"
    if not out_path.is_absolute():
        out_path = ROOT / out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "scored_items": len(validated), "groups": len(ranking)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BlindScoreError as exc:
        print(f"BLIND_SCORE_FAIL: {exc}", file=sys.stderr)
        raise SystemExit(2)
