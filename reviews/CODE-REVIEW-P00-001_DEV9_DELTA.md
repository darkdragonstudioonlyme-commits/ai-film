# CODE-REVIEW-P00-001 — dev9 delta review

```yaml
MODE: CODE_REVIEW
PHASE: "00 — Host / WSL"
TARGET: 0.1.0.dev9
SOURCE_COMMIT: 3da3ddc771c15d175a2c5045c86a7c1ff9987dbd
PACKAGE_SHA256: d6f83dc3ff60f73acd54750f58db34d817c7bb492c83088693f7c47c65d510cb
REVIEW_SCOPE: CR-P00-002/003/004 remediation
SOURCE_MODIFIED_DURING_REVIEW: false
DELTA_VERDICT: PASS
OVERALL_CODE_REVIEW_VERDICT: FAIL
CODE_REVIEW_PASS: false
```

## Independent evidence

REVIEW worktree was detached at the exact candidate commit. Independent rerun produced **692 PASS / 93 static PASS** with source digest `09104ef51e06d9d3be984271c1f2eaf3b7d7a2fa3c1f5435cab6d20e45248b93` and test digest `59e56a692018fce4d5514d0083d861423d1e2b6fa131d3a7756804afe1b7f697`.

Package verification independently reproduced size `1114609`, SHA-256 `d6f83dc3ff60f73acd54750f58db34d817c7bb492c83088693f7c47c65d510cb`, candidate commit `3da3ddc...`, and all manifest-listed member hashes. No approved contract file changed.

## Finding dispositions

### CR-P00-002 — CLOSED

The owner-verification recovery branch now checks exact fence identity, performs `_reauthorize(...)` after observation and immediately before persistence, checks authority generation/actor/request state, rechecks fence identity, then performs the durable relabel.

Independent reproduction of the prior failure scenario now returns `12/APPROVAL_EXPIRED` and leaves the original `AWAITING_USER_INIT` fence unchanged. Focused tests also cover authority-generation rollback, actor drift and recovery-request drift.

### CR-P00-003 — CLOSED

SessionRunner/legacy engine now project operator-wait results to a typed safe `wait_observation`. For an observed pending reboot, the durable fence retains normalized `cbs_reboot_pending` / `windows_update_reboot_required`, reason, previous state and result digest. Raw result fields are not copied.

Independent review scenario confirmed the pending flags were durable and `raw_output` was absent.

### CR-P00-004 — CLOSED

`Coordinator.awaiting` now requires a typed observation validated by `native.lifecycle.validate_wait_observation`: exact allowed fields, per-kind semantic rules, previous-state binding, fixed reboot-indicator keys, digest validation and a canonical 1024-byte cap. Unknown/sensitive fields and oversized payloads are rejected before durable persistence.

## Overall verdict

**FAIL for the full CODE_REVIEW gate.** Dev9 closes the three concrete dev8 review defects, but CR-P00-001 remains. The implementation still declares `AUTHOR_COMPLETE=false`; prior pre-C3/checkpoint/nested E00, publication recovery, non-DIRECT transport, causal 86-case harness and production-factory integration remain open.

Required next action: return global execution to IMPLEMENT lane and continue the next coherent implementation increment. Formal `CODE_REVIEW_PASS` remains unavailable until the full handoff gate is satisfied.
