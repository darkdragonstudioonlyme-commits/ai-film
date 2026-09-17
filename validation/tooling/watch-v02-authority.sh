#!/usr/bin/env bash
set -euo pipefail
umask 077
OUT=/home/dragon/ai-film-dev/run-evidence/validation/v02-authority
TOOL_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
VALIDATOR="$TOOL_DIR/v02-authority-intake.py"
INBOX=/mnt/c/Users/Admin/AppData/Local/AI-FILM/LAB/authority-approved/dev21
mkdir -p "$OUT"
flag="$OUT/READY_TO_ADVANCE.flag"
# Fail closed before every evaluation: READY exists only as a product of the current successful evaluation.
rm -f "$flag"
tmp=$(mktemp "$OUT/.latest.XXXXXX")
set +e
"$VALIDATOR" --inbox "$INBOX" >"$tmp"
rc=$?
set -e
mv -f "$tmp" "$OUT/latest.json"
sha256sum "$OUT/latest.json" >"$OUT/latest.sha256"
set +e
status=$(python3 - "$OUT/latest.json" <<'PY2'
import json,sys
try:
    data=json.load(open(sys.argv[1],encoding='utf-8'))
    value=data.get('status')
    print(value if isinstance(value,str) else 'UNREADABLE')
except Exception:
    print('UNREADABLE')
PY2
)
parse_rc=$?
set -e
if [[ $parse_rc -ne 0 || "$status" == UNREADABLE ]]; then
  echo "V02_AUTHORITY_WATCH_ERROR status=UNREADABLE rc=$rc" >&2
  exit 1
fi
case "$status:$rc" in
  BLOCKED:12)
    rm -f "$flag"
    echo 'V02_AUTHORITY_WATCH_BLOCKED'
    exit 0
    ;;
  READY_TO_ADVANCE:0)
    sha256sum "$OUT/latest.json" | awk '{print $1}' >"$flag"
    chmod 600 "$flag"
    echo 'V02_AUTHORITY_WATCH_READY_OPERATOR_ACTION_REQUIRED'
    exit 0
    ;;
  *)
    rm -f "$flag"
    echo "V02_AUTHORITY_WATCH_ERROR status=$status rc=$rc" >&2
    exit 1
    ;;
esac
