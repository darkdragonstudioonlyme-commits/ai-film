# AI-FILM Phase00 — implementation source drop dev4

**WORK_ITEM: IMPL-P00-001 · MODE: IMPLEMENTATION · VERSION: 0.1.0.dev4**

**PARTIAL_SOURCE_DROP_DEV4. AUTHOR_COMPLETE=false. Full-scope CODE_REVIEW handoff: NOT_READY.**

This revision adds original-fence recovery/diagnostics/pause/cancellation, live committed-run revalidation, detached-read journal checks and script-byte pinning to the exact approved source inventory. These are source and author-test improvements, not native execution evidence. C0 observation-to-binding, complete lifecycle/evidence entry integration and the full native controller harness remain unfinished code.

## Start with the boundaries

[Implementation status](docs/IMPLEMENTATION_STATUS.md), [remaining source work](docs/REMAINING_IMPLEMENTATION.md), [integration boundary](docs/NATIVE_INTEGRATION_BOUNDARY.md) and [recovery contract](docs/RECOVERY.md) describe implemented components and outstanding source blockers. [Change log](docs/CHANGELOG_DEV3_TO_DEV4.md) and `source_diff.patch` compare exact parent dev3 bytes.

The primary native `apply`, `verify` and `support-bundle` CLI commands still return **11 / NATIVE_BACKEND_NOT_IMPLEMENTED**. Native `preflight` remains partial C0 inventory. Offline `dry-run` does not turn user-supplied bindings into observations. No fake/MemoryGuard fallback is registered. Native factory code is not authorization to call it on a host.

## Workspace-only author checks

From this package directory, using an isolated POSIX workspace with Python 3.11+:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:tests python tools/run_workspace_tests.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python tools/check_source.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m aifilm_p00 preflight --workspace-only
```

The delivered report records **534 successful tests**, no failures/errors/skips, and **71 static checks**. Tests use explicit synthetic ports and POSIX temporary files. They do not call a native Windows factory, PowerShell, guest script or live network. Static checks are Python AST, JSON parsing and shell syntax only. The original dev3 regression was also rerun successfully (458 tests); actual logs are retained in `evidence/dev4-history/`.

These totals do not close the eight ACs or the **86 native T/F/subcase entries**, which remain NOT_EVALUATED/NOT_RUN. Only the existing five native foundation procedures are authored; the complete native route/failure controller harness is still missing.

## New source locations

| Path | Role |
|---|---|
| `src/aifilm_p00/recovery.py` | Original-fence intent, one-guard recovery, protected diagnostics and non-success pause |
| `src/aifilm_p00/native/recovery_driver.py` | Native metadata/writer/service/revocation observation; no mutation replay |
| `src/aifilm_p00/native/read_recovery.py` | Detached read-process journal accounting and recovery helpers |
| `src/aifilm_p00/native/noop.py` | Live after-state/content/asset revalidation; no installer/lifecycle/workspace replay |
| `src/aifilm_p00/native/source_pin.py` | Script-member bytes tied to approved source digest, not self-generated trust |
| `src/aifilm_p00/session.py`, `resume.py`, `admission.py` | Separate revalidation intent/progress, SAFE_PAUSE/CLEAR semantics |
| `tests/test_dev4_*.py` | 76 new workspace cases; not native validation |
| `contracts/` | Unmodified approved V2 documents, approval and Blueprint |
| `history/dev3/` | Exact historical parent documents; not current status |

## Gates

Approved contract digest: `f259656c48ed24c15bd48da2bb040950ed94d8edcf1473cf6456b96578c933ee`. Design review remains PASS for exact V2. Code review NOT_PERFORMED. HOST_READY NOT_EVALUATED. No qualification or baseline promotion. State V9 retains IMPLEMENTATION and all REM-01…08 at OPEN full-item scope.
