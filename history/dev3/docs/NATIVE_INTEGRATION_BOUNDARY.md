# Native integration boundary — dev3

## Implemented call path, not an authorization to execute

`native_session(root)` constructs real HKLM/Win32 ports only. `SessionRunner` preauthorizes, acquires one host-global guard, reads the durable fence/progress, then refreshes authority and observed context before each step. The driver rechecks profiles, principals, volumes, support/trust and exact build/test identity. An unheld permission snapshot is not accepted as live admitted observation.

`run()` dispatches exact fixed actions. `_after()` reads writer/service/registry/VHD/guest or approved external postcheck evidence. Only observed after-state and evidence may generate Completion. `observe()` captures protected source records before the coordinator writes TERMINAL and matching CLEAR. Snapshot failure leaves an unresolved intent instead of emitting a fictional success. Last-step bundle outcomes are not erased by a successful journal commit.

Bindings declare specific future generated identities at reviewed transition locations; they are never observations. Exact Windows-created IDs are persisted after observation. A raw process exit remains a native-command result, not service completion, target health, phase readiness or qualification.

## Explicitly unfinished execution surfaces

1. **Committed NOOP:** native final assertions do not yet re-establish every effective guest/content/terminal assertion on an already completed run. This path now blocks with `NATIVE_NOOP_REVALIDATION_INCOMPLETE`, rather than reporting NOOP from metadata alone. This is unfinished implementation, not a substitute approved behavior.
2. **Reconciliation:** exact original-plan authorization and successful reconciliation components exist. Native safe cancellation, non-success SAFE_PAUSE accounting, diagnostic publication while retaining the original fence, and complete restart/OOBE/resume entry wiring do not. No normal bundle command may bypass a pending fence.
3. **Observation-to-plan:** authenticated native binding consumption exists. The complete passive inventory-to-execution-binding interface and all capability/profile facts are not integrated into the primary C0/dry-run flow.
4. **Evidence:** Snapshot creation/selection and publish/assessment source exist. All stage/route-specific field semantics, prior guest baseline selection before C3, failure-stage capture, conditional applicability consistency, crash recovery of publication and full protected I/O integration tests are not complete.
5. **Native test controller:** only the original five NF-* foundation paths exist. Full supported-route and failure-injection controller automation has not been written. Having 86 rows with NOT_RUN is an inventory, not an executable harness.

These limitations keep `NATIVE_BACKEND_AVAILABLE=false` and the primary native apply/verify/support-bundle commands unavailable. No user data request, fixture switch or manual PASS receipt closes them.

## Additional source assurance limits

Fixed guest/network agent source is hash-checked against the build but needs complete handle-pinning across source reads to eliminate the remaining read/check/use surface. The append-only native journal retains its original bounded size; long-workflow capacity/fence handling needs end-to-end qualification and source-level handling before a full candidate. DIRECT-only networking does not implement approved enterprise proxy profiles. The current conservative installer-service-idle observation is not evidence that every supported servicing lifecycle will progress without deadlock.

These are explicit implementation/assurance items, not newly approved constraints on the host. Required source changes must preserve the reviewed behavior; a genuine required behavior change must create DESIGN_GAP.

## Test provenance

`test_session_integration.py` uses real orchestration/journal-frame logic with explicit synthetic ports. `test_dev3_proof_observer_integration.py` invokes real receipt/observer policy methods with synthetic graph/API data, not the production factory. `test_dev3_catalog_native_helpers.py` covers catalog/transition/command/terminal helper contracts. Native scripts and agents were not executed, including indirectly.
