# CHANGELOG — dev17 → dev18

## Independent review remediation

- CR-P00-012: bind every harness collector release to the exact suite build and approved contract.
- CR-P00-013: bind preparation continuity to exact stage windows and bind controller actions to exact procedure-owned route indices.
- Procedure digests now include `controller_stage_indices`; result evidence cannot rebind an action to another route.
- Corrected T07-H causal procedure so CREATE is explicitly invoked before reconciliation.
- Refreshed all 86 procedure digests/binding mirrors while preserving NOT_RUN/native-validation status.

## Tests

- Added/extended negative coverage for wrong collector build/contract, expired continuity, temporal window mismatch, and wrong action→route rebinding.
- Native Windows/WSL/LAB/SITE remains NOT_RUN.

## Contracts

- No FD/D00/public contract change and no acceptance lowering.
