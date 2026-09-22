#!/usr/bin/env bash
set -euo pipefail
usage(){ echo "usage: $0 --binding PATH --binding-sha256 SHA256 --inbox DIR --out-root DIR --lab-state-file PATH --seal-root DIR" >&2; exit 64; }
BINDING= SHA= INBOX= OUT= STATE= SEAL=
while (($#)); do case "$1" in
 --binding) BINDING=$2;shift 2;; --binding-sha256) SHA=$2;shift 2;; --inbox) INBOX=$2;shift 2;;
 --out-root) OUT=$2;shift 2;; --lab-state-file) STATE=$2;shift 2;; --seal-root) SEAL=$2;shift 2;; *) usage;; esac; done
[[ -n "$BINDING" && -n "$SHA" && -n "$INBOX" && -n "$OUT" && -n "$STATE" && -n "$SEAL" ]] || usage
TOOL_DIR=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$OUT";chmod 700 "$OUT";rm -f "$OUT/READY"
[[ -f "$STATE" && "$(tr -d '\r\n' < "$STATE")" == "STOPPED" ]] || { echo PRE_V03_STAGE_V2_BLOCKED_LAB_NOT_STOPPED; exit 20; }
/usr/bin/python3 "$TOOL_DIR/v02-authority-preflight-v2.py" --binding "$BINDING" --binding-sha256 "$SHA" --inbox "$INBOX" --json >"$OUT/preflight.json"
/usr/bin/python3 "$TOOL_DIR/v02-authority-intake-v2.py" --binding "$BINDING" --binding-sha256 "$SHA" --inbox "$INBOX" >"$OUT/intake.json"
/usr/bin/python3 "$TOOL_DIR/materialize-v02-native-policy-v2.py" --binding "$BINDING" --binding-sha256 "$SHA" --inbox "$INBOX" --out "$OUT/native-policy.candidate.json" >"$OUT/materialize.json"
/usr/bin/python3 "$TOOL_DIR/verify-lab-artifact-seal-v2.py" --binding "$BINDING" --binding-sha256 "$SHA" --root "$SEAL" >"$OUT/seal.json"
printf '%s\n' "$SHA" > "$OUT/READY";chmod 600 "$OUT/READY"
echo PRE_V03_STAGE_V2_READY
