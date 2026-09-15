# IMPL-P00-001 Implementation Status — dev12 increment

`0.1.0.dev12 / PARTIAL_SOURCE_DROP_DEV12`

Dev12 advances REM-07 publication/E17 recovery semantics without changing approved contracts.

- E16 and E17 publishers derive an exact deterministic protected staging path before write and bind staging + final identity in the write-ahead journal intent.
- Filesystem publication is create-only temp → write-through move with no replace. The publisher no longer invents an unjournaled random temp path.
- Recovery is read-only: final-only exact bytes may be re-observed; temp-only exact bytes are recorded as retained failure and remain exit18; final+temp is drift/ambiguity; missing output remains failure.
- Non-publishable/no-archive E16 outcomes (15/22/23) now have a durable write-ahead decision and can be recovered only when no unexpected final output exists.
- GATE_HANDOFF reconciliation requires an E17 intent when the recovered E16 component is eligible, recovers exact existing E17 bytes, and rejects assessment intent when E17 is not applicable.
- E17 remains a PROPOSAL with `accepted_by_master=false` and `host_ready=false`.
- Added focused crash/applicability/tamper/duplicate staging tests.

Final author evidence: **728 PASS / 0 failure/error/skip**, static **95 PASS**. Native Windows/WSL/LAB/SITE remains NOT_RUN. Overall CODE_REVIEW remains blocked by CR-P00-001/full REM scope.

---

# IMPL-P00-001 Implementation Status — dev11 increment

`0.1.0.dev11 / PARTIAL_SOURCE_DROP_DEV11`

Dev11 is the focused remediation for REVIEW finding CR-P00-005. PRE_C3 historical events must now be observed no later than the current evidence-capture/context time. No TTL or arbitrary freshness window was introduced.

Final author evidence: **711 PASS / 0 failure/error/skip**, static **94 PASS**. Native Windows/WSL/LAB/SITE remains NOT_RUN.

---

# IMPL-P00-001 Implementation Status — dev10 increment

`0.1.0.dev10 / PARTIAL_SOURCE_DROP_DEV10`

Dev10 advances REM-03/07 cross-stage evidence semantics without changing reviewed contracts.

- Prior guest facts selected from exact current/history plans now bind host, execution class, target registration, timestamp and content-addressed journal provenance.
- E04/E05/E07 cells sourced from prior guest evidence retain the original `source_ref`, `observed_at`, and `source_kind` instead of being relabeled as current capture.
- PRE_C3 events are selected only from exact current/host-restart C3 plans, boundary-hash checked, deduplicated, and their protection receipts revalidated at recorded time under current trust/withdrawal state.
- E12 stores validated nested pre-C3 provenance and owner/proof linkage.
- E15 separates CPK-PRE-C3 protection refs from the post-apply committed RESTORE_EXPORT checkpoint provenance.
- Added 18 focused prior/nested provenance tests.

Final author evidence: **710 PASS / 0 failure/error/skip**, static **94 PASS**. Native Windows/WSL/LAB/SITE remains NOT_RUN; overall CODE_REVIEW remains blocked by CR-P00-001/full REM scope.

---

# IMPL-P00-001 Implementation Status — dev9 increment

`0.1.0.dev9 / PARTIAL_SOURCE_DROP_DEV9`

Dev9 is a focused PATCH-like implementation increment performed in IMPLEMENTATION after the early dev8 CODE_REVIEW FAIL. It closes CR-P00-002/003/004 in source/tests; CR-P00-001 remains open because the overall work item is not author-complete.

- Owner-verification relabel after recovery observation now performs renewed authority, generation, actor/request and fence checks immediately before the durable transition.
- Session/legacy engine operator waits now persist a typed safe projection instead of only the derived state.
- Wait metadata has an exact schema, 1024-byte canonical cap, fixed reboot-indicator keys, digest references, and no raw process/owner output.
- Reboot-origin owner-verification retains only the digest of the previous wait observation.
- Added 9 focused review-finding regression tests.

Final author evidence: **692 PASS / 0 failure/error/skip**, static **93 PASS**. Windows/WSL/LAB/SITE native execution remains **NOT_RUN**. CODE_REVIEW_PASS remains false.

---

# IMPL-P00-001 Implementation Status — dev8 increment

## Current verified author candidate

`0.1.0.dev8 / PARTIAL_SOURCE_DROP_DEV8`

Dev8 hardens reviewed service/reboot/OOBE/reconciliation behavior without changing Phase00 operations or public contracts.

### Added in dev8

- `native/lifecycle.py`: pure classification of observed C3 pending-reboot state and actual reboot-resume boundaries.
- Native `ENABLE_PREREQUISITES` / `INSTALL_RUNTIME`: exit 0 no longer implies the step may continue when Windows reports a pending reboot; the original fence becomes `AWAITING_REBOOT`. Native exit 3010 remains an explicit reboot wait.
- Reconciliation of a reboot-wait requires a different host boot witness and cleared pending-reboot indicators before the original step can commit.
- When a C3 action is completed only after reboot, affected-resource post-C3 owner checks are consumed before terminal commit.
- Missing owner postcondition evidence on an existing operator-wait fence returns/retains `AWAITING_OWNER_VERIFICATION/20`; it does not replay the mutation or relabel the step successful.
- OOBE owner-verification waits remain distinct from reboot waits; they do not invent a host-reboot requirement.
- Added 10 focused lifecycle author tests.

### Author evidence

- Workspace regression: **683 PASS / 0 failure / 0 error / 0 skip**.
- Static author checks: **92 PASS / 0 fail**.
- Source content digest: `e793fc78d622c987343d1b5e5d3909cb4c19d7b0bcbafbc32909f137a1894c08`.
- Test content digest: `f91b422b6ce4ffeee9fc516bff0dc00c8e4a6216ae98e94b977ac2ef00949021`.
- Windows/WSL/LAB/SITE native execution: **NOT_RUN**.
- Code review: **NOT_PERFORMED**.
- HOST_READY: **NOT_EVALUATED**.

### Boundaries

The reviewed final `AWAIT_OWNER_RESTART` operation remains in ENGINE/HOST_RESTART plans. Dev8 does not remove or coalesce that planned owner restart. Remaining service/OOBE/restart/resume/factory and native causal coverage is still OPEN under REM-04/05/08.

# IMPL-P00-001 Implementation Status — dev7 increment

## Current verified author candidate

`0.1.0.dev7 / PARTIAL_SOURCE_DROP_DEV7`

This increment closes the **Windows child executable exact-byte trust boundary** and hardens effective-profile delivery inside the native driver. It does not close the full work item and does not authorize native Windows/WSL execution.

### Added in dev7

- `native/executable_trust.py`: authenticated site/build-scoped executable policy loaded from `NativeStore`; exact path/size/SHA-256 required; duplicate aliases and untrusted policy scope fail closed.
- `WindowsPaths.pinned_executable`: administrator-owned, non-operator-writable file boundary plus exact byte hashing while handles remain pinned.
- `NativeSupervisor`: production mode now requires an executable-trust adapter before `CreateProcess`; trusted executable policy/hash/size/kind are written into the durable native witness.
- `native_session`: production supervisor constructed with executable trust mandatory.
- Native binding now requires `executable_policy_ref`; authority refresh reloads the exact policy on every refresh/step instead of carrying path-only trust forward.
- Effective profile is explicitly checked inside `NativeDriver.refresh` and exported as `profile_verified=True`; a direct native consumer cannot receive a Refresh object whose observed effective profile differs from the reviewed plan profile.
- Added 7 focused author tests for policy scope, duplicate aliases, unlisted binaries, dependency entries, fail-before-process behavior, and witness binding.

### Author evidence

- Workspace regression: **673 PASS / 0 failure / 0 error / 0 skip**.
- Static author checks: **90 PASS / 0 fail**.
- Source content digest: `93e28ed77c132ad032cf8bf951e7d51627f6f8d007aa4179bb5696f0d6f1c6e8`.
- Test content digest: `1c79354e63bdc76de157621547a7f92eb97d98fa90a6e53856619861103a3799`.
- Windows/WSL/LAB/SITE native execution: **NOT_RUN**.
- Code review: **NOT_PERFORMED**.
- HOST_READY: **NOT_EVALUATED**.

### Remaining

`IMPL-REM-01…08` remain OPEN at full-item scope. In particular, dev7 does **not** claim guest interpreter/rootfs dependency proof, remaining service/OOBE/restart/resume interactions, prior pre-C3/checkpoint nested E00 closure, non-DIRECT transport, or the complete causal 86-case controller suite.

---

# IMPLEMENTATION_STATUS — dev6

**PARTIAL_SOURCE_DROP_DEV6. AUTHOR_COMPLETE=false. CODE_REVIEW_HANDOFF_READY=false.**

## Actual source increment

| Area | Source now present | Remaining source boundary |
|---|---|---|
| E17 publication/recovery | Write-ahead assessment intent; create-only proposal; exact existing-byte recovery; non-authoritative result | Full interrupted assessment integration across every recovery path and later MASTER acceptance remains outside implementation authority |
| Prior guest/C3 provenance | Exact current/history plan graph; hash-linked `OPERATION_AFTER_OBSERVED` selection; unrelated/tampered/ambiguous evidence rejected | Complete cross-stage nested semantics, prior pre-C3/checkpoint selectors and full restore/terminal integration remain open |
| Failure before first snapshot | Protected `EARLY_FAILURE_CAPTURED` journal capsule after durable fence without fabricated E00 facts | Full causal failure harness and downstream bundle inclusion/diagnostics for every early-failure class remain open |
| Existing dev5 functionality | C0 capture/binding, original-read recovery, native CLI dispatch, publication readback, session/recovery/noop components remain | IMPL-REM-01…08 are not closed by this revision |

## Actual author results

- Workspace regression: **666 PASS**, 0 failure/error/skip.
- Static author checks: **88 PASS**, no failed static check.
- Native Windows/WSL/LAB/SITE, PowerShell and guest/network execution: **NOT_RUN**.
- AC00-01…08: NOT_EVALUATED. Native inventory T/F/subcases: NOT_RUN.

No design change, code-review verdict, qualification or HOST_READY is claimed.
