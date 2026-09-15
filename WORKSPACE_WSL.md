# AI-FILM-SERVER — WSL Development Workspace

This file documents the currently prepared WSL development workspace so a future chat can resume without rediscovering local paths, environment behavior, or Git limitations.

## Workspace identity

```yaml
DEVICE: DESKTOP-LCISMET
WSL_DISTRO: Ubuntu 24.04.4 LTS
KERNEL: 6.18.33.2-microsoft-standard-WSL2
USER: dragon
HOME: /home/dragon
WORKSPACE_ROOT: /home/dragon/ai-film-dev
```

## Layout

```text
/home/dragon/ai-film-dev/
├── repo/                 # clone of darkdragonstudioonlyme-commits/ai-film
├── source-dev7/          # exact extracted implementation package 0.1.0.dev7
├── artifacts/            # exact downloaded delivery archives
├── run-evidence/         # per-run author-test outputs outside source Git
├── .venv/                # isolated Python 3.12 author-test environment
├── env.sh                # enter source + environment variables
├── test.sh               # workspace regression + static checks
└── README-WORKSPACE.md   # local quick reference
```

## Canonical Git clone

Repository:

```text
https://github.com/darkdragonstudioonlyme-commits/ai-film.git
```

Local clone:

```text
/home/dragon/ai-film-dev/repo
```

Repo-local identity:

```text
user.name  = darkdragonstudioonlyme-commits
user.email = darkdragon.studio.onlyme@gmail.com
```

The WSL clone can fetch/pull public repository state. Direct local `git push` is **not currently authenticated**. Git Credential Manager exists on the Windows side, but an automated WSL probe waited for interactive authentication/UI; the helper was removed from the local repo to avoid future hangs.

Until WSL Git authentication is explicitly configured, use the connected GitHub connector for remote writes/push-equivalent state updates. Do not store a PAT in plaintext files.

## Exact implementation baseline in WSL

Source directory:

```text
/home/dragon/ai-film-dev/source-dev7
```

Archive:

```text
/home/dragon/ai-film-dev/artifacts/IMPL-P00-001_IMPLEMENTATION_PACKAGE_V7.zip
```

Verified archive identity:

```text
SHA-256: 63f9a8ce948ff0bb80de5d0dc37cc75a0c37723579ac1930098cca7e4de49312
```

The archive was downloaded from the verified Drive recovery anchor and SHA-256 was checked before extraction.

`source-dev7/` is initialized as a **local Git repository** for WSL diff/rollback:

```text
branch: dev7-baseline
baseline commit: b937649c1344baef3eb7b221ddd0347f5954ed85
message: baseline: exact IMPL-P00-001 dev7
```

This local source Git history is a development convenience. It is not a substitute for the canonical GitHub state/commit ledger or the verified Drive delivery artifact.

## Python environment

System Python:

```text
/usr/bin/python3 = Python 3.12.3
```

Ubuntu does not currently have the `python3.12-venv` package/ensurepip installed, and non-interactive sudo requires a password. Therefore the workspace uses:

```text
/usr/bin/python3 -m venv --without-pip /home/dragon/ai-film-dev/.venv
```

The current dev7 `pyproject.toml` has no external runtime dependencies, so the isolated environment is made functional with `.pth` entries pointing to:

```text
/home/dragon/ai-film-dev/source-dev7/src
/home/dragon/ai-film-dev/source-dev7/tests
```

This is intentional and sufficient for the current author-test baseline. If future source adds external Python dependencies, install `python3.12-venv`/pip through an authorized interactive sudo step or adopt another reviewed package-management path; do not silently reuse another project's venv.

## Enter environment

```bash
source /home/dragon/ai-film-dev/env.sh
```

This sets:

```text
VIRTUAL_ENV=/home/dragon/ai-film-dev/.venv
PYTHONPATH=/home/dragon/ai-film-dev/source-dev7/src:/home/dragon/ai-film-dev/source-dev7/tests
PYTHONDONTWRITEBYTECODE=1
```

and changes directory to `source-dev7`.

## Run author tests

```bash
/home/dragon/ai-film-dev/test.sh
```

Verified WSL result after setup:

```text
workspace tests: 673 PASS / 0 failures / 0 errors / 0 skipped
static checks:   90 PASS / 0 failed
source digest:   93e28ed77c132ad032cf8bf951e7d51627f6f8d007aa4179bb5696f0d6f1c6e8
test digest:     1c79354e63bdc76de157621547a7f92eb97d98fa90a6e53856619861103a3799
```

The package's official runners rewrite three evidence files inside the source tree. The workspace `test.sh` therefore:

1. runs the official workspace test runner;
2. copies generated test log/report into `/home/dragon/ai-film-dev/run-evidence/<UTC timestamp>/`;
3. runs static checks and copies their report to the same run directory;
4. restores the three package evidence files from the local Git baseline on exit.

This keeps `source-dev7` clean after a verification run while preserving the actual WSL-run evidence externally. A verified run after this optimization produced the same 673 PASS + 90 static result and left `git status` clean.

These are author/workspace checks only. They are not Windows/WSL native validation, LAB/SITE evidence, qualification, CODE_REVIEW_PASS, or HOST_READY.

## Safety boundaries

The workspace setup did **not**:

- modify `.wslconfig` or global WSL networking/resource settings;
- create/remove/import/unregister any distro;
- execute Phase00 native provisioning routes;
- run Windows/WSL/LAB/SITE/guest/live-network validation;
- modify existing `/home/dragon` project directories outside `/home/dragon/ai-film-dev`;
- write GitHub credentials or tokens to disk.

## Future-chat startup on WSL

A future chat with Desktop Commander should:

1. Read `PROJECT_STATE.md`, `NEXT_WORK_ITEM.md`, relevant `PROJECT_MEMORY.md` entries, and this file.
2. Verify `/home/dragon/ai-film-dev/repo` and `/home/dragon/ai-film-dev/source-dev7` exist.
3. Run `git status` in both local Git repositories.
4. Run `/home/dragon/ai-film-dev/test.sh` before changing source when practical.
5. Confirm the source Git returns clean after the test helper completes.
6. Continue only the current recorded implementation increment.
7. Persist reusable discoveries automatically through the Documentation Sync Gate.
