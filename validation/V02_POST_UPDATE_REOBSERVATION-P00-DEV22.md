# V02A — Windows post-update reobservation

CHANGE_CLASS: EVIDENCE_UPDATE
RUN_ID: RUN-P00-VALIDATION-002
SOURCE_COMMIT: 86bb64938a136e3f8d6cfd0266685a01cb832b77
EXPECTED_LANE_PARENT: 180c87c041ce67c42fa4be49ee938c512c807da0
CANONICAL_MAIN_AT_START: 5466e99c7f80cb930ba2ca160475ab2f495c650a
ASSURANCE_CLASS: SAME_TRUST_DOMAIN_LOCAL_OPERATOR
REVIEW_STATUS: PENDING_EXACT_CANDIDATE_REVIEW
FINAL_REVIEW_RECORD: reviews/VALIDATION-V02A-POST-UPDATE-DEV22-REVIEW-001.md
FINAL_AUDIT_RECORD: reviews/VALIDATION-V02A-POST-UPDATE-DEV22-AUDIT-001.md

## Result and scope

The owner-updated Windows host was reobserved on 2026-09-21: Professional 25H2, build 26200.9457, AMD64, hypervisor present, boot 2026-09-21T01:30:05.5000000Z. WSL reports version 2.7.11.0 and the AI-FILM-P00-LAB distro remains Stopped. No Windows update, reboot, LAB start, registry policy change or native procedure was performed by this continuation.

The exact accepted dev22 host_profile predicate passed after explicit normalization of Professional to Pro, AMD64 to x64, and the Microsoft General Availability build row to stable. The Microsoft release-information table records Home/Pro 25H2 support through 2027-10-12 and GA build 26200.9457. A conservative cutoff of 2027-10-12T00:00:00Z leaves 385 whole days at observation, above the unchanged 90-day predicate. This is a support prerequisite result, not a complete native live-profile/catalog admission or HOST_READY verdict.

Source: https://learn.microsoft.com/en-us/windows/release-health/windows11-release-information (retrieved 2026-09-21, 25H2 servicing/history rows).

## Evidence and checks actually run

Receipt: `validation/evidence/V02A-POST-UPDATE-20260921/receipt.json`. SHA256: `2cd680bbd8a411584ba60f1455833dc357327a5ac9a28d194664fcd46968692c`. Adjacent stdout files retain sanitized command outputs. The complete local observation folder is `/home/dragon/ai-film-dev/run-evidence/validation/v02a-post-update-20260921`.

- Live registry/CIM observation, `wsl.exe --version`, and `wsl.exe -l -v` were read-only.
- Exact dev22 `host_profile` accepted the supported normalized observation. Three diagnostic negative inputs were rejected with exit 11 and the expected reasons: less than 90 days, missing support evidence, and unavailable virtualization. No production or test oracle was changed.
- All 61 tracked src/native files in the deployed validation directory matched exact source 86bb649... byte-for-byte. Its historical detached HEAD plus three-file overlay was preserved; clean Git HEAD is not claimed for that deployment directory.
- All 20 deployed tooling files matched their manifest. The existing private-derived public key, public file, metadata and reviewed trust anchor passed the deployed parity verifier. Private key mode remains 0600; no key bytes were exported.
- The deployed artifact-seal verifier passed all eight sealed LAB artifacts. This rechecks integrity, not a new restore-probe execution.
- Read-only preflight and intake returned 10 and 12 respectively on APPROVAL_ENVELOPE_MISSING. Staging remained unchanged. No READY/native policy was manufactured.
- Seven bootstrap checks passed on canonical V61 with the intent lane head: state contract, project docs, documentation governance, learning lifecycle, documentation structural audit, local runtime state, and strict remote continuity. These are structural checks, not a new holistic DOC-AUDIT.

The historical 766-test / 101-static accepted-candidate verdict is retained but was not rerun. No effectiveness promotion, learning lifecycle update, native result, qualification or SITE result is claimed by this change.

## Read profile and preserved authority

CORE, resume/write/handoff and scoped validation host-support profiles were used. Current state/router/map, continuity/Git/lane/workspace/test/recovery policy, the complete accepted Blueprint, exact design approval, dev22 local-authority change and the current V02 host-support/local-authority/validation plan were consulted. This is not a full phase-contract/native execution audit. The accepted product, authority model, contract/test digests, original RUN_ID and all native prerequisites remain frozen.

## Next cursor

V02A Windows update/reboot is observed complete. V02 remains BLOCKED because the fresh signed local authority object graph has not been created. Before V03, prepare and review exact live-profile/catalog bindings and per-procedure plans/fixtures; sign the current <=24h graph using the existing WSL-local key; pass current preflight/intake, artifact seal and pre-V03 policy staging/review. Reobserve durable prerequisites immediately before creating ephemeral authority. Do not reuse this support receipt as plan authorization or expire/recreate a suite just to repeat a blocked step.

The owning lane may carry this bounded progress ahead of main. Canonical PROJECT_STATE/NEXT_WORK_ITEM synchronization still requires its own reviewed transaction; until then, explicitly reconcile this receipt and do not ask the user to update Windows again.
