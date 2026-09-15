# AI-FILM-SERVER — WSL Workspace Map

## Identity

```yaml
DEVICE: DESKTOP-LCISMET
DISTRO: Ubuntu 24.04.4 LTS
USER: dragon
ROOT: /home/dragon/ai-film-dev
```

## Worktrees

```text
repo/         canonical GitHub control-plane clone
source-dev8/  immutable historical dev8 baseline
implement/    writable source lane, branch impl/p00
review/       detached exact source review candidate
docs-v2-design/  active Documentation System V2 design lane
docs-v2-review/  active detailed V2 review lane
docs-v2-audit/   active holistic V2 audit lane
docs-design/     historical V1 design worktree; not active
docs-review/     historical V1 review worktree; not active
artifacts/    exact delivery ZIPs
run-evidence/implement/
run-evidence/review/
```

## Source-state ownership

This file intentionally does **not** pin current delivery versions, source commit SHAs, WIP dirty files, review target or test counts. Those mutable facts are owned by `PROJECT_STATE.md`, `NEXT_WORK_ITEM.md` and freshly fetched lane state.

Before source work:

```bash
python3 /home/dragon/ai-film-dev/repo/tools/check_runtime_state.py

git -C /home/dragon/ai-film-dev/implement status --short --branch
git -C /home/dragon/ai-film-dev/review status --short --branch
```

Direct WSL HTTPS push is currently not configured for unattended use; connected GitHub tools persist remote control-plane state. If that capability changes, update this workspace/tooling fact but still keep mutable candidate identity in `PROJECT_STATE.md`.

## Lane helpers

```bash
source /home/dragon/ai-film-dev/implement-env.sh
/home/dragon/ai-film-dev/lane-test.sh implement

source /home/dragon/ai-film-dev/review-env.sh
/home/dragon/ai-film-dev/lane-test.sh review
```

Current Python environment is `/home/dragon/ai-film-dev/.venv` (Python 3.12, no pip). This remains acceptable only while the implementation package has no external Python dependencies.

## Bootstrap safety

1. Pull/fetch the canonical repo first.
2. Fresh-fetch relevant lane refs; do not trust cached `origin/lane/*` state.
3. Check selected worktree `git status` before checkout/reset.
4. If WIP is documented, preserve it.
5. REVIEW must remain detached at exact handed-off commit.
6. Test helpers keep lane evidence separate and restore tracked generated evidence.

No plaintext GitHub credentials are stored in this workspace.

## Benchmark/environment ownership

This file owns workspace paths/tools only. Hardware/model benchmark identity is owned by `SERVER_ENVIRONMENT.md`; model comparison procedure is `MODEL_EVALUATION.md`. Do not copy mutable benchmark hardware facts here as a second authority.
