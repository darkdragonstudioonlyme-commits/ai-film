# DOCSYS-V2-R9 V41 Authority Reference Consistency — R12 Detailed Review Criteria

R12 may PASS only if one exact `R11_V41_AUTHORITY_REFERENCE_CONSISTENCY` design SHA satisfies all conditions below.

1. Product/native state is byte/identity-equivalent to canonical V41: dev21 source, blocked V02 run, 86 native `NOT_RUN`, no qualification, no SITE claim and HOST_READY not evaluated.
2. Canonical governance predeclares new R12/A12 identities and new DESIGN/REVIEW/AUDIT branches; R11/A11 are not reused for the changed SHA.
3. `DESIGN_RECORD` exists in both Markdown and JSON governance and resolves to the active design surface.
4. Markdown/JSON governance parity is machine-checked for release, revision, branch roles, design record, final review/audit IDs and records, and promotion state.
5. `PROJECT_STATE.md`, the current state checkpoint and the active design record contain no superseded `R<n>/A<n>` pair as live authority. Historical mismatches are allowed only when the same line explicitly marks the reference as prior/old/historical/superseded/reuse/earlier/previous/pre-promotion evidence.
6. The previously stale R10/A10 live-authority wording is corrected without deleting the immutable R10/A10 and R11/A11 evidence chains.
7. Learning 007 is finalized to `PASS` + `ACTIVE` using its existing R11/A11 activation evidence and no longer depends on the current final-verdict fields.
8. `workflow-health/HEALTH_REVIEW-DOCSYS-R9-V41-AUTHORITY-015.md` preserves the regression, both fail-closed detector refinement runs, the green detector run and the correction route.
9. `tools/test_project_docs_checker.py` persistently proves baseline PASS, stale live authority rejection, explicit historical-authority acceptance and structured-governance parity rejection; CI triggers all `tools/test_*.py` files.
10. `LEARNING-CONTROL-001` may transition to EFFECTIVE only if R12 independently validates the metric-bound receipt against exact measurement commit `0d106cbad7e144b737cb43eb17409339d107021d`, run `35223256888` / job `105208358932`, and confirms runtime/lane/artifact fail-closed predicates were not weakened.
11. `LEARNING-AUTHORITY-REFERENCE-CONSISTENCY-008` is a new reusable learning candidate only: activation is conditional on R12/A12 and effectiveness remains pending after promotion.
12. Existing lifecycle/adversarial/governance/active-doc/active-doc-adversarial/continuity/holistic checks all PASS on the exact final design target.
13. GitHub platform protection remains explicitly separate from project policy.

Any hidden stale authority, reused verdict, deleted failure evidence, unsupported EFFECTIVE claim, product/native advancement or red exact-design CI requires R12 FAIL.
