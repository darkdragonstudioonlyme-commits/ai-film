# DOCSYS-V2-R9 V41 — Forensic self-learning hardening

## Purpose

This revision incorporates an independent forensic audit of the control plane's self-learning and continuous-improvement claims. The objective is not to add more PASS labels; it is to close ambiguity between **declared design**, **structural checker success**, **semantic proof**, and **actual cross-run improvement**.

The product/native state remains unchanged. Exact dev21 remains the reviewed candidate and `RUN-P00-VALIDATION-001` remains blocked at V02 external LAB authority.

## Findings addressed at the documentation/policy layer

### F1 — Evidence path existence is weaker than effectiveness proof

The current lifecycle checker validates that effectiveness evidence paths exist. That is useful structural integrity, but it does not evaluate whether those artifacts prove the declared metric. V41 hardening makes the distinction normative: `EFFECTIVE` requires semantic binding from learning → metric → scope/sample → predicate → observations/evidence → independently reviewed result.

### F2 — Success metric has one semantic owner

`learning/LEARNING-*.md` owns what was learned and its `SUCCESS_METRIC`. The lifecycle register may duplicate the metric for convenience, but the duplicate must match the immutable record. Changing a metric to make measurement easier is not a lifecycle update; it is a new/successor learning requiring review.

### F3 — Intermediate verdict branches need role-aware CI

The exact design target can be green while a later review-only or audit-only branch becomes red because a promoted-tree checker rejects a partial verdict set. Review/audit PASS must therefore report both the exact design-target evidence and the verdict-bearing commit's CI state. Tooling should become branch-role aware; until then the red verdict-branch condition is process debt and cannot be hidden.

### F4 — Test review must resolve its proposal

A durable `TEST_REVIEW` cannot depend on a proposal that only existed in conversation context or a mutable branch tip. This candidate restores `TEST_CHANGE-P00-DEV20-FACTORY-003.md` byte-identically from immutable IMPLEMENT history and makes canonical proposal resolution a standing test-governance rule.

### F5 — Root metadata is not implicit project truth

Files such as root `pyproject.toml` may contain old package metadata. Unless PROJECT_STATE delegates authority to such a file, they are not current candidate/version/review truth. Cold-start routing must use the documented source-of-truth hierarchy.

### F6 — Policy is not platform enforcement

A project can require CI/review procedurally while GitHub branch/ruleset settings do not technically prevent bypass. Documentation must state the difference. Platform enforcement is an external fact to verify, not infer from policy wording.

### F7 — Continuous improvement requires longitudinal measurement

Activity counts are not improvement. Workflow health now requires comparable population/time-window measurement snapshots when claiming a trend such as lower duplicate work, fewer repeated findings, or higher resume-without-rework rate.

## Measurement receipt contract

A semantic effectiveness receipt records at minimum `LEARNING_ID`, `METRIC_ID`, metric version, scope, sample requirement, observations, expected predicate, result, immutable evidence identities, measurement commit and independent review ID. A receipt with N=1 cannot satisfy a metric requiring N=3.

The hardened lifecycle checker now machine-enforces immutable-metric equality, receipt-to-metric hash binding, receipt/evidence-path binding, and stage-aware DESIGN/REVIEW/AUDIT verdict invariants. Semantic truth of a receipt's observations remains independently review-gated: tooling proves the binding, while the release-selected final independent review/audit decide whether the evidence actually satisfies the predicate. CI path filters cover workflow-runs, test-governance, environments, model-evaluations, deliveries and root metadata, and server-side continuity checking is included. GitHub `main` branch protection/ruleset enforcement remains external platform debt.

## Truthful reclassification of prior effectiveness claims

Forensic reconciliation restored every register `success_metric` to the immutable learning record. Three older structural `EFFECTIVE` claims (control-checker generality, source visibility, and workflow continuity) did not have evidence sufficient for the immutable metric and are returned to `PENDING_MEASUREMENT`. Learning 005/006 retain `EFFECTIVE` with explicit metric-bound receipts. GitHub Actions then exposed ambient-environment recurrence in learning 004, so 004 is reclassified `INEFFECTIVE` with successor 007. New learning 007 captures semantic binding plus stage/environment isolation and is pending measurement after activation.

GitHub Actions run `35218316047` is preserved as negative evidence: exact design SHA `57296cc...` passed the lifecycle checker but failed the adversarial suite because the fixture inherited `GITHUB_REF_NAME`. The correction neutralizes ambient role variables for generic fixtures and routes the recurrence through learning 004 → 007.

## Promotion/review boundary history

Revision `R10_V41_FORENSIC_PROMOTION_FINALIZATION` superseded the earlier unpromoted V41 R8 design target for promotion purposes. The prior R9/A9 verdict artifacts remain immutable evidence for their old SHA and were not reused.

That finalization revision predeclared new review/audit identities R11/A11. Independent R11/A11 subsequently bound its exact finalized forensic-hardening SHA; promotion added only those verdict records. Those verdicts remain authority for that exact historical SHA, not for later edits.

## Non-claims

This revision modifies lifecycle/governance checkers and CI coverage, but does not change product source, native validation procedures, LAB authority, qualification, SITE evidence or HOST_READY. Full semantic interpretation remains independent-review responsibility, and GitHub repository protection/rulesets remain external platform debt until separately configured and verified.

## Promotion-state finalization correction history

Pre-promotion inspection of the green R10/A10 chain found that `FORENSIC_HARDENING.STATUS` still said `DESIGN_CANDIDATE_PENDING_INDEPENDENT_R10_A10` and JSON still described two implemented controls as merely specified. Merging that exact tree would have created immediate canonical state drift. The R10/A10 verdicts therefore remain valid historical evidence for their old design SHA but are not promotion authority for the corrected tree.

R10_V41 predeclared `PROMOTION_STATE: ACTIVE_ON_PROMOTION` and `FORENSIC_HARDENING.STATUS: ACTIVE_ON_PROMOTION`, aligned JSON with the machine-enforced checker/CI reality, and historically required new R11/A11 verdicts bound to the corrected exact SHA. No product/native state changed.

## R11_V41 authority-reference consistency correction

Post-promotion canonical reread found that three live-authority sentences still used superseded R10/A10 wording even though structured governance selected R11/A11. That contradiction demonstrates a checker blind spot: token presence and structured parity did not prove that current prose used the same verdict authority.

Revision `R11_V41_AUTHORITY_REFERENCE_CONSISTENCY` records the incident in `workflow-health/HEALTH_REVIEW-DOCSYS-R9-V41-AUTHORITY-015.md`, allocates new R12/A12 verdicts for the changed exact tree, exposes the active `DESIGN_RECORD` in canonical governance, and extends active-document checking so the expected live verdict pair is derived from canonical final IDs. Mismatched `R<n>/A<n>` pairs fail on current authority surfaces unless their line explicitly marks the reference as prior, old, historical, superseded, reuse, earlier, previous, or pre-promotion evidence.

The detector is now protected by `tools/test_project_docs_checker.py`: the baseline must pass, stale live authority must fail, explicit historical authority must pass, and structured governance parity drift must fail. The workflow path filter covers all `tools/test_*.py` regression files.

Exact detector commit `0d106cbad7e144b737cb43eb17409339d107021d` passed GitHub Actions run `35223256888` / job `105208358932` after two fail-closed refinement runs. That real semantic schema/checker evolution is the candidate measurement event for `LEARNING-CONTROL-001`, bound by `learning/measurements/MEASUREMENT-LEARNING-CONTROL-001-001.md` and still requiring R12/A12 semantic verification.

`LEARNING-AUTHORITY-REFERENCE-CONSISTENCY-008` captures the new reusable rule and is only conditionally active through R12/A12; its effectiveness remains pending for a future documentation promotion or authority-reference regression.

This correction does not rewrite immutable historical verdict records and does not treat earlier PASS labels as proof that the blind spot never existed. R12/A12 must independently review/audit the new exact design tree before promotion.
