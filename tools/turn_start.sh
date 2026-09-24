#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
git fetch origin --prune >/dev/null 2>&1 || true
echo "=== RESUME ==="
sed -n '1,80p' RESUME.md
echo "=== READY BACKLOG ==="
awk '/^- id:/{id=$0} /status: READY/{print id " | " $0}' BACKLOG.yaml
echo "=== MILESTONES ==="
grep -E '^- \[[ x]\]' MILESTONES.md
echo "=== STATUS ==="
git status --short --branch
