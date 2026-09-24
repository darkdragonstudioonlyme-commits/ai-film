#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
summary="$1"
tests="$2"
python3 - "$summary" "$tests" <<'PY'
import json,sys
from datetime import datetime,timezone
p="PROGRESS_LOG.jsonl"
rows=[x for x in open(p,encoding="utf-8") if x.strip()]
turn=len(rows)
rec={"turn":turn,"ts":datetime.now(timezone.utc).isoformat(),"actor":"turn_end","summary":sys.argv[1],"tests":sys.argv[2]}
with open(p,"a",encoding="utf-8") as f:
    f.write(json.dumps(rec,ensure_ascii=False)+"\n")
PY
echo "progress recorded; update BACKLOG/RESUME/MILESTONES before commit"
