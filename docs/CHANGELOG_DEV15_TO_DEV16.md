# CHANGELOG — dev15 → dev16

## Review remediation

- Split suite authorization from post-run result-set aggregation.
- Added execution_id/suite_ref provenance to fixture result, measurement, stage, oracle, journal and result-set schemas.
- Added raw-bound exact journal trace records instead of accepting a journal hash alone.
- Added suite-window and causal-order timestamp enforcement.
- Added exact fixture-result and result-set refs to controller CLI.

## Tests

- Harness focused suite now covers suite replay, stale causal records and fabricated journal proof.
- Full author regression: 750 PASS. Static: 100 PASS.
- Native Windows/WSL/LAB/SITE: NOT_RUN.

## Contracts

- No FD/D00/public contract change.
