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
docs-design/  documentation architecture authoring lane
docs-review/  independent documentation review lane
artifacts/    exact delivery ZIPs
run-evidence/implement/
run-evidence/review/
```

## Current source lane facts

- IMPLEMENT HEAD/base durable candidate: dev17 commit `64ea95bf10e05e856a009be9204983182f520b45`.
- IMPLEMENT currently has dev18 WIP in four modified files; do not discard it.
- Latest dev18 WIP author run: 756 PASS / 100 static PASS.
- REVIEW worktree is detached at dev17 while dev18 remains uncommitted.
- Direct WSL HTTPS push remains unauthenticated; connected GitHub tools persist remote control-plane state.

Exact current details belong in `PROJECT_STATE.md`; this file owns paths/tooling facts.

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
