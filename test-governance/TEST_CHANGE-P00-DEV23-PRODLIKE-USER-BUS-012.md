# TEST_CHANGE — dev23 prodlike user-systemd bus and timer-state semantics 012

~~~yaml
TEST_CHANGE_ID: TEST_CHANGE-P00-DEV23-PRODLIKE-USER-BUS-012
RUN_ID: RUN-P00-VALIDATION-002
WORK_ITEM: TEST-DESIGN-P00-DEV23-PRODLIKE-USER-BUS-012
BASE_VALIDATION_COMMIT: ae167ce4af9180fd7e239b4b83cfddc9ade061b5
TARGET_EXECUTOR_BASE: 7bb931254d61823af616ac52ba624cbede25312a
TARGET_RECEIPT_REVIEW: reviews/CODE-REVIEW-P00-DEV23-PRODLIKE-DEPLOYMENT-RECEIPT-001.md
TARGET_RECEIPT_SHA256: fcb3b059634e41cf08dc61ec39c80d5dc93250e735ab2d795afbd67583ddabfd
PREDECESSOR_TEST_CHANGE: TEST_CHANGE-P00-DEV23-PRODLIKE-LAB-DEPLOYMENT-011
PREDECESSOR_TEST_REVIEW: TEST_REVIEW-P00-DEV23-PRODLIKE-LAB-DEPLOYMENT-011
ORACLE_CHANGED: false
EXPECTED_BUSINESS_BEHAVIOR_CHANGED: false
REAL_EXECUTION_AUTHORIZED: false
PRODLIKE_RETRY_AUTHORIZED: false
LAB_MUTATION_AUTHORIZED: false
NATIVE_EXECUTION_AUTHORIZED: false
AUTHORITY_SIGNING_AUTHORIZED: false
HKLM_MUTATION_AUTHORIZED: false
STATUS: PENDING_NON_AUTHOR_TEST_REVIEW
~~~

## Cause and invariant

Attempt 1 consumed its immutable authorization and ended `RECONCILE_REQUIRED`. The reviewed production runner omitted `XDG_RUNTIME_DIR` and `DBUS_SESSION_BUS_ADDRESS`; `systemctl --user` therefore returned rc=1 / empty stdout / `Failed to connect to bus: No medium found`. `capture_timer_state` allowed rc 1/3/4 and reduced empty output to `enabled=false, active=false`, creating false state evidence before the first quiesce command failed.

Read-only reconciliation found current still dev22, backed-up control bytes unchanged, staged dev23 exact, and all eleven timers enabled+active when queried through the actual `/run/user/1000` user bus. The consumed receipt remains authoritative and must never be replayed.

## Authorized correction scope

MODIFY only:
- `validation/tooling/deployment_transaction_common.py`
- `validation/tooling/deploy_prodlike_candidate-v2.py`
- `validation/tooling/tests/test_prodlike_deployment_transaction_v2.py`

`rebuild_lab_candidate-v2.py`, its tests, historical dev22 tooling, product source, candidate binding/package, test/oracle contracts and all native/signing/HKLM tooling remain byte-identical. Any need to widen this scope reopens TEST_REVIEW.

## Required coverage

- `TV012-01` — a pure user-bus environment helper derives `/run/user/<uid>` and its `bus` socket from the executing UID, validates the runtime directory is an owned directory with no group/world write and the bus is an owned Unix socket, then adds only exact `XDG_RUNTIME_DIR` and `DBUS_SESSION_BUS_ADDRESS` values to the constrained runner environment.
- `TV012-02` — missing, wrong-owner, non-directory, writable runtime directory, missing bus, non-socket bus, or wrong-owner bus fails closed. Tests use temporary directories/Unix sockets; they must not depend on the live user session.
- `TV012-03` — `SubprocessRunner` remains minimal by default. Prodlike `main()` explicitly opts into validated user-bus environment; LAB executor/default command paths do not acquire that capability implicitly.
- `TV012-04` — `capture_timer_state` accepts only semantically recognized non-empty `systemctl is-enabled` and `is-active` outputs. Empty stdout, `unknown`, connectivity text on stderr, or an unrecognized state is not a disabled/inactive observation and must raise before mutation.
- `TV012-05` — valid enabled+active and disabled/inactive timer states remain representable and deterministic; stored raw values match the observed systemctl state.
- `TV012-06` — an unavailable user bus or semantically invalid timer observation during transaction capture yields durable `FAILED_PREMUTATION` with `mutation_started=false`; release staging/current/control mutation must not occur.
- `TV012-07` — the consumed attempt-1 `RECONCILE_REQUIRED` receipt is never reused/replayed as an executable attempt. A later attempt requires a new transaction id, new immutable authorization hash and separate receipt root.
- `TV012-08` — the exact already-staged dev23 release may be recognized as an exact existing target by a later reviewed transaction; any byte/mode/symlink drift still fails closed. This test does not authorize cleanup or execution.
- `TV012-09` — all TV011 transaction/fault-injection tests, TV010 reconciliation tooling tests, TV009 tooling tests and 11 historical dev22 scripts remain green. The correction must not weaken command/mutation-root hardcuts or one-attempt semantics.
- `TV012-10` — tests and correction never grant LAB/native/signing/HKLM/SITE/qualification/HOST_READY authority and never perform real prodlike mutation.

## Evidence discipline

Host read-only reconciliation is evidence about the observed post-attempt state, not proof that Claude executed commands and not permission to rewrite the receipt. A test may use fake runners and synthetic Unix sockets; no real user-systemd mutation is permitted during author/review tests.

## Exit gate

Independent TEST_REVIEW must confirm all ten TV012 obligations, `ORACLE_CHANGED=false`, the exact three-file MODIFY scope, and predecessor TV011 coverage retention. Only PASS authorizes implementation correction. A corrected executor still requires CODE_REVIEW, a **new** prodlike authorization capsule/review and one new foreground attempt; the consumed authorization remains permanently non-replayable.
