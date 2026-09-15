# AI-FILM-SERVER — Prepared WSL Workspace

## Stable layout

```text
/home/dragon/ai-film-dev/
├── repo/             canonical main/control-plane clone
├── implement/        writable source workflow
├── review/           detached source-review candidate
├── docs-v2-design/   writable documentation-system design
├── docs-v2-review/   independent detailed documentation review
├── docs-v2-audit/    independent holistic documentation audit
├── artifacts/        exact delivery packages
├── run-evidence/     lane-scoped evidence
├── .venv/            project author-test Python environment
├── lane-test.sh      low-level source test executor
├── implement-env.sh
└── review-env.sh
```

Use `SERVER_ENVIRONMENT.md` for measured hardware/tool facts and model-evaluation readiness; do not duplicate them here.

## Environment/tool ownership

The project `.venv` has Python but no pip. Ambient `pip3` may resolve to another project's environment and must not be used implicitly. Tool provenance must be explicit before installing dependencies or benchmarking.

## Standard verification

Control plane:

```bash
cd /home/dragon/ai-film-dev/repo
/usr/bin/python3 tools/run_governance_checks.py
```

Business-governed source/review tests:

```bash
/usr/bin/python3 /home/dragon/ai-film-dev/repo/tools/run_test_workflow.py implement
/usr/bin/python3 /home/dragon/ai-film-dev/repo/tools/run_test_workflow.py review
```

`test.sh` is a managed compatibility entrypoint and must delegate to the canonical business-governed wrapper through `/usr/bin/python3`. `lane-test.sh` remains an explicit low-level source-test executor. Before V2 promotion, audit `tools/sync_workspace_helpers.py` against an isolated `--root`; after V2 is promoted to canonical `main`, run the sync tool on the real workspace and verify with `--check`. Runtime reconciliation then enforces exact helper content.

## Safety

Keep IMPLEMENT writable and REVIEW detached. Preserve WIP during governance repair. Direct WSL GitHub push remains unauthenticated; use connected GitHub write tools unless secure authentication is intentionally configured. No PAT/token in plaintext.
