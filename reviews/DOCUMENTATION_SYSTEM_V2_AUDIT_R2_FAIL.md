# Documentation System V2 — Holistic Audit R2

```yaml
AUDIT_ID: DOC-V2-AUDIT-002
TARGET_COMMIT: e75681f3dd33a7b541a051ce7ab44662d8693579
DETAILED_REVIEW: DOC-V2-REVIEW-003 / PASS
AUDIT_LANE: DOC-AUDIT-V2
SOURCE_MODIFIED_DURING_AUDIT: false
VERDICT: FAIL
CLOSED_FROM_R1: [DOCV2-A01]
```

All automated checks passed. Holistic semantic audit found three persistence/reproducibility gaps not covered by the checkers.

## DOCV2-A02 — HIGH — environment snapshot digest definition is self-referential/ambiguous

`SERVER_ENVIRONMENT.md` says the digest is over the YAML fact values below, but that YAML block contains `SNAPSHOT_DIGEST` itself. A second implementation cannot know whether to include or exclude the digest without relying on unstated convention.

Required: define an explicit digest input schema/payload that excludes the digest field, ideally persist the exact canonical fact payload or exact immutable environment record and verify its hash.

## DOCV2-A03 — HIGH — no immutable storage contract for environment snapshots/model evaluations

The docs require old environment facts/results not be overwritten, but there is no canonical `environments/` or `model-evaluations/` record domain. Keeping all history in active methodology files would either overwrite evidence or create bloat.

Required: define immutable environment snapshot and model-evaluation record paths/indexing/identity, with active docs containing methodology/current pointer only.

## DOCV2-A04 — MEDIUM — self-learning records have no durable persistence domain

`SELF_LEARNING.md` defines `LEARNING_ID`, evidence, promotion and success metric, while `PROJECT_MEMORY.md` is intentionally compact. There is no canonical location for a learning record that did not originate in an existing review/health record.

Required: define immutable `learning/` records (or equivalent), compact index ownership, supersession/retirement linkage, and success-metric follow-up without regrowing active memory prose.

## Disposition

Return to DOC-DESIGN-V2. A new immutable design must pass detailed DOC-REVIEW-V2 before holistic audit reruns.
