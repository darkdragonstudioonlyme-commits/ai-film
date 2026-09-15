# CHANGELOG — dev16 → dev17

## Review remediation

- Added causal preparation-action trace schema and raw provenance.
- Added exact ordered controller-step trace schema and raw provenance.
- Replaced stage evidence-id strings with exact protected evidence refs bound to execution/suite/case/stage/plan/run.
- Added preparation mode identity to procedure digest and refreshed all 86 inventory procedure digests.

## Tests

- Focused harness suite: 14 PASS.
- Full author regression before packaging: 753 PASS. Static: 100 PASS.
- Native Windows/WSL/LAB/SITE: NOT_RUN.

## Contracts

- No FD/D00/public contract change or acceptance lowering.
