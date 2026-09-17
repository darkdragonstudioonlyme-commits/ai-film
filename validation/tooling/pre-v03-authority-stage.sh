#!/usr/bin/env bash
set -euo pipefail
umask 077
ROOT=/home/dragon/ai-film-dev/run-evidence/validation/v02-authority
INBOX=/mnt/c/Users/Admin/AppData/Local/AI-FILM/LAB/authority-approved/dev21
TOOL_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
VALIDATOR="$TOOL_DIR/v02-authority-intake.py"
MATERIALIZER="$TOOL_DIR/materialize-v02-native-policy.py"
SEAL="$TOOL_DIR/verify-lab-artifact-seal.py"
mkdir -p "$ROOT"
intake="$ROOT/pre-v03-intake.json"
set +e
"$VALIDATOR" --inbox "$INBOX" >"$intake"
irc=$?
set -e
chmod 600 "$intake"
if [[ $irc -ne 0 ]]; then
  echo "PRE_V03_STAGE_BLOCKED_AUTHORITY rc=$irc"
  exit 12
fi
seal_out="$ROOT/pre-v03-artifact-seal.json"
"$SEAL" >"$seal_out"
chmod 600 "$seal_out"
policy_out="$ROOT/pre-v03-policy-stage.json"
set +e
"$MATERIALIZER" --inbox "$INBOX" >"$policy_out"
prc=$?
set -e
chmod 600 "$policy_out"
if [[ $prc -ne 0 ]]; then
  echo "PRE_V03_STAGE_BLOCKED_POLICY rc=$prc"
  exit 12
fi
policy_file="$ROOT/native-policy.candidate.json"
test -s "$policy_file"
policy_sha=$(sha256sum "$policy_file" | awk '{print $1}')
wsl_state=$(/home/dragon/ai-film-dev/root-ops/private-windows-interop.sh /mnt/c/Windows/System32/wsl.exe -l -v | tr -d '\r\000')
if ! grep -Eq 'AI-FILM-P00-LAB[[:space:]]+Stopped' <<<"$wsl_state"; then
  echo 'PRE_V03_STAGE_BLOCKED_LAB_NOT_STOPPED'
  exit 12
fi
python3 - "$policy_sha" <<'PY'
import json,sys
print(json.dumps({'kind':'PRE_V03_AUTHORITY_STAGE','status':'READY_FOR_TRUST_ANCHOR_INSTALL_REVIEW',
 'candidate_id':'336b12af-cada-4968-8083-8a5b41e479a2','policy_sha256':sys.argv[1],
 'lab_state':'STOPPED','hklm_written':False,'native_execution_started':False},
 sort_keys=True,separators=(',',':')))
PY
