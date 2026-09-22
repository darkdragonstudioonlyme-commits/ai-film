#!/usr/bin/env bash
set -euo pipefail
usage(){ echo "usage: $0 --binding PATH --binding-sha256 SHA256 --inbox DIR --out-root DIR" >&2; exit 64; }
BINDING= SHA= INBOX= OUT=
while (($#)); do case "$1" in
 --binding) BINDING=$2;shift 2;; --binding-sha256) SHA=$2;shift 2;; --inbox) INBOX=$2;shift 2;;
 --out-root) OUT=$2;shift 2;; *) usage;; esac; done
[[ -n "$BINDING" && -n "$SHA" && -n "$INBOX" && -n "$OUT" ]] || usage
TOOL_DIR=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$OUT"; chmod 700 "$OUT"
rm -f "$OUT/READY"
tmp=$(mktemp "$OUT/.watch.XXXXXX"); trap 'rm -f "$tmp"' EXIT
set +e
/usr/bin/python3 "$TOOL_DIR/v02-authority-preflight-v2.py" --binding "$BINDING" --binding-sha256 "$SHA" --inbox "$INBOX" --json >"$tmp"
rc=$?
set -e
mv "$tmp" "$OUT/preflight.json"; trap - EXIT
if [[ $rc -eq 0 ]]; then
  printf '%s\n' "$SHA" > "$OUT/READY"; chmod 600 "$OUT/READY"
  echo "V02_AUTHORITY_WATCH_V2_READY"
  exit 0
fi
echo "V02_AUTHORITY_WATCH_V2_BLOCKED"
exit "$rc"
