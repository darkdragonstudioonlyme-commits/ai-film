# AI-FILM-SERVER — PROJECT MEMORY

> Living reusable knowledge for future chats.  
> Current state lives in `PROJECT_STATE.md`; next execution lives in `NEXT_WORK_ITEM.md`; historical full memory through V14 is archived at `memory/archive/PROJECT_MEMORY_V14.md`.

## No-silent-knowledge rule

A reusable discovery, optimization, tooling limitation, failure pattern, test lesson, risk, security rule, or clarification must be persisted before the related increment is considered durable.

Memory does not approve architecture or pass gates. If a discovery requires changing reviewed behavior, create a DESIGN_GAP in the correct mode.

## Active Memory Index

| ID | Type | Reusable rule |
|---|---|---|
| MEM-20260915-001 | PROCESS | Separate current state, next work, reusable knowledge, and immutable history. |
| MEM-20260915-002 | TOOLING | Exact baselines require byte-preserving transport plus independent identity verification. |
| MEM-20260915-003 | TESTING | Author regression/static checks are not Windows/WSL/LAB/SITE proof. |
| MEM-20260915-004 | PROCESS | An increment is durable only after remote artifact/state verification. |
| MEM-20260915-005 | SECURITY | Secret-scan every public-repo delivery; never persist real credentials/private assets. |
| MEM-20260915-006 | TOOLING | Prefer file-reference/raw-file actions for binary delivery artifacts. |
| MEM-20260915-007 | PROCESS | Hybrid persistence is valid when Git state and exact binary artifact roles are explicit. |
| MEM-20260915-008 | LESSON | Explicit missing state is safer than accepting non-identical bytes. |
| MEM-20260915-009 | TOOLING | If chunking is unavoidable, verify every Git blob SHA individually; prefer file-native transfer. |
| MEM-20260915-010 | TESTING | Use the package’s src-layout invocation (`PYTHONPATH=src` or official runner); import failure without it is not a source regression. |
| MEM-20260915-011 | SECURITY | Executable trust must bind path + exact bytes + policy scope + pinned handle + witness before process resume. |
| MEM-20260915-012 | TOOLING | Keep AI-FILM work in a dedicated WSL subtree and verify the exact delivery hash before extraction. |
| MEM-20260915-013 | TOOLING | If system `ensurepip` is unavailable and the project has no external deps, a `venv --without-pip` + `.pth` source binding is an acceptable isolated author-test environment. |
| MEM-20260915-014 | PROCESS | WSL local Git fetch/commit and GitHub remote write authority are separate; do not leave an interactive credential helper that can hang automation. |
| MEM-20260915-015 | TESTING | Author-test helpers should preserve actual run evidence outside the source baseline and restore generated package evidence files so baseline Git stays clean. |

## New entries since archived V14 memory

### MEM-20260915-010 — Src-layout test invocation is part of reproducible author evidence

```yaml
MEMORY_ID: MEM-20260915-010
TYPE: TESTING
STATUS: ACTIVE
DISCOVERED_IN:
  MODE: IMPLEMENTATION
  PHASE: "00 — Host / WSL"
  WORK_ITEM: IMPL-P00-001
SUMMARY: "The package uses a src/ layout; running unittest discovery without exposing src causes import failures that are invocation errors, not implementation regressions."
EVIDENCE: "The first dev7 baseline invocation without PYTHONPATH=src failed imports; rerunning with PYTHONPATH=src reproduced the verified dev6 baseline at 666/666 PASS. The official tools/run_workspace_tests.py path also completed successfully after the dev7 patch."
IMPACT: "Future chats could falsely diagnose a broken baseline or waste time patching imports."
REUSABLE_RULE: "For author regression use the documented package invocation: PYTHONPATH=src python -m unittest ... or the official workspace-test runner. Classify missing-src import errors as invocation/environment failures until source regression evidence exists."
AFFECTED_AREAS: [testing, reproducibility, tooling]
ACTION_TAKEN: "Dev7 baseline and final regression were run with the correct src-layout invocation."
FOLLOW_UP: "Keep the official invocation in delivery records and future CI/bootstrap documentation."
SUPERSEDES: []
SUPERSEDED_BY: null
```

### MEM-20260915-011 — Native child executable trust is byte identity, not path identity

```yaml
MEMORY_ID: MEM-20260915-011
TYPE: SECURITY
STATUS: ACTIVE
DISCOVERED_IN:
  MODE: IMPLEMENTATION
  PHASE: "00 — Host / WSL"
  WORK_ITEM: IMPL-P00-001
SUMMARY: "A trusted executable path alone does not prove the bytes actually launched are the reviewed dependency/controller binary."
EVIDENCE: "Dev7 added executable-policy pins scoped to host/build/contract, exact path/size/SHA-256 verification under pinned filesystem handles, administrative owner/writer constraints, mandatory production-supervisor trust before child creation, and process witnesses recording policy ref/hash/size/kind. Seven targeted tests and full 673-test regression passed."
IMPACT: "This closes a TOCTOU/trust gap at the native process boundary and makes later diagnostics/recovery able to identify the exact binary authorized for execution."
REUSABLE_RULE: "Before a native child is resumed, bind authority to policy-scoped exact binary bytes using a pinned handle; record that identity in the durable process witness. Never infer executable trust from path or process exit alone."
AFFECTED_AREAS: [security, native-process, trust, reproducibility]
ACTION_TAKEN: "Implemented ExecutableTrust, filesystem pinned_executable, production supervisor enforcement, binding requirement, authority refresh and witness fields in dev7."
FOLLOW_UP: "Do not overclaim: guest interpreter/rootfs provenance and remaining dependency/bootstrap trust are still open."
SUPERSEDES: []
SUPERSEDED_BY: null
```

### MEM-20260915-012 — Dedicated WSL workspace + hash-before-extract

```yaml
MEMORY_ID: MEM-20260915-012
TYPE: TOOLING
STATUS: ACTIVE
DISCOVERED_IN:
  MODE: IMPLEMENTATION
  PHASE: "00 — Host / WSL"
  WORK_ITEM: ENV-P00-GIT-001
SUMMARY: "A dedicated project subtree under /home/dragon avoids mixing AI-FILM state with unrelated local environments and makes cleanup/recovery predictable."
EVIDENCE: "Created /home/dragon/ai-film-dev; downloaded exact V7 archive, verified SHA-256 63f9a8ce...49312 before extraction, and reproduced 673 workspace PASS + 90 static PASS from the extracted source."
IMPACT: "Future chats can enter one known workspace without touching existing /home/dragon projects or reconstructing source from prose."
REUSABLE_RULE: "Use /home/dragon/ai-film-dev for this project; download exact delivery, verify recorded SHA before extraction, and keep canonical repo clone/source/artifacts/venv separated by directory."
AFFECTED_AREAS: [wsl, workspace, reproducibility, recovery]
ACTION_TAKEN: "Added WORKSPACE_WSL.md plus local env.sh/test.sh helper scripts."
FOLLOW_UP: "If the active delivery advances, keep old exact artifact for rollback and create/update the source workspace deliberately rather than overwriting an unverified tree."
SUPERSEDES: []
SUPERSEDED_BY: null
```

### MEM-20260915-013 — Isolated no-pip venv is sufficient only while dependencies are empty

```yaml
MEMORY_ID: MEM-20260915-013
TYPE: TOOLING
STATUS: ACTIVE
DISCOVERED_IN:
  MODE: IMPLEMENTATION
  PHASE: "00 — Host / WSL"
  WORK_ITEM: ENV-P00-GIT-001
SUMMARY: "Ubuntu system Python lacked ensurepip/python3.12-venv and sudo required an interactive password, but dev7 has zero external Python dependencies."
EVIDENCE: "System `/usr/bin/python3 -m venv` failed due missing ensurepip; sudo -n failed; `/usr/bin/python3 -m venv --without-pip` plus `.pth` entries for src/tests produced a clean isolated Python 3.12.3 environment and reproduced 673 tests + 90 static checks."
IMPACT: "The project can be tested now without reusing another project's venv, but future dependency additions would make this environment incomplete."
REUSABLE_RULE: "A no-pip venv + `.pth` source binding is acceptable for the current zero-dependency author-test baseline only. If external dependencies appear, explicitly provision python3.12-venv/pip (authorized sudo) or another reviewed package manager; never silently borrow `/home/dragon/arb/.venv`."
AFFECTED_AREAS: [python, wsl, dependency-management, testing]
ACTION_TAKEN: "Created `/home/dragon/ai-film-dev/.venv` without pip and bound exact dev7 src/tests via site-packages `.pth` files."
FOLLOW_UP: "Re-evaluate environment setup whenever pyproject dependencies change."
SUPERSEDES: []
SUPERSEDED_BY: null
```

### MEM-20260915-014 — Local Git operations and remote write authentication are separate concerns

```yaml
MEMORY_ID: MEM-20260915-014
TYPE: PROCESS
STATUS: ACTIVE
DISCOVERED_IN:
  MODE: IMPLEMENTATION
  PHASE: "00 — Host / WSL"
  WORK_ITEM: ENV-P00-GIT-001
SUMMARY: "WSL can clone/fetch the public GitHub repository and maintain local commits, while direct HTTPS push still requires a separate authenticated credential path."
EVIDENCE: "Clone/fetch succeeded. `git push --dry-run` failed without credentials. Windows Git Credential Manager is visible from WSL but an automated credential probe waited for interactive UI, so the repo-local helper was removed to prevent hangs."
IMPACT: "Future automation must not assume that a successful clone means WSL can push, and must not leave an interactive helper that blocks unattended tasks."
REUSABLE_RULE: "Use local Git for diff/commit/rollback; use the connected GitHub connector for remote writes until WSL authentication is explicitly configured. Never write PATs to plaintext files."
AFFECTED_AREAS: [git, github, wsl, automation, security]
ACTION_TAKEN: "Configured repo-local author identity, left credential.helper unset, initialized local dev7 source Git baseline commit b937649c..., and documented the limitation in WORKSPACE_WSL.md."
FOLLOW_UP: "If the user later wants direct WSL push, configure an explicit secure SSH/GCM flow as its own setup step and verify with push --dry-run before changing workflow policy."
SUPERSEDES: []
SUPERSEDED_BY: null
```

### MEM-20260915-015 — Test runs should not dirty the exact source baseline

```yaml
MEMORY_ID: MEM-20260915-015
TYPE: TESTING
STATUS: ACTIVE
DISCOVERED_IN:
  MODE: IMPLEMENTATION
  PHASE: "00 — Host / WSL"
  WORK_ITEM: ENV-P00-GIT-001
SUMMARY: "The official dev7 author-test/static runners rewrite evidence files inside the source tree, which makes an exact baseline Git worktree appear modified after a verification-only run."
EVIDENCE: "After the first WSL verification, local Git reported modifications to evidence/WORKSPACE_TEST_LOG.txt, evidence/WORKSPACE_TEST_REPORT.json and evidence/AUTHOR_STATIC_CHECKS.json. A wrapper was changed to copy actual WSL-run outputs into /home/dragon/ai-film-dev/run-evidence/<UTC timestamp>/ and restore those three source files from HEAD on exit. Re-running produced 673 PASS + 90 static and left `git status` clean."
IMPACT: "Future chats can distinguish source edits from test-output churn and retain actual run evidence without contaminating the baseline diff."
REUSABLE_RULE: "When verification tools overwrite tracked evidence, capture the actual outputs outside the source tree and restore baseline evidence files after the run; never hide real source/test code changes."
AFFECTED_AREAS: [testing, git, reproducibility, workspace]
ACTION_TAKEN: "Updated /home/dragon/ai-film-dev/test.sh and WORKSPACE_WSL.md; created /home/dragon/ai-film-dev/run-evidence/."
FOLLOW_UP: "If the package later supports configurable output paths, prefer that native option over wrapper restore logic."
SUPERSEDES: []
SUPERSEDED_BY: null
```

## Usage by future chats

1. Read `PROJECT_STATE.md` and `NEXT_WORK_ITEM.md` first.
2. Scan this Active Memory Index for current-task lessons.
3. Read `WORKSPACE_WSL.md` when operating through Desktop Commander/WSL.
4. Open `memory/archive/PROJECT_MEMORY_V14.md` only when older entry detail is needed.
5. Add/supersede memory entries automatically at every meaningful increment.
