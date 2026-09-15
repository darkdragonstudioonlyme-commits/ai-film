# AI-FILM Phase00 — implementation source drop dev8

**IMPL-P00-001 · IMPLEMENTATION · 0.1.0.dev13 · PARTIAL_SOURCE_DROP_DEV13**

**Full author-complete: false. Full-scope CODE_REVIEW handoff: NOT_READY.**

Dev13 preserves dev12 staged E16/E17 recovery and closes review finding CR-P00-006: a no-archive E16 outcome is accepted only if the exact approved final output path is currently absent. Pre-existing stale output is rejected without delete/overwrite. Full Phase00 implementation remains incomplete. No native Windows/WSL/LAB/SITE execution occurred during authoring.

## Read first

Read `docs/IMPLEMENTATION_STATUS.md`, `docs/REMAINING_IMPLEMENTATION.md`, `docs/NATIVE_INTEGRATION_BOUNDARY.md`, `docs/CHANGELOG_DEV12_TO_DEV13.md`, and `docs/TRACEABILITY.md`. Approved Phase00 Design V2 remains unchanged.

## Workspace-only checks

From an isolated POSIX workspace with Python 3.11+:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:tests python tools/run_workspace_tests.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python tools/check_source.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m aifilm_p00 preflight --workspace-only
```

Workspace tests are author evidence only. They do not close AC00-01…08, the native T/F inventory, qualification, CODE_REVIEW_PASS, or HOST_READY.

## Delivery boundaries

Immutable approved contract digest: `f259656c48ed24c15bd48da2bb040950ed94d8edcf1473cf6456b96578c933ee`. Design PASS remains exact V2 only. Code review NOT_PERFORMED; HOST_READY NOT_EVALUATED; qualification not issued; baseline not promoted.
