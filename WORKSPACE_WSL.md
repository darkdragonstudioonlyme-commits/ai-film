# AI-FILM-SERVER — WSL Development Workspace

Current prepared authoring environment for future chats using Desktop Commander.

## Identity

```yaml
DEVICE: DESKTOP-LCISMET
WSL_DISTRO: Ubuntu 24.04.4 LTS
KERNEL: 6.18.33.2-microsoft-standard-WSL2
USER: dragon
HOME: /home/dragon
WORKSPACE_ROOT: /home/dragon/ai-film-dev
ACTIVE_DELIVERY: 0.1.0.dev8
```

## Layout

```text
/home/dragon/ai-film-dev/
├── repo/                 # clone of canonical GitHub state/handoff repo
├── source-dev8/          # active exact dev8 source package + local Git baseline
├── source-dev7/          # clean exact dev7 rollback source
├── artifacts/            # exact downloaded delivery ZIPs
├── run-evidence/         # actual per-run author outputs outside source Git
├── .venv/                # isolated Python 3.12 author-test environment
├── env.sh                # enters source-dev8
├── test.sh               # regression + static checks, keeps source baseline clean
└── README-WORKSPACE.md   # local quick reference
```

## Canonical Git clone

```text
repo: https://github.com/darkdragonstudioonlyme-commits/ai-film.git
local: /home/dragon/ai-film-dev/repo
user.name: darkdragonstudioonlyme-commits
user.email: darkdragon.studio.onlyme@gmail.com
```

The clone can fetch/pull. Direct WSL HTTPS push is **not authenticated**. Windows Git Credential Manager is visible but the unattended probe waited for interactive UI, so no repo-local helper is left configured. Use local Git for diff/rollback and the connected GitHub connector for remote writes until a secure WSL authentication flow is explicitly configured. Never store a PAT/token in plaintext.

## Active exact source

```text
Directory: /home/dragon/ai-film-dev/source-dev8
Package:   /home/dragon/ai-film-dev/artifacts/IMPL-P00-001_IMPLEMENTATION_PACKAGE_V8.zip
SHA-256:  d4e6b67eebd40fbc173f85205792499021cf6eea9b82309e54c2a76a9a9e3cb5
Drive ID: 125T2wVf0CVkcmQND0PSmF3HHvXh8AgxD
Local branch: dev8-baseline
Local commit: c44c2f87084f8082ce29af5935c6b47d03f7b96c
```

The V8 ZIP was raw-downloaded from the verified Drive anchor, SHA-256 checked before extraction, then the extracted source reproduced the expected author digests/tests. `source-dev7/` was reset/cleaned back to exact dev7 after V8 became active.

## Python environment

System `/usr/bin/python3` is Python 3.12.3. Ubuntu currently lacks `python3.12-venv`/ensurepip and non-interactive sudo requires a password. The current package has no external Python dependencies, so the isolated environment is:

```text
/home/dragon/ai-film-dev/.venv
created with: /usr/bin/python3 -m venv --without-pip
```

`.pth` entries bind the active source/tests. This is valid only while dependencies remain empty. If dependencies are added, explicitly provision pip/venv via an authorized path; never reuse another project's environment.

## Enter environment

```bash
source /home/dragon/ai-film-dev/env.sh
```

Current bindings:

```text
VIRTUAL_ENV=/home/dragon/ai-film-dev/.venv
PYTHONPATH=/home/dragon/ai-film-dev/source-dev8/src:/home/dragon/ai-film-dev/source-dev8/tests
PYTHONDONTWRITEBYTECODE=1
```

## Run author verification

```bash
/home/dragon/ai-film-dev/test.sh
```

Verified active result:

```text
workspace tests: 683 PASS / 0 failures / 0 errors / 0 skipped
static checks:   92 PASS / 0 failed
source digest:   e793fc78d622c987343d1b5e5d3909cb4c19d7b0bcbafbc32909f137a1894c08
test digest:     f91b422b6ce4ffeee9fc516bff0dc00c8e4a6216ae98e94b977ac2ef00949021
```

The official runners rewrite three tracked evidence files. `test.sh` copies actual outputs into `/home/dragon/ai-film-dev/run-evidence/<UTC timestamp>/` and restores those tracked evidence files from the active local Git baseline on exit. A verification-only run must leave `source-dev8` clean.

These are author/workspace checks only. They are **not** Windows/WSL native validation, LAB/SITE evidence, qualification, CODE_REVIEW_PASS or HOST_READY.

## Safety boundaries

Workspace setup/authoring does not:

- modify `.wslconfig` or global WSL networking/resource settings;
- create/remove/import/unregister a distro;
- execute Phase00 native provisioning routes;
- perform Windows/WSL/LAB/SITE/guest/live-network validation;
- modify unrelated `/home/dragon` projects;
- store GitHub secrets/tokens on disk.

## Future-chat startup

1. Read `PROJECT_STATE.md`, `NEXT_WORK_ITEM.md`, relevant `PROJECT_MEMORY.md`, then this file.
2. Pull `/home/dragon/ai-film-dev/repo` and confirm it matches remote `main`.
3. Check `git status` in `repo`, `source-dev8`, and rollback source if relevant.
4. Run `/home/dragon/ai-film-dev/test.sh` before changes when practical.
5. Confirm `source-dev8` is clean after the helper.
6. Continue only the current increment recorded by `NEXT_WORK_ITEM.md`.
7. Persist reusable discoveries through the Documentation Sync Gate before starting another increment.
