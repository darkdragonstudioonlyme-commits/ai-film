# CHANGELOG — dev7 → dev8

## Source

- Added `src/aifilm_p00/native/lifecycle.py`.
- Extended `Coordinator.awaiting()` with bounded durable wait context.
- Hardened C3 run classification for observed pending reboot after native process completion.
- Hardened reboot reconciliation with host-boot/pending-state boundary checks.
- Added post-reboot affected-resource checks for C3 mutation completion.
- Preserved OOBE owner wait separately from reboot-origin owner wait.
- Recovery now returns `AWAITING_OWNER_VERIFICATION/20` only from existing operator-wait states when owner postcondition evidence is missing.

## Tests

- Added `tests/test_dev8_lifecycle.py` with 10 focused synthetic author tests.
- Final author regression: 683 PASS / 0 failure/error/skip.
- Static checks: 92 PASS / 0 failed.
- No Windows/WSL/LAB/SITE native execution.

## Contracts

- No FD/D00/public-contract change.
- ENGINE and HOST_RESTART operation lists are unchanged.
- Final owner-planned restart is intentionally retained.
