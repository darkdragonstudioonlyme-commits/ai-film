# DOCSYS-V2-R9 — V60 WSL-local authority and host-support reconciliation

DESIGN_ID: DOCSYS-R9-V60-WSL-AUTHORITY-HOST-SUPPORT
TARGET_RELEASE: DOCSYS-V2-R9
TARGET_STATE_VERSION: 60
REVISION: R33_V60_WSL_AUTHORITY_HOST_SUPPORT
BASE_MAIN_COMMIT: e1153e105f2373ea2a4933e65c4d771ab84dffb6
VALIDATION_EVIDENCE_HEAD: 517783d29aecb3d6ae1b0548109480733fa36fe6
DESIGN_BRANCH: lane/docs-v2-r9-v60-wsl-authority-host-support-design
REVIEW_BRANCH: lane/docs-v2-r9-v60-wsl-authority-host-support-review
AUDIT_BRANCH: lane/docs-v2-r9-v60-wsl-authority-host-support-audit
REQUIRED_REVIEW_ID: DOC-V2-R9-REVIEW-034
REQUIRED_AUDIT_ID: DOC-V2-R9-AUDIT-034
PRODUCT_SOURCE_CHANGED_BY_DOCSYS: false
NATIVE_EXECUTION_ADVANCED: false

## WSL simplification

Validation has independently reviewed/audited and deployed the V02 authority inbox simplification. Tooling remains under WSL validation-ops, durable private key remains owner-only outside Git/inbox, and the canonical authority object inbox is now `/home/dragon/ai-film-dev/local-authority/dev22/inbox`. Deployment receipt SHA `8bb2f75c...` proves manifest 20/20, key parity PASS, identity-context non-drift, expected missing-envelope fail-closed state and watcher active/enabled.

## Host support gate

Live Windows registry observation is Professional / 23H2 / build 22631.3296. Microsoft current Home/Pro lifecycle makes 23H2 out of updates. Exact dev22 policy independently requires support_end-now >= 90 days. On 2026-09-18, 24H2's October 2026 end also falls inside that margin; validation therefore records 25H2-or-later as the minimum target class, subject to re-observing exact post-update facts.

The <=24h V02 authority suite is not generated before the OS update because it would expire or become identity/profile-stale before a valid V03 path. User action is only normal Windows Update + reboot; authority generation/signing remains WSL-local afterward.

## Boundaries

Prodlike and LAB remain exact dev22. LAB is stopped/sealed/restore-probed. No approval envelope/signature/native policy/native result/qualification/SITE/HOST_READY is created. All 86 native cases remain NOT_RUN. Learning state remains unchanged.

## Exact-tree rule

Historical/prior-tree R33/A33 remain V59 authority. R34/A34 are final verdict identities for this exact V60 semantic tree; any authority/host/native/learning semantic edit after review reopens review/audit.
