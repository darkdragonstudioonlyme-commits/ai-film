# CHANGELOG — dev11 → dev12

## Publication/recovery

- deterministic journal-bound staging path for E16 bundle and E17 assessment;
- create-only stage + write-through no-replace final move;
- final-only exact recovery, temp-only retained failure, final+temp ambiguity, missing-output failure;
- durable no-archive E16 decisions for non-publishable/incomplete outcomes;
- E17 recovery integrated into GATE support-bundle reconciliation with applicability checks;
- no delete/rename/republication during recovery; E17 remains non-authoritative.

## Tests

- Final author regression: 728 PASS / 0 failure/error/skip.
- Static checks: 95 PASS / 0 failed.
- Native Windows/WSL/LAB/SITE: NOT_RUN.

## Contracts

No FD/D00/public-contract change.
