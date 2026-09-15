# CHANGELOG — dev18 → dev19

## Review remediation

- CR-P00-012: remove unsupported `collector_release.contract_digest` dependency; contract is validated at the exact LAB suite boundary and collector release remains build-bound.
- CR-P00-014: restore production-shaped collector fixtures and add independent valid/wrong-build/wrong-contract suite coverage.
- Preserve CR-P00-013 stage continuity, temporal controller windows, exact procedure-owned route mappings and T07-H causal sequence.

## Tests

- Added positive coverage for a production-shaped collector under a valid contract-bound suite.
- Split wrong-build and wrong-suite-contract rejection tests so authority boundaries cannot be conflated.
- Native Windows/WSL/LAB/SITE remains NOT_RUN.

## Contracts

- No FD/D00/public contract change and no acceptance lowering.
