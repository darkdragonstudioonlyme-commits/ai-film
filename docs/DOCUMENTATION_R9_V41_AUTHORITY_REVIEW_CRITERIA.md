# DOCSYS-V2-R9 V41 Authority Reference Consistency — R12 Detailed Review Criteria

R12 may PASS only if one exact `R11_V41_AUTHORITY_REFERENCE_CONSISTENCY` design SHA satisfies all conditions below.

1. Product/native state is byte/identity-equivalent to canonical V41: dev21 source, blocked V02 run, 86 native `NOT_RUN`, no qualification, no SITE claim and HOST_READY not evaluated.
2. Canonical governance predeclares new R12/A12 identities and new DESIGN/REVIEW/AUDIT branches; R11/A11 are not reused for the changed SHA.
3. `DESIGN_RECORD` exists in both Markdown and JSON governance and resolves to the active design surface.
4. Markdown/JSON governance parity is machine-checked for release, revision, branch roles, design record, final review/audit IDs and records, and promotion state.
5. `PROJECT_STATE.md`, the current state checkpoint and the active design record contain no superseded `R<n>/A<n>` pair as live authority. Historical mismatches are allowed only when the same line explicitly marks the reference as prior/old/historical/superseded/reused/earlier/previous/pre-promotion evidence.
6. The previously stale R10/A10 live-authority wording is corrected without deleting the immutable R10/A10 and R11/A11 evidence chains.
7. Learning 007 is finalized to `PASS` + `ACTIVE` using its existing R11/A11 activation evidence and no longer depends on the current final-verdict fields.
8. `workflow-health/HEALTH_REVIEW-DOCSYS-R9-V41-AUTHORITY-015.md` preserves the regression, root cause and correction route.
9. Existing learning lifecycle, adversarial lifecycle, documentation governance, active-document consistency, workflow continuity and holistic audit checks all PASS on the exact design target.
10. Any effectiveness transition introduced after detector CI must use a metric-bound receipt and remain subject to independent R12 semantic review; no checker PASS alone may manufacture EFFECTIVE.
11. GitHub platform protection remains explicitly separate from project policy.

Any hidden stale authority, reused verdict, deleted failure evidence, false EFFECTIVE claim, product/native advancement or red exact-design CI requires R12 FAIL.
