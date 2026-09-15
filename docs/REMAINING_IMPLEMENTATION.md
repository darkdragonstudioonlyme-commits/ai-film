# DEV12 Remaining-Work Delta

- **REM-07 progress:** deterministic temp identity, temp/final/no-output recovery state, incomplete bundle recovery, and E17 recovery applicability are now implemented at source level.
- Temp bytes are retained protected and never auto-renamed/deleted/re-published during recovery.
- E17 remains a separate non-authoritative artifact; recovery cannot create a missing E17 intent/output or grant MASTER acceptance.
- **Still open:** reviewed non-DIRECT transport, causal 86-case controller/oracles, production-factory author integration and any residual full-scope REM closure.
- CR-P00-001 remains OPEN_BLOCKER.

---

# DEV11 Remaining-Work Delta

- `CR-P00-005`: implementation fix authored — PRE_C3 `checked_at` is bounded by current capture time.
- Dev10 prior guest/pre-C3/checkpoint provenance behavior is otherwise preserved.
- Independent REVIEW disposition is still required before CR-P00-005 can close.
- CR-P00-001/full REM scope remains open.

---

# DEV10 Remaining-Work Delta

- **REM-03/07 progress:** prior guest/pre-C3/checkpoint consumers now retain and validate exact cross-stage provenance rather than stamping historical facts as current capture.
- **REM-07 progress:** E12 pre-C3 provenance and E15 pre-C3-vs-post-apply checkpoint separation are implemented at source level.
- **Still open:** complete remaining nested/applicability semantics beyond these source selectors, incomplete/temp publication + remaining E17 integration, non-DIRECT transport, full causal 86-case harness and production-factory author integration.
- All full-item REM entries remain OPEN; CR-P00-001 remains OPEN_BLOCKER.

---

# DEV9 Remaining-Work Delta

- `CR-P00-002`: implementation fix authored — renewed authority/fence/request checks precede durable owner-wait relabel.
- `CR-P00-003`: implementation fix authored — wait cause is persisted as typed safe metadata/digest.
- `CR-P00-004`: implementation fix authored — exact per-kind wait schema plus serialized-size/privacy boundary.
- These fixes require independent REVIEW lane disposition before findings are considered closed.
- `CR-P00-001` and `IMPL-REM-01…08` remain open at full scope.

Next implementation scope after review disposition: prior pre-C3/checkpoint provenance + nested cross-stage E00 semantics.

---

# DEV8 Remaining-Work Delta

- **REM-04/05 progress:** pending reboot after a C3 process is now a durable operator wait even when the process returned exit 0; reboot reconciliation requires a changed host boot witness and cleared pending state.
- **REM-04 progress:** missing post-C3/OOBE owner evidence can remain `AWAITING_OWNER_VERIFICATION` without replaying mutation; reboot-origin owner waits preserve their reboot-boundary requirement.
- **REM-04 progress:** post-reboot completion of `ENABLE_PREREQUISITES`, `INSTALL_RUNTIME`, and `AWAIT_OWNER_RESTART` consumes affected-resource postchecks before commit.
- **Still open:** full service/OOBE/restart/resume production-factory integration across supported native profiles, approval-expiry/continuation combinations, and causal Windows/LAB execution; no native validation is claimed.
- **REM-06…08 and remaining REM-01/02/03 scope:** unchanged except where dev7/dev8 progress is explicitly noted.

Do not remove the reviewed final owner-planned restart merely because an earlier C3 step separately required reboot. Design V2/T00-05 requires planned host-restart lifecycle coverage; dev8 only prevents false continuation/commit across reboot boundaries.

---

# DEV7 Remaining-Work Delta

The full REM register remains authoritative below. Dev7 changes the progress interpretation as follows:

- **REM-01 / REM-03 progress:** Windows controller child executables and the Windows Python dependency are now required to match an authenticated exact-byte executable policy before process creation. The policy is host/build/contract scoped and reloaded on authority refresh.
- **REM-01 progress:** effective-profile mismatch now fails inside the native driver before a Refresh can be consumed.
- **Still open under REM-03:** guest-side interpreter/rootfs dependency provenance and any remaining bootstrap/dependency trust chain not represented by Windows executable policy.
- **Still open under REM-04/05:** remaining service/OOBE/restart/resume/multi-stage factory behavior.
- **REM-06…08:** unchanged at full-item scope.

Do not mark REM-01 or REM-03 CLOSED solely because the executable policy exists; their broader closure criteria remain.

---

# OPEN_IMPLEMENTATION_ITEMS_V6

Full-item statuses below remain **OPEN**. Completed subcomponents are not described as absent; none is promoted to CODE_REVIEW_PASS or native evidence. All remaining source is owned by IMPL-P00-001.

| ID | Source progress through dev6 | Remaining full-item closure |
|---|---|---|
| IMPL-REM-01 | Native observations plus protected C0 capture and observation-to-proposal binding | Complete effective-profile/eligibility integration across supported contexts, full native factory route flows |
| IMPL-REM-02 | Native single guard, durable fence/read set, original-request recovery, logical/physical journal byte checks before reads | Full source integration/fault procedures at journal exhaustion, interrupted readers and lifecycle boundaries; no implicit journal reset |
| IMPL-REM-03 | Exact source scripts, native trust/proof graph, per-entry/per-step authorization; pinned execution and selection records | Full bootstrap/executable/dependency byte-trust integration; current/previous source epochs and prior-guest/pre-C3 proof selection |
| IMPL-REM-04 | Primary native CLI now registered to concrete factory; service/reboot preconditions; first-user wait vs actual receipt | Complete factory execution-path author tests and remaining service/OOBE/restart/resume interaction branches; not only constructor/routing tests |
| IMPL-REM-05 | Both original mutation-fence recovery and pre-mutation detached-read recovery; safe non-success cancellation/pause and committed live NOOP | Complete prolonged/multi-stage resume, later request boundaries and remaining recovery/publication interactions |
| IMPL-REM-06 | Current guest/content/assets/terminal readers and native source proof consumers | Non-DIRECT transport contexts; full effective-profile/terminal/restore context integration and causal native harness assertions |
| IMPL-REM-07 | Immutable snapshot stage, field checks, failed capture hook, publication intent/readback recovery, primary support entry | Full nested field semantics, prior guest/C3 provenance, failure-before-snapshot capture, temp/partial output and E17 crash recovery/applicability |
| IMPL-REM-08 | Existing foundations plus new registered-LAB route controller, route oracles, expanded author regression | Full supported-route/failure scenario preparations/controllers and per-T/F/subcase oracles; end-to-end production factory integration tests |

## IMPL-BLOCK-01 — Remaining native integration

OPEN, REM-01…06. C0 capture-to-binding and no-mutation-fence recovery entry now exist; do not repeat them as wholly missing. Primary active CLI is wired, but not all reviewed route/environment/recovery behavior is complete. Finish effective profile, interpreter/executable trust, service/OOBE/restart/multi-stage recovery and their production factory integration. Supported non-DIRECT transport remains an explicit unimplemented adapter path, not an approved waiver of networking acceptance.

## IMPL-BLOCK-02 — Remaining evidence/recovery semantics

OPEN, REM-03/06/07. Prior-guest selection now consumes exact hash-linked operation observations from the current/history source graph, but full nested semantics and prior pre-C3/checkpoint selection remain unfinished. Snapshot stage binding and archive re-observation are implemented. dev6 also adds a bounded protected early-failure capsule before the first usable snapshot and write-ahead/read-only recovery for the separate E17 proposal. These do not finish all nested semantics, prior pre-C3/checkpoint selection, incomplete/temp bundle-output recovery, or every recovery-path integration. No code may turn an intended output hash, a preserved file, or a PASS envelope into eligibility. Snapshot formats missing new stage context are rejected rather than inferred from status; no native legacy capture has been claimed to exist.

## IMPL-BLOCK-03 — Full failure/controller harness

OPEN, REM-08. `run_native_route_tests.py` now drives registered native route entry and verifies journal-based outcomes. It is a real controller contribution, not a mere inventory, but it is **not** the full failure suite. It does not provision every causal environment fault, coordinate every cross-principal/concurrency/restore-isolation scenario, or evaluate every one of the 86 normative entries. Existing five foundation procedures and route summaries do not close that gap.

## Source vs execution

These are outstanding implementation/integration tasks, not requests for user-supplied host inventory. Native execution is correctly deferred to authorized gates, but source closure cannot be deferred under the name of missing evidence. No DESIGN_GAP has been established; approved contracts remain unchanged.
