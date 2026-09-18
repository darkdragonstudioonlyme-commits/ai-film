# Phase00 dev22 — V02 LAB technical rebuild design

DESIGN_ID: V02-LAB-DEV22-REBUILD-P00-001
RUN_ID: RUN-P00-VALIDATION-002
STEP_ID: V02_LOCAL_OPERATOR_LAB_AUTHORITY
BASE_VALIDATION_HEAD: 046f428e46e463923864ee325b44b32746dde597
SOURCE_COMMIT: 86bb64938a136e3f8d6cfd0266685a01cb832b77
PACKAGE_SHA256: c2ea52087039f4c7b98c53a7cc0eaf1a4a0f931645f86491bf2eb8ef12956aae
CANDIDATE_ID: 6f895394-e0b4-5434-bebc-79ee4e576282
CANDIDATE_BINDING_SHA256: 4aaf09ec2ef8618a5680e147cd2eeac695f940d45ae5cb0446c7b7e5c2483384
LAB_DISTRO: AI-FILM-P00-LAB
STATUS: DESIGN_CANDIDATE_PENDING_REVIEW
NATIVE_EXECUTION_STARTED: false

## Scope

This transaction prepares only the disposable LAB technical substrate for exact dev22. It does not create a signed approval envelope, does not close V02 and does not start any native case.

The existing LAB is Ubuntu 24.04.5 WSL2, default user `aifilmlab`, password locked, Windows automount disabled, Windows PATH append disabled, no production mapping and no real credential. Existing dev21 remains the rollback source and its historical artifacts remain immutable.

## Payload contract

`build_lab_dev22_payload.py` packages only the immutable exact application tree from the already-audited prodlike dev22 release. It explicitly refuses wrong source/package/wheel/digest identities, any native-authority/native-execution claim, app-manifest drift, missing/extra app files or a failing source runtime verifier.

The output is deterministic:
- `AI-FILM-P00-DEV22_APP.tar`: sorted regular files only, root:root metadata, mode 0444, mtime 0;
- exact `AI-FILM-P00-DEV22_APP.sha256`;
- `LAB_DEV22_PAYLOAD_MANIFEST.json` binding candidate/source/package/wheel/digests and target root.

A host prodlike venv is never copied into LAB. The guest creates a fresh venv at `/opt/ai-film-lab/runtime/dev22/venv` and binds its site-packages to exact local `app/src`, preserving relocatability.

## Audited deployment sequence

After review/audit and canonical promotion only:

1. Reverify canonical validation head, prodlike dev22 runtime, durable local-key parity, V02 BLOCKED/APPROVAL_ENVELOPE_MISSING and LAB Stopped.
2. Build the deterministic app payload from `/home/dragon/ai-film-runtime/dev22`; verify the payload twice and record hashes.
3. Preserve a fresh stopped pre-migration WSL export in addition to the immutable historical dev21 pristine snapshot.
4. Start LAB only for preparation. Reverify isolation; create side-by-side `runtime/dev22`; extract exact app payload; create guest-local venv; write a dev22 launcher; keep app bytes 0444/directories 0555.
5. Run only metadata/read-only verification: dev22 `--version`, workspace-only preflight, `tools/run_native_acceptance_tests.py --list`, package/app manifest checks and inventory digest. No native route/test runner may execute.
6. Write a fresh dev22 `pre-v03-inventory.json` with exactly 86 NOT_RUN, parent_cases_executed=0, qualification=false, host_ready=false.
7. Terminate LAB and confirm Stopped.
8. Export a fresh dev22 pristine WSL snapshot. Import it under a temporary probe name, verify exact dev22 runtime/inventory/isolation, terminate/unregister the probe, then record restore_probe=PASS.
9. Replace host candidate technical facts and `LAB_ARTIFACT_SEAL_V1.json` with dev22 candidate-bound artifacts only after all hashes/restore probe pass. Make every sealed artifact and the seal non-writable.
10. Run canonical `verify-lab-artifact-seal.py`; it must PASS for candidate `6f895394...`, source `86bb649...`, binding `4aaf09ec...`.
11. End with LAB Stopped, V02 still BLOCKED on missing approval envelope, all 86 native cases NOT_RUN.

Any failure restores/retains dev21 as the authority-free rollback source and must not generate a consumable V02 package.

## Boundary

This transaction authorizes technical LAB preparation only after audit. The next separate reviewed transaction may build/sign the candidate-specific local authority object graph from the successfully sealed dev22 LAB evidence.
