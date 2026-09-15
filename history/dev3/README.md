# AI-FILM Phase00 — implementation source drop dev3

**WORK_ITEM: IMPL-P00-001 · MODE: IMPLEMENTATION · VERSION: 0.1.0.dev3**

**PARTIAL_SOURCE_DROP_DEV3. AUTHOR_COMPLETE=false. Full-scope CODE_REVIEW handoff is NOT_READY.**

This revision adds a concrete native session driver and connects guard, refreshed authority/observations, actuators, route observers, guest operations, terminal sweep and protected E00 snapshot/publication components. It does **not** finish every REM item. Do not mistake concrete source for native test evidence, or this package for a deployable host bootstrap.

The primary native `apply`, `verify` and `support-bundle` CLI commands still fail explicitly with `11 / NATIVE_BACKEND_NOT_IMPLEMENTED`. No MemoryGuard, fake observation, fixture approval or process-exit fallback is registered. The native factory is a code component, not permission to invoke it on a host.

## Start with the status, not the test count

[Implementation status](docs/IMPLEMENTATION_STATUS.md), [Remaining implementation](docs/REMAINING_IMPLEMENTATION.md) and [Integration boundary](docs/NATIVE_INTEGRATION_BOUNDARY.md) identify what is authored, tested only with explicit workspace ports, unexecuted natively, or still missing. [Change log](docs/CHANGELOG_DEV2_TO_DEV3.md) and `source_diff.patch` compare exact parent dev2 bytes.

Important remaining source blockers are the complete committed-run NOOP verifier; safe-pause/cancel and read-only diagnostics on an existing fence; finished original-plan reconciliation; full C0 inventory-to-plan integration; complete stage-specific E00 semantics/publication integration; and the full route/failure native harness. They are not requests for the user to supply missing data and are not merely missing Windows tests.

## Workspace-only author checks

From this directory, in an isolated POSIX workspace with Python 3.11+:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:tests python tools/run_workspace_tests.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python tools/check_source.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m aifilm_p00 preflight --workspace-only
```

These commands do not install packages, run PowerShell, start a distro or call a network endpoint. Tests use explicit synthetic ports and POSIX temporary files; they do not invoke `native_session()` or execute guest agents. The static checker parses Python and JSON and runs `sh -n`, not the shell script. No PowerShell parser is supplied in this environment.

`tools/run_native_foundation_tests.py --list` is only a metadata listing. Actual foundation cases require later authorized native gates. Only five foundation paths are authored; they are **not** the complete 86-entry T/F/subcase harness.

## Layout

| Path | Role |
|---|---|
| `src/aifilm_p00/session.py` | Single-admission per-step orchestration and result semantics |
| `src/aifilm_p00/native/session_driver.py` | Production-only native factory/driver; exact Win32/WSL ports |
| `src/aifilm_p00/native/proofs.py` | Pinned receipt/measurement provenance and claim-coverage checks |
| `src/aifilm_p00/native/observations.py`, `system_state.py` | Host/runtime/features/process/service observations |
| `native/guest-agent.py`, `native/host-observe.ps1` | Fixed guest/host observation/action source; not executed here |
| `src/aifilm_p00/native/terminal_sweep.py`, `network.py` | Context-separated terminal/network source |
| `src/aifilm_p00/evidence_catalog.py`, `native/evidence_pipeline.py` | Typed fields/stages, capture, snapshot, bundle and E17 proposal source |
| `src/aifilm_p00/native/artifacts.py` | Create-only protected records and committed snapshot selectors |
| `contracts/` | Byte-preserved approved V2 plus Blueprint/approval |
| `tests/`, `evidence/` | Executed workspace cases and actual reports; not acceptance evidence |
| `history/` | Prior states/documents/evidence, explicitly historical |

## Gates

Exact design contract digest: `f259656c48ed24c15bd48da2bb040950ed94d8edcf1473cf6456b96578c933ee`.
Design review remains PASS. Code review NOT_PERFORMED. HOST_READY NOT_EVALUATED. Qualification and baseline promotion NONE. All eight ACs remain NOT_EVALUATED and all 86 native inventory entries remain NOT_RUN. State V8 and the next-work-item document keep this task in IMPLEMENTATION.

No host/lab Windows/WSL operation or live network request was executed while producing this source drop.
