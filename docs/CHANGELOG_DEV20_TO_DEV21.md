# Changelog dev20 → dev21

Scope: remediate independent CODE_REVIEW finding `CR-P00-015` only. No reviewed FD/D00/public behavior or test-oracle change.

## Changes

- Replaced stale root README dev8/dev14 partial/not-ready text with current dev21 author-complete-candidate boundaries.
- Replaced stale dev8/dev5 code-review handoff draft with the exact dev21 delta-review contract.
- Removed the tracked V8 `MANIFEST.json`; package manifests are generated from the exact committed tree at the delivery boundary, avoiding a stale second manifest authority.
- Updated package version/status metadata to `0.1.0.dev21` and removed the stale package docstring claim that source/test closure is partial.
- Updated current implementation/remaining-work/traceability pointers for the CR-P00-015 correction.

## Preserved non-claims

- `CR-P00-015` is FIXED_PENDING_REVIEW, not self-closed.
- `CR-P00-001` remains open until independent delta review accepts the corrected exact candidate.
- Native Windows/WSL/LAB/SITE remains NOT_RUN.
- CODE_REVIEW_PASS, qualification and HOST_READY remain unissued/not evaluated.
