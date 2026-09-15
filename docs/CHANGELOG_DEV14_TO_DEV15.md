# CHANGELOG — dev14 → dev15

## Source

- Added `native/harness_cases.py`: exact 86-case procedure catalog.
- Added `native/harness_controller.py`: registered-LAB fixture/stage/oracle controller/finalizer.
- Added `tools/run_native_acceptance_tests.py`: metadata listing/description and Windows-only stage/finalize entry.
- Added internal production request composition seam without backend injection.
- Updated native inventory with exact procedure digests; statuses remain NOT_RUN.

## Tests

- Added `tests/test_dev15_harness.py` (8 author tests).
- Full author regression: 747 PASS. Static checks: 100 PASS.
- No native Windows/WSL/LAB/SITE execution occurred.

## Contracts

- No FD/D00/public contract change and no acceptance lowering.
