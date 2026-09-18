# VALIDATION PRODLIKE USER-SYSTEMD RECOVERY — AUDIT 001 PASS

```yaml
AUDIT_ID: VALIDATION-PRODLIKE-SYSTEMD-RECOVERY-AUDIT-001
TARGET_DESIGN_COMMIT: 190cf242f5834e8abac2de2a627d4e9acac21e9b
REQUIRED_REVIEW_COMMIT: 9d5eab9baeb3994c08453a7452ea1f146af7e9a2
BASE_VALIDATION_HEAD: 5edb3f65ddd369321c6a5a4286a8fa5027494a18
DESIGN_CI_RUN: 35307665127
DESIGN_CI_JOB: 105483072905
REVIEW_CI_RUN: 35307714342
REVIEW_CI_JOB: 105483213837
VERDICT: PASS
OPEN_FINDINGS: []
PRODUCT_SOURCE_CHANGED: false
NATIVE_EXECUTION_ADVANCED: false
```

## Holistic audit

1. The incident is a real supervision-deployment loss on the live prodlike host, not a source/runtime candidate mutation. Exact dev21 product, package, test and contract identities remain unchanged.
2. Verified source backup `control-state-20260918T041624Z.tar.gz` SHA `ab2ddc7fab3693a7b0c101cc2dd8f7435b9a369b9d1b441f61611fec535e3210` contained 91 manifest-bound files including 46 systemd unit/drop-in files, eleven service/timer pairs and no native authority/protected identity payload.
3. Every archive member and all sixteen live runtime control scripts matched expected hashes before recovery.
4. The first restore attempt copied exact bytes to system scope, but no timer was activated. The first service execution failed because root identity violated the runtime writability invariant; direct root verification returned `APP_WRITABLE_DRIFT` while user `dragon` verification PASSed. All `/etc/systemd/system` AI-FILM files and enable symlinks were then removed and daemon state reloaded before correct activation.
5. Correct recovery used the lingering `dragon` user manager (`Linger=yes`) and restored exact files under `/home/dragon/.config/systemd/user`. All 46 files matched archive-manifest hashes and `systemd-analyze --user verify` PASSed.
6. All eleven user timers are enabled/active. Ten non-health periodic services returned success, followed by runtime-health success with every check true, V02 `BLOCKED / APPROVAL_ENVELOPE_MISSING`, READY absent and `native_execution_started=false`.
7. Postrestore evidence is fresh and internally consistent: health SHA `b2fa7347c966c8b85e781ae88931f87c331426f27492f9bb39cdc290b50d5cf5`; 93-file control backup SHA `1d7e7ef0e37791c789940e2f3715c789fbb741271db75893ebc238fd69fdbfa9`; offhost export SHA `cec3339223a1d3965ba14bfcb22749560b2f3f68d565522631566d7ca5891a5c`.
8. `verify_prodlike_user_systemd.py` provides durable machine binding from portable backup manifest to archive members, deployed user-unit bytes and optional live timer enabled/active states. Its five-case regression covers missing/drifted units/drop-ins and archive tamper.
9. Exact design server run `35307665127` / job `105483072905` passes the new regression plus all prior V02 authenticity, byte-integrity, watcher, pre-V03, manifest and exact-source hardened-validator checks.
10. Review commit `9d5eab9...` adds only its immutable review record; review run `35307714342` / job `105483213837` repeats the full suite successfully.
11. Validation CI branch/path filters now include prodlike design/review/audit evidence, preventing future recovery verdict commits from silently skipping server checks.
12. The operations runbook now defines user-systemd scope as a hard invariant and forbids reconstructing unit text from prose, weakening hashes, or installing the supervision layer as root/system services.
13. V02 external authenticity/authority remains unchanged. Approval envelope/signature and HKLM trust remain absent, LAB stays stopped, policy/READY remain absent, and all 86 native cases remain NOT_RUN.
14. Review-to-audit adds only this audit record. Any semantic tooling/state/runbook change after review requires reopened review/audit.

## Result

Holistic PASS. `lane/validation-p00` may fast-forward to this audited chain only if its current head remains `5edb3f65ddd369321c6a5a4286a8fa5027494a18`, followed by mandatory canonical-lane Validation V02 Tooling CI and a live post-promotion user-systemd/V02 boundary recheck.
