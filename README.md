# AI-FILM Phase00 — implementation source drop dev8

**IMPL-P00-001 · IMPLEMENTATION · 0.1.0.dev20 · AUTHOR_COMPLETE_CANDIDATE / CODE_REVIEW_PENDING**

**Full author-complete: false. Full-scope CODE_REVIEW handoff: NOT_READY.**

Dev14 aligns network transport with exact Design V2: P00 remains a fixed DIRECT probe and never invents a proxy/VPN remediation adapter. Actual environment/system/user proxy configuration is observed and fails as network context exit14 rather than being silently stripped/bypassed; controller parsing revalidates the proxy observation. Existing VPN/networking mode is preserved and actual bounded connectivity remains the acceptance fact. Full Phase00 implementation remains incomplete. No native Windows/WSL/LAB/SITE execution occurred during authoring.

## Read first

Read `docs/IMPLEMENTATION_STATUS.md`, `docs/REMAINING_IMPLEMENTATION.md`, `docs/NATIVE_INTEGRATION_BOUNDARY.md`, `docs/CHANGELOG_DEV13_TO_DEV14.md`, and `docs/TRACEABILITY.md`. Approved Phase00 Design V2 remains unchanged.

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
