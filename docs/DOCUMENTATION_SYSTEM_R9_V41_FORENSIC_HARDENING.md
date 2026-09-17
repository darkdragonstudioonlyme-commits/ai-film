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

The hardened lifecycle checker now machine-enforces immutable-metric equality, receipt-to-metric hash binding, receipt/evidence-path binding, and stage-aware DESIGN/REVIEW/AUDIT verdict invariants. Semantic truth of a receipt's observations remains independently review-gated: tooling proves the binding, while R10/A10 decide whether the evidence actually satisfies the predicate. CI path filters now cover workflow-runs, test-governance, environments, model-evaluations, deliveries and root metadata, and server-side continuity checking is included. GitHub `main` branch protection/ruleset enforcement remains external platform debt.

## Truthful reclassification of prior effectiveness claims

Forensic reconciliation restored every register `success_metric` to the immutable learning record. Three older structural `EFFECTIVE` claims (control-checker generality, source visibility, and workflow continuity) did not have evidence sufficient for the immutable metric and are returned to `PENDING_MEASUREMENT`. Learning 004/005/006 retain `EFFECTIVE` with explicit metric-bound receipts. New learning 007 captures this forensic failure class and is pending measurement after activation.

## Promotion/review boundary

This is revision `R9_V41_FORENSIC_HARDENING`. It supersedes the earlier unpromoted V41 R8 design target for promotion purposes. The prior R9/A9 verdict artifacts remain immutable evidence for their old SHA and are not reused.

The final candidate predeclares new review/audit identities:

- `DOC-V2-R9-REVIEW-010`
- `DOC-V2-R9-AUDIT-010`

Independent R10/A10 must bind the exact final forensic-hardening SHA. Promotion remains verdict-only after audit and requires post-promotion CI.

## Non-claims

This revision modifies lifecycle/governance checkers and CI coverage, but does not change product source, native validation procedures, LAB authority, qualification, SITE evidence or HOST_READY. Full semantic interpretation remains independent-review responsibility, and GitHub repository protection/rulesets remain external platform debt until separately configured and verified.
