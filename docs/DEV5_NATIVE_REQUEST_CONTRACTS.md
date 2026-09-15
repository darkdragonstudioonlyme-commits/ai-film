# Dev5 internal request records and primary entry

These are implementation encodings of approved Phase00 purposes, not new phase permissions. All native records come from the existing out-of-band role/digest trust chain. The source package never emits approvals, registrations, qualification receipts or fabricated measurements. No sample below should be interpreted as execution authority.

| Entry | Input | Behavior |
|---|---|---|
| `preflight --plan-ref` | Pinned `execution_plan` containing a PASSIVE or DISCOVERY plan | Protected C0 capture or explicitly authorized guest probe, never automatic conversion between them |
| `apply --plan-ref` | Pinned execution plan for an allowed apply purpose | Native session |
| `verify --plan-ref` | Pinned execution plan for allowed verify/recovery purpose | Native session or exact original-request recovery |
| `support-bundle --plan-ref` | Pinned SUPPORT_BUNDLE plan | Native publisher path, preserves interface outcome |
| `dry-run --selection-ref --capture-digest` | Pinned `binding_selection` plus digest of committed protected C0 capture | Unapproved plan proposal with observed-before and desired-after separate |
| `dry-run --binding` | Offline document | Document-only plan analysis, no native eligibility assertion |

Missing native plan reference is `10/NATIVE_PLAN_REFERENCE_REQUIRED`. A malformed digest is input failure. On POSIX a well-formed native request reaches the Windows platform guard and exits 11 before constructing native APIs. Native execution is not authorized in authoring.

`execution_plan`: schema_version 1, withdrawn false, plan object; fixture-only native inputs rejected. Its role/digest is anchored outside the request. `binding_selection`: schema_version 1, withdrawn false, exact host/owner/capture scope, desired binding fields excluding observed host/principal/build/profile/before. The capture supplies those observed values. Output `BINDING_PROPOSED` stays protected; public output contains references, blockers and no approvals.

`recovery_request` for no-fence reads selects DIAGNOSE/RECONCILE/PAUSE/CANCEL and exact host/owner/original-plan/read-set digest. The recovery execution plan retains the original actor/target/run and references the immutable original plan. Writer observations, missing-witness absence proof and revocation are separate data sources, not request flags. See `read_recovery.py` and `native/read_request_recovery.py` for exact checks.

`journal_maximum_additional_bytes` is a required native execution reservation. It is checked against native logical cap, physical volume allocation/free space and actual append size. It is not a permission to expand a held reservation. C0 capture, dry-run and recovery use their own explicit output permissions/reservations.

`lab_route_suite` is consumed by the route controller only in registered disposable LAB. It binds host/owner/build/test set and a bounded issue/expiry interval, with explicit case → interface/purpose/plan_ref/expectation rows. It does not create fixture conditions or qualification. Route expectations are COMMIT/NOOP/PAUSE/RECONCILE/DIAGNOSE and are checked against native journal records. They do not mean parent T/F cases passed.

Full source closure is still pending as recorded in `REMAINING_IMPLEMENTATION.md`; these interfaces must not be advertised as a production-ready installation path.
