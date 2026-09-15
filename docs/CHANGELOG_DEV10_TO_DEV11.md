# CHANGELOG — dev10 → dev11

- Close CR-P00-005 at implementation level: `_pre_c3_events` now requires an explicit current-time bound and rejects `checked_at` later than the capture context.
- Added focused future-PRE_C3 negative test.
- No FD/D00/public-contract change; no freshness TTL introduced.
- Final author regression: 711 PASS; static: 94 PASS; native Windows/WSL/LAB/SITE: NOT_RUN.
