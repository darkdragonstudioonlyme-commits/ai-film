# OPEN_IMPLEMENTATION_ITEMS_V2

Work item: IMPL-P00-001. Revision: dev2 / implementation package V2.

**All eight items remain OPEN with partial source progress.** These are implementation blockers, not code-review findings, design waivers or evidence of an infeasible design. Full-scope code-review handoff remains NOT_READY.

| ID | Area | Source now authored | Still blocks full completion |
|---|---|---|---|
| IMPL-REM-01 | Native identity/observations/path/ACL | Win32 ABI, token/elevation/AMD64, fixed registry queries, same-principal distro inventory, handle-pinned path and volume reads; fixed HOST/FEATURES/AUTHENTICODE and guest read-only collector source. | Full observation-to-binding normalization, supported-version/capability verification, physical-volume allocation integration, qualified active discovery and startup/quiesce assessment are not integrated. |
| IMPL-REM-02 | Guard/fence/native process lifecycle | Fixed Global mutex with actual handle ACL check; fixed ProgramData journal; flushed append-only hash chain, root identity and no-op initialization; suspended process/job/witness/resume ordering; unresolved native mutex held until controller exit. | All active entrypoints must still share a concrete session lifecycle; service writers, native terminal observation and crashed-controller reconciliation are not integrated. No cross-SID Windows execution evidence. |
| IMPL-REM-03 | Authority/payload/qualification | Read-only HKLM ACL-checked anchor, exact-role/digest/withdrawal reader; actual uppercase design approval normalization; release metadata graph; metadata initialization authority; exact source/test content checks. | Full E00 proof adapters, observed Authenticode-to-payload binding, selection/renewal of authority per active step and target runtime binding still need integration. The adapter does not establish real trust by itself. |
| IMPL-REM-04 | Provisioning/restore actuators | NativeActuator source invokes NativeSupervisor for ENABLE_PREREQUISITES, INSTALL_RUNTIME, INSTALL_DISTRO, EXPORT_CHECKPOINT, IMPORT_NEW_CLONE and STOP_RETAIN_CLONE. Exact argument vectors, pinned payload handles, no automatic reboot/unregister. | No complete ENGINE/CREATE/ADOPT/RESTORE route driver, workspace/OOBE adapter or service-level completion verification. Native process completion deliberately returns postconditions=false; native CLI apply stays disabled. |
| IMPL-REM-05 | Resume/reconciliation | New read-only reconciliation authority links to immutable original plan/fence without rewriting hash or purpose; committed-step reconstruction requires terminal + matching CLEAR frames. | No end-to-end native resume dispatcher, per-step live drift/authority renewal, restart/OOBE continuation or owner-authorized post-C3 orchestration. Missing binder in dev1 is now authored, but the whole lifecycle is not complete. |
| IMPL-REM-06 | Live assertions/terminal/restore envelope | Fixed host/guest collector source, bounded DIRECT HTTPS transport and testable retry/redirect handling; existing terminal/protection/isolation predicates retained. | Guest transport execution, supported proxy integration, sentinel/perms operations, independent envelope/controller proof, lifecycle runner and complete terminal sweep remain unimplemented/unwired. Live network and native collectors were not executed. |
| IMPL-REM-07 | Evidence/support bundle | Native handle-backed protected snapshot reader verifies access, bytes/hash and exact record refs; separate strict safe-summary scanner; native create-only atomic publisher normalizes output failure. | All E00-01…17 field-level catalogs, conditional requiredness, individual collector continuation, source of trusted snapshot index, full stage assembly, E17 seal and CLI support-bundle remain incomplete. Envelope schemas are not a complete evidence schema implementation. |
| IMPL-REM-08 | Harness/traceability | Executable registered-LAB foundation harness with 5 named paths; source/test identity; native API fakes, transport fakes, replay and negative author tests; AC/T/F maps and expanded-case inventory retained. | Foundation cases do not implement the full 86-entry native acceptance/failure inventory; controller automation, native route fixtures and remaining integration tests are missing. Actual native execution still requires later gates. |

## Next integration boundary

Write the concrete native session driver that consumes actual observations and authenticated raw proofs, obtains exactly one global admission, checks the durable fence, re-reads trust/identity/capacity before each approved step, dispatches the existing actuator, and obtains route-specific native/service postconditions before terminal or safe-pause. Only then register active CLI interfaces. A process-exit value, trusted document flag, marker, fixture or synthetic context cannot substitute for these postconditions.

After the session driver, implement E00 field catalogs/conditional collectors/publisher and E17; then complete native route/failure harnesses. Keep the existing 86 acceptance entries NOT_RUN until actual authorized executions.

## Specific omissions not to hide

The six native actuator action names are not six completed routes. `CREATE_WORKSPACE`, first-login/OOBE, real guest sentinel/perms, phase handoff and all supported route postconditions are not supplied by the command compiler.

The HKLM reader authenticates a policy location/digest/role chain; it does not establish ownership of a host, create real approvals, obtain an external lab attestation or validate every underlying evidence claim. A metadata status `authenticated=true` is only acceptable when its raw signed/owner-authorized proof chain has been independently established; that broader proof integration is unfinished.

DIRECT HTTPS is only one transport. Non-DIRECT contexts block instead of silently bypassing proxy policy. No proxy capability has been removed from the approved acceptance contract.

`SnapshotReader` is a component, not a completed optional-collector continuation pipeline. The separate safe scanner conservatively rejects unknown structures; it is not a universal secret detector.

No actual Windows behavior, ACL enforcement, process tree, TLS, service completion, restore isolation or cross-SID exclusion has been validated by the author workspace suite.

## Design-gap rule

No DESIGN_GAP is established from the current omissions. If completing a remaining item requires changing FD/D00/AC/public behavior, open a DESIGN_GAP with evidence and exit IMPLEMENTATION for the affected scope. Do not remove an item merely because the code currently returns a blocking result.
