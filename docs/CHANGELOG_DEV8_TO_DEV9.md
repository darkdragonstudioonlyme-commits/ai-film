# CHANGELOG — dev8 → dev9

## Review findings addressed

- CR-P00-002: re-authorize immediately before persistent owner-verification relabel; reject approval expiry, authority rollback, actor drift and recovery-request drift after observation.
- CR-P00-003: persist safe typed wait cause instead of discarding observed pending-reboot facts.
- CR-P00-004: exact wait schemas, fixed pending-reboot keys, canonical 1024-byte cap, digest-only references and unknown/raw-field rejection.

## Tests

- Added `tests/test_dev9_review_fixes.py` (9 focused cases).
- Final author regression: 692 PASS / 0 failure/error/skip.
- Static checks: 93 PASS / 0 failed.
- Native Windows/WSL/LAB/SITE execution: NOT_RUN.

## Contracts

No FD/D00/public-contract change. CR-P00-001 remains open because full implementation scope is incomplete.
