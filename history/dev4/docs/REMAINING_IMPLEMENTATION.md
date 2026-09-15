# OPEN_IMPLEMENTATION_ITEMS_V4

**All REM-01…08 remain OPEN at full-item scope.** Subcomponent source completion is described below without claiming end-to-end completion. These are unfinished implementation items, not review findings and not missing user-supplied host facts.

| ID | Concrete source progress through dev4 | Remaining source closure condition |
|---|---|---|
| IMPL-REM-01 | Native observations, guest transport, source-member pinning and volume normalization | Complete passive C0 observation-to-binding, capability/effective-profile normalization, full actual-context route integration |
| IMPL-REM-02 | One guard/fence; non-success SAFE_PAUSE journal accounting; live revalidation fence; unresolved detached reads block admission | Complete recovery entry for interrupted C0 reads without an original mutation fence; full lifecycle admission/public CLI; journal capacity handling |
| IMPL-REM-03 | Native trusted bindings/proof graph, original-fence intent pinning, current revocation proof, reviewed script-member bytes | Complete cross-stage action/epoch/profile proof selection and pre-C3 prior-guest bindings; full executable/bootstrap/dependency byte trust integration |
| IMPL-REM-04 | Native actuation and observers; revalidation reads do not replay installs/workspace/lifecycle; completion requires observed after-state | Complete C0-to-terminal production factory integration tests, pending-servicing/first-user/OOBE flows and primary active CLI |
| IMPL-REM-05 | Original-fence diagnostics, authenticated safe pause/cancel, reconciliation, detached writer checking; exact original progress preserved | Complete original-request recovery entry when no mutation fence exists, native restart/OOBE and post-pause full resume dispatch; full route integration |
| IMPL-REM-06 | Terminal/history/content/restore source; current guest/asset revalidation and current owner postchecks | Supported non-DIRECT contexts, full effective profile/terminal/restore integration and actual context proof binding |
| IMPL-REM-07 | E00 catalog/pipeline source, bounded protected diagnostic records and revalidation snapshots; return-code preservation | Finish cross-stage nested semantics, failure-stage capture, publication crash recovery, applicability, E17 safe handoff and primary support CLI |
| IMPL-REM-08 | 534 workspace tests, including 76 new recovery/NOOP/pinning/journal cases | Write full executable supported-route/failure controller procedures and factory integration tests; five foundations and 86 inventory rows do not satisfy this |

## IMPL-BLOCK-01 — Native lifecycle/entry completion

Owner: IMPL-P00-001. Status: OPEN. Scope: REM-01…06.

Complete C0 observation-to-binding and registered primary entry. The original-fence recovery and live-NOOP components now exist; they must not remain described as wholly absent. However, an interrupted detached read **before any original mutation fence exists** can block subsequent admission, and a complete authorized original-request recovery entry for that case is still missing. Native journal capacity planning, pending-servicing/first-user/OOBE/resume paths, complete source/authority pipeline and production factory end-to-end author tests remain.

The existing native CLI refusal is a visible source blocker, not an approved substitute for the supported behavior. No user inventory or additional permission writes these paths.

## IMPL-BLOCK-02 — Evidence pipeline completion

Owner: IMPL-P00-001. Status: OPEN. Scope: REM-07 and relevant REM-03/06.

Complete nested field semantics and prior-guest/pre-C3/current-epoch proof selection. Finish failure-before-return capture, publication crash recovery, applicability rules and E17 safe handoff. Bind collectors, source, authority, output and CLI. A working diagnostic journal or snapshot writer is not a full support-bundle implementation. Conservative INCOMPLETE/UNAVAILABLE remains a safety behavior, not completion of missing source.

## IMPL-BLOCK-03 — Harness completion

Owner: IMPL-P00-001. Status: OPEN. Scope: REM-08.

Implement each supported route/failure controller procedure with isolated fixture preparation, causal expected-vs-observed assertions and bounded recovery. Add complete native factory integration through explicit author-test ports without native execution. Do not manufacture review/owner/qualification receipts. The existing five foundation procedures are retained, but all 86 native inventory entries remain NOT_RUN and most harness procedures are still NOT_IMPLEMENTED.

## No automatic promotion

Design is unchanged. No required behavior change has been established; no DESIGN_GAP is used to disguise missing code. The full exit condition remains unsatisfied. Continue IMPLEMENTATION, not CODE_REVIEW. Native execution belongs to later authorized gates but the unfinished harness/source belongs to this task now.
