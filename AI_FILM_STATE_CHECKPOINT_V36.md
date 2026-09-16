# AI-FILM-SERVER — State Checkpoint V36

Phase00 product/native state is unchanged: accepted candidate `0.1.0.dev21` at source commit `934659f535d81d9a4a07389531acc2b9c304fa6d` remains code-review PASS; `RUN-P00-VALIDATION-001` remains BLOCKED at `V02_LAB_EXECUTION_AUTHORITY`; all 86 native acceptance procedures remain `NOT_RUN`; qualification is not issued and HOST_READY is not evaluated.

Documentation system remains `DOCSYS-V2-R9`. V36 is a production-like readiness plus scheduled learning-effectiveness reconciliation, not a new product release or native-validation transition.

## Production-like readiness reconciled

The validation lane now provides durable evidence for:

- immutable exact-dev21 runtime with `PRODLIKE_RUNTIME_VERIFY_PASS 283 86 NOT_RUN`;
- seven enabled/active user-systemd timers with bounded execution and supervised previous-result checks;
- daily safe control backup with retention 14, hash/member verification and restore/secret-scan proof;
- ACL-protected Windows NTFS second-filesystem mirror of verified control backups;
- boot/periodic recovery verification;
- ACL-protected Windows NTFS exact-runtime rebuild set bound to V21 package, wheel and manifests;
- cold-rebuild proof using only the NTFS rebuild set, reproducing `0.1.0.dev21`, 283/283 bytes, `host_ready=false`, and `86 NOT_RUN`.

These controls are non-native operational readiness only. They do not create LAB authority, qualification, SITE evidence or HOST_READY.

## Lifecycle-consistency measurement

`LEARNING-LIFECYCLE-CONSISTENCY-002` reaches its structured V36 measurement gate. The V36 candidate marks it `EFFECTIVE` with evidence across V34, V35 and V36 plus `workflow-health/HEALTH_REVIEW-DOCSYS-R9-LIFECYCLE-004.md`.

Its success metric remains guarded by exact-target review/audit and post-promotion CI: no unreviewed correction auto-promotes; lifecycle/register/project-state aggregates remain machine-consistent; historical ineffective learnings retain valid successor/meta-review paths.

## Self-learning recurrence discovered during V36

The first exact V36 design run exposed a new valid ambient state that broke one adversarial fixture: after pending measurements reached zero, `overdue_measurement_drift` no longer constructed an overdue record and the regression harness failed while the lifecycle checker correctly passed.

This evidence reclassifies `LEARNING-ADVERSARIAL-FIXTURE-ISOLATION-003` as `INEFFECTIVE` and creates successor `LEARNING-ADVERSARIAL-STATE-INDEPENDENCE-004`. The corrected fixture now constructs its own active pending-measurement record, due gate and matching pending aggregate before deliberately leaving the overdue aggregate wrong. Successor 004 is predeclared for R4/A4 activation and remains `PENDING_MEASUREMENT` with a V38 gate.

Promotion-ready V36 learning aggregates:

```yaml
LEARNED_BUT_NOT_ACTIVE_BACKLOG: 0
UNRESOLVED_INEFFECTIVE_LEARNING: 0
PENDING_EFFECTIVENESS_MEASUREMENT: 1
OVERDUE_EFFECTIVENESS_MEASUREMENT: 0
HISTORICAL_INEFFECTIVE_LEARNING: 2
```

## Review/audit contract

- `DOC-V2-R9-REVIEW-004` → `reviews/DOCUMENTATION_SYSTEM_R9_REVIEW_R4_PASS.md`
- `DOC-V2-R9-AUDIT-004` → `reviews/DOCUMENTATION_SYSTEM_R9_AUDIT_R4_PASS.md`

R4 review and A4 audit must bind one exact V36 design SHA. Promotion may then add only those two immutable verdict records to that exact tree, followed by mandatory post-promotion CI.

Canonical next action remains unchanged: resume `RUN-P00-VALIDATION-001/V02_LAB_EXECUTION_AUTHORITY`; documentation or production-like readiness cannot substitute for external LAB authority.