# OPEN_IMPLEMENTATION_ITEMS_V3

**All REM-01…08 remain OPEN at full-item scope.** Several formerly absent integration components are now authored; none of the entries below is closed merely by linking a new source file. These are unfinished implementation items, not review findings or host validation failures.

| ID | Progress in dev3 | Concrete remaining source closure condition |
|---|---|---|
| IMPL-REM-01 | Admitted observation broker, actual feature/runtime/distro/profile/volume normalization, bounded fixed guest transport and output-volume coverage connected to session | Complete passive inventory-to-plan bindings; complete observed capability/effective-profile and path-source pinning; end-to-end before/after observation cases |
| IMPL-REM-02 | One guard/fence across session; per-step refresh; actual writer/service probes; snapshot-before-terminal ordering; existing-commit replay | Complete native NOOP revalidation, diagnostic-only access under an unresolved fence, non-success SAFE_PAUSE accounting, journal capacity handling and remaining lifecycle integration |
| IMPL-REM-03 | Authenticated native bindings; per-claim external proof graph; scoped fresh receipts; Authenticode payload path; no fixtures through NativeStore | Complete action/epoch/profile proof selection across all resume paths; pre-C3 prior-guest baselines; artifact byte pinning through agent execution |
| IMPL-REM-04 | ENGINE/CREATE/ADOPT/EXPORT/IMPORT/RESTORE/lifecycle action dispatch source; guest workspace/sentinel; native actual after-state observers | Complete full-route C0-to-terminal tests, pending-servicing progression and failed/cancelled operation disposition; only then register primary active CLI |
| IMPL-REM-05 | Exact original-plan reconciliation entry under one guard; boot/user-init owner receipts; actual material replay; no retry from INTENT | Safe cancel/pause and diagnostic handling without mutating or clearing unknown original state; complete native restart/OOBE/reconciliation/resume dispatch and no-op behavior |
| IMPL-REM-06 | Source terminal sweep/history/restore linkage; separate Windows/guest network contexts; sentinels/perms; independent envelope receipts | Supported non-DIRECT proxy contexts, complete binding/profile observations, terminal/restore full integration coverage and effective-state NOOP revalidation |
| IMPL-REM-07 | Catalog E00-01…17; requiredness per stage; collector continuation; create-only protected snapshots; E16 outcomes preserved; separate E17 proposal source | Complete per-stage nested semantics and cross-stage old/new evidence binding, failure-stage capture, output-crash recovery, publication applicability checks, safe diagnostics with pending fence, full native protected I/O integration and primary CLI wiring |
| IMPL-REM-08 | 458 workspace tests, source-to-test mapping; five original native foundation paths retained | Write the full supported-route/failure executable controller harness and simulate complete native factory flows; the 86-case inventory is not sufficient |

## Managed blocking work

### IMPL-BLOCK-01 — Native lifecycle and active entry completion

Owner: current IMPLEMENTATION work item. Status: OPEN. Scope: REM-01…06.

Complete (a) C0 observation-to-binding path, (b) previously committed operation live NOOP assertions, (c) original-fence safe diagnostics/cancellation/pause/reconciliation, (d) full service/reboot/OOBE transitions and (e) source-byte pinning. Add causal workspace tests that exercise the production integration through explicit test-only API ports without invoking Windows. Keep primary active CLI blocked until these contracts and end-to-end source paths exist. Host inventory supplied by the user would not write these missing paths.

### IMPL-BLOCK-02 — Evidence pipeline completion

Owner: current IMPLEMENTATION work item. Status: OPEN. Scope: REM-07 plus relevant REM-03/06.

Complete field-level cross-stage semantics (especially pre-C3 old guest proof and SITE gate handoff), actual-context bundle applicability, capture on failure before returning, protected snapshot/publication crash handling and E17 safe handoff. Fully bind schema, collectors, authority, output and CLI behavior. Conservative UNAVAILABLE/INCOMPLETE is safe but does not count as complete source support.

### IMPL-BLOCK-03 — Harness completion

Owner: current IMPLEMENTATION work item. Status: OPEN. Scope: REM-08.

Implement each supported-route/failure controller procedure with actual expected-vs-observed assertions and fixture isolation; parameter names or an inventory cannot replace procedure source. Never manufacture qualification, code-review or owner receipts. Later authorized native execution remains separate, but writing that harness is required now before author-complete status.

## Behavioral disposition

Approved FD/D00/AC are unchanged. No waiver or redesign is introduced. The native NOOP path's named prerequisite refusal is recorded as an implementation omission, not a new approved contract. No design gap has been proved; if finishing an item actually requires changing reviewed behavior, record the exact gap and leave implementation for that scope.

## Exit remains unsatisfied

A full CODE-REVIEW-P00-001 handoff requires all full-scope source paths and test harnesses, docs, actual author regression and traceability. Missing actual Windows execution is expected at authoring, but missing code is not excused by it. Current delivery remains PARTIAL_SOURCE_DROP_DEV3.
