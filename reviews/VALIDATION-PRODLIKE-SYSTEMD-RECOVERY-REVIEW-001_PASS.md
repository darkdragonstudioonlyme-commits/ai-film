# VALIDATION PRODLIKE USER-SYSTEMD RECOVERY — REVIEW 001 PASS

```yaml
REVIEW_ID: VALIDATION-PRODLIKE-SYSTEMD-RECOVERY-REVIEW-001
TARGET_DESIGN_COMMIT: 190cf242f5834e8abac2de2a627d4e9acac21e9b
BASE_VALIDATION_HEAD: 5edb3f65ddd369321c6a5a4286a8fa5027494a18
DESIGN_BRANCH: lane/validation-p00-prodlike-user-systemd-recovery
DESIGN_CI_RUN: 35307665127
DESIGN_CI_JOB: 105483072905
VERDICT: PASS
OPEN_FINDINGS: []
PRODUCT_SOURCE_CHANGED: false
NATIVE_EXECUTION_ADVANCED: false
```

## Independent review

1. The incident is real current-host operational drift, not historical prose drift: all eleven documented user-systemd timers were absent while exact dev21 runtime/control bytes, V02 tooling, verified backups and offhost export remained intact.
2. Verified source backup `control-state-20260918T041624Z.tar.gz` SHA `ab2ddc7fab3693a7b0c101cc2dd8f7435b9a369b9d1b441f61611fec535e3210` contains 91 manifest-bound files including 46 systemd unit/drop-in files and eleven timer definitions. All archive members and all 16 live runtime control scripts matched expected hashes.
3. The first recovery copy used system scope and was stopped before timer activation. Exact `verify-runtime` succeeds as `dragon` and intentionally returns `APP_WRITABLE_DRIFT` as root; this, together with `systemd_user_linger=true`, proves the supervision layer belongs to the lingering user manager. System-scope files and enable symlinks were fully rolled back.
4. Final recovery restored 46 exact files to `/home/dragon/.config/systemd/user`, passed byte-for-byte postinstall verification and `systemd-analyze --user verify`, and attached to `/run/user/1000/bus` with `Linger=yes`.
5. Eleven timers are enabled/active. Ten non-health periodic oneshots returned `Result=success / ExecMainStatus=0`; runtime-health then returned success with every check true, `authority_status=BLOCKED`, reason `APPROVAL_ENVELOPE_MISSING`, READY absent and `native_execution_started=false`.
6. Fresh postrestore health SHA is `b2fa7347c966c8b85e781ae88931f87c331426f27492f9bb39cdc290b50d5cf5`; postrestore 93-file control backup SHA is `1d7e7ef0e37791c789940e2f3715c789fbb741271db75893ebc238fd69fdbfa9`; refreshed offhost export SHA is `cec3339223a1d3965ba14bfcb22749560b2f3f68d565522631566d7ca5891a5c`.
7. New `verify_prodlike_user_systemd.py` machine-binds control-backup manifest → archive members → deployed user-unit bytes and optionally all timer enabled/active states. Live execution against the postrestore backup passed with 46 files / 11 timers / native=false.
8. Its portable regression passes five cases: valid deployment, missing unit, content drift, missing drop-in and archive-member drift. Design server run `35307665127` / job `105483072905` executes this regression plus all prior V02 tooling and exact-source authority tests successfully.
9. Workflow branch/path filters now cover prodlike design/review/audit artifacts so verdict-only follow-up commits cannot silently skip server validation.
10. Runbook explicitly forbids `/etc/systemd/system` recovery for these units and requires user-scope manifest verification plus runtime-health PASS after real service execution.
11. Design diff changes only validation operational evidence/tooling/workflow. Accepted dev21 source/package/test/contract identities are unchanged; all 86 native cases remain NOT_RUN; V02 remains BLOCKED and LAB remains stopped.

## Result

PASS for exact design `190cf242f5834e8abac2de2a627d4e9acac21e9b`. Audit may add only an immutable audit record before canonical validation-lane fast-forward consideration.
