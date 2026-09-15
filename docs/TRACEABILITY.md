# Traceability — dev8 lifecycle increment

Approved contract remains `f259656c48ed24c15bd48da2bb040950ed94d8edcf1473cf6456b96578c933ee`.

Final author result: **683 PASS / 0 failures/errors/skipped**, static **92 PASS**. Source digest `e793fc78d622c987343d1b5e5d3909cb4c19d7b0bcbafbc32909f137a1894c08`; test digest `f91b422b6ce4ffeee9fc516bff0dc00c8e4a6216ae98e94b977ac2ef00949021`.

| New author test module | Cases | Parent specifications | What it demonstrates |
|---|---:|---|---|
| `test_dev8_lifecycle` | 10 | T00-05, T00-07, T00-13, T00-14-I; F00-09/10/11 | Synthetic control-flow/oracle coverage for pending reboot, changed boot witness, owner-verification wait and no mutation replay. It is not native lifecycle validation. |

Broad parent IDs remain NOT_RUN at native/LAB/SITE scope. AC00-01…08 remain NOT_EVALUATED.

---

# Traceability — dev5 partial implementation

Approved contract: `f259656c48ed24c15bd48da2bb040950ed94d8edcf1473cf6456b96578c933ee`.
Exact source: `953de476ce5fc1610c49172c8ddf8b6698bb6dcc3f8a5f98735a4d61bd30135e`.
Exact tests: `7100cc014babf8cad40941dcfba8e5fa2d841b0dad3383022ab44416faca493c`.

Actual final report: **653 workspace tests PASS**, zero failures/errors/skipped. This includes 119 new cases over the re-executed dev4 baseline of 534. No native execution or qualification occurred.

| New module | Cases | Related parent specifications | Scope |
|---|---:|---|---|
| test_dev5_read_recovery | 39 | T00-03, T00-06, T00-07, T00-13, T00-14 | Original-request detached-read recovery before mutation fence; journal reservations — partial |
| test_dev5_observation_binding | 28 | T00-01, T00-02, T00-06, T00-14 | C0 capture-to-plan proposal; read identity and source/desired separation — partial |
| test_dev5_evidence_cli | 35 | T00-05, T00-06, T00-08, T00-13, T00-14 | Native request/factory binding, stage identity, lifecycle predicates, publication readback — partial |
| test_dev5_route_harness | 17 | T00-06, T00-07, T00-11, T00-12, T00-13, T00-14 | Journal-based route-oracle logic and native-controller dispatch/denial — partial |

The JSON preserves previous links and adds exact executed IDs for these components. Broad parent links are not whole-parent executions. All eight ACs remain NOT_EVALUATED, and all 86 T/F/subcase entries remain NOT_RUN.

## Controller vs coverage

The new registered-LAB route controller calls the concrete native factory and has journal-based outcome checks. Only its oracle/dispatch/denial logic was exercised with synthetic ports in the workspace; no native case ran. It is not the full causal fault suite, cross-principal controller, restart/restore-isolation suite or full production-factory E2E implementation. Five existing foundation procedures remain partial contributions.

## Remaining source and tests

Complete nested/prior-stage guest and pre-C3 proof integration; failure-before-snapshot, temp-output and E17 crash handling; non-DIRECT profiles; executable/dependency trust and remaining lifecycle/factory paths; all required native failure-controller preparations and assertions. See REMAINING_IMPLEMENTATION.md.

## Author test history

`evidence/dev5-history/` retains the re-executed dev4 baseline and intermediate failures from newly required publisher journal fixtures, changed CLI error expectations, the framed-journal test fixture, and a source defect in matching SAFE_PAUSE to the original run/request. Four negative cases exposed the latter; the source was tightened to match original plan, request, evidence digest and matching CLEAR. Those reports are not target validation failures. The final report reflects the final source/test hashes above. No errors or skipped cases remain in that executed workspace suite.
