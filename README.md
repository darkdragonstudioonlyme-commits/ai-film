# AI-FILM Phase00 — implementation source drop dev8

**IMPL-P00-001 · IMPLEMENTATION · 0.1.0.dev9 · PARTIAL_SOURCE_DROP_DEV9**

**Full author-complete: false. Full-scope CODE_REVIEW handoff: NOT_READY.**

Dev9 closes the concrete dev8 review findings CR-P00-002/003/004: durable owner-wait relabel now re-authorizes immediately before persistence; operator waits retain only typed/bounded safe context and a result/prior-wait digest; actual pending-reboot cause is no longer discarded. Full Phase00 implementation remains incomplete. No native Windows/WSL/LAB/SITE execution occurred during authoring.

## Read first

Read `docs/IMPLEMENTATION_STATUS.md`, `docs/REMAINING_IMPLEMENTATION.md`, `docs/NATIVE_INTEGRATION_BOUNDARY.md`, `docs/CHANGELOG_DEV8_TO_DEV9.md`, and `docs/TRACEABILITY.md`. Approved Phase00 Design V2 remains unchanged.

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
