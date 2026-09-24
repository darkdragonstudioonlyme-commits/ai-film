# Workflow Router v2

Canonical routing is CONTINUE_PROTOCOL.md.

Normal "Tiếp tục" selects READY work from BACKLOG.yaml and advances the earliest incomplete product milestone. Historical P00 current_work/state JSON no longer routes normal turns.

Escalate only for:
- destructive cleanup or irreversible migration
- publication
- secret/rights boundary changes
- bounded paid-resource approval
- incompatible product data-schema migration

All other work uses branch → implement → tests → one cross-review/fix cycle → merge.
See RESUME.md for the live cursor and archive/p00-governance-2026-09-24 for the frozen legacy control plane.
