# CHANGELOG — dev9 → dev10

## Source

- `evidence_catalog.new_body` supports validated field-specific provenance metadata.
- Prior guest selection validates timestamp, host, execution class, target identity and exact history-plan membership.
- Added exact PRE_C3 event selection + historical protection receipt revalidation and target checkpoint provenance.
- Added committed RESTORE_EXPORT checkpoint history binding.
- E12 emits validated pre-C3 nested refs; E15 separates those refs from post-apply checkpoint provenance.

## Tests

- Added `tests/test_dev10_prior_nested.py` (18 focused cases).
- Final author regression: 710 PASS / 0 failure/error/skip.
- Static checks: 94 PASS / 0 failed.
- Native Windows/WSL/LAB/SITE execution: NOT_RUN.

## Contracts

No FD/D00/public-contract change.
