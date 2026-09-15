# NEXT WORK ITEM — IMPL-P00-001

```yaml
WORK_ITEM_ID: IMPL-P00-001
MODE: IMPLEMENTATION
PHASE: "00 — Host / WSL"
STATUS: IN_PROGRESS
CURRENT_DELIVERY: PARTIAL_SOURCE_DROP_DEV6
ENTRY_GATE: DESIGN_REVIEW_PASS
ENTRY_GATE_STATUS: SATISFIED_EXACT_V2
TARGET_GATE: CODE_REVIEW_PASS
PHASE_GATE: HOST_READY
MODE_TRANSITION_NOW: NONE
IMPLEMENTATION_MAY_RESUME: true
EXACT_DEV6_DELIVERY_DURABLE: true
SOURCE_RECOVERY_VERIFIED: true
GITHUB_FULL_DEV6_SOURCE_TREE_MATERIALIZED: false
DOCUMENTATION_SYNC: MANDATORY
LIVING_MEMORY: PROJECT_MEMORY.md
```

## Exact recovery anchor

```yaml
PACKAGE: IMPL-P00-001_IMPLEMENTATION_PACKAGE_V6.zip
SIZE_BYTES: 1178410
SHA256: 41f8a4ed1d80b87bc84981c3cdb2254a3fbc33f21b822580d7e0788b7b404f7e
DRIVE_FILE_ID: 1nYtbxJ3p0A0Oo_QyYgAc3zdyLbQYCSc4
RAW_REDOWNLOAD_SHA_VERIFIED: true
```

Before modifying source in a fresh chat/workspace, fetch the raw Drive artifact, verify size/SHA, extract fresh, and verify package manifest/source identity. Do not reconstruct dev6 from prose.

## Goal

Finish the remaining Phase 00 source/integration/fault-controller scope without re-labelling missing source as missing native evidence and without changing exact approved Design V2 behavior.

## First implementation increment

1. Inspect exact dev6 `docs/REMAINING_IMPLEMENTATION.md`, `docs/NATIVE_INTEGRATION_BOUNDARY.md`, source and tests related to executable/dependency trust, effective profile, service/OOBE/restart/resume and native factory.
2. Complete executable/interpreter/dependency byte-trust integration that is already required by approved contracts.
3. Complete remaining effective-profile handling needed by the same increment.
4. Complete only the directly coupled service/OOBE/restart/resume/factory branches that can be closed without changing reviewed behavior.
5. Add targeted negative/positive author tests.
6. Run targeted tests, then full workspace regression/static checks at the increment delivery boundary.
7. Run Documentation Sync Gate, persist reusable lessons in `PROJECT_MEMORY.md`, package exact next delivery, upload/hash-verify binary artifact, update Git state/docs, then proceed.

## Following implementation increments

After the first coherent increment is durably persisted:

- prior pre-C3/checkpoint selection and nested cross-stage E00 semantics;
- incomplete/temp bundle publication recovery and remaining E17 recovery applicability/integration;
- reviewed non-DIRECT transport support where required;
- full causal supported-route/failure controller procedures for the 86 normative T/F/subcases;
- production-factory integration author tests using explicit author test ports.

Do not mix all remaining blockers into one unreviewable patch if they can be closed as independent coherent increments.

## Already authored through dev6 — do not redo as absent

- mutation-fence recovery;
- detached C0-read recovery before mutation fence;
- protected C0 observation-to-plan proposal binding;
- primary native CLI dispatch;
- live committed-run NOOP components;
- snapshot stage identity/final archive re-observation;
- E17 write-ahead/read-only recovery;
- prior-guest hash-linked provenance selection;
- bounded early-failure capture;
- partial registered-LAB route controller/oracles;
- author regression baseline: 666 PASS; static: 88 PASS.

## Inputs

- `PROJECT_STATE.md`
- `NEXT_WORK_ITEM.md`
- relevant `PROJECT_MEMORY.md` entries
- `GIT_WORKFLOW.md`
- `SOURCE_IMPORT_STATUS.md`
- authoritative Blueprint V2
- exact approved Phase 00 Design V2 contracts/review approval from recovered dev6 package
- exact dev6 source tree from recovered package
- `docs/IMPLEMENTATION_STATUS.md`
- `docs/REMAINING_IMPLEMENTATION.md`
- `docs/NATIVE_INTEGRATION_BOUNDARY.md`
- latest verified workspace test report

## Forbidden

- Change FD/D00/public/reviewed contracts or lower acceptance.
- Execute Windows/WSL/LAB/SITE/guest/live-network operations during authoring.
- Register fixture/fake active CLI backends.
- Treat process exit, fixture flags, inventory, author-test count, or evidence-envelope labels as actual native proof.
- Delete unresolved journal/fence/read state to recover.
- Self-approve code review, qualification, HOST_READY, or production readiness.
- Ask for user host data as a substitute for remaining source implementation.
- Continue from a source tree whose recovery hash/manifest was not verified.

## Living-memory obligation

At the end of every meaningful increment automatically evaluate:

```text
state changed?              → PROJECT_STATE.md
next work changed?          → NEXT_WORK_ITEM.md
reusable learning found?    → PROJECT_MEMORY.md
workflow improved?          → GIT_WORKFLOW.md + PROJECT_MEMORY.md
implementation scope moved? → implementation/remaining/traceability/evidence docs
milestone reached?          → new checkpoint MD + JSON
```

## Design-gap rule

If implementation evidence demonstrates that reviewed behavior itself must change, record a genuine DESIGN_GAP and leave the affected implementation scope before redesign. Do not create a design gap merely because code is incomplete.

## Exit condition

A full author-complete source/harness/docs/test candidate exists; all `IMPL-REM-01…08` are actually closed or properly managed under the mode system; no hidden stub remains; full required author regression/static checks are clean; exact candidate identity is durably persisted and reviewable; canonical docs/state are synchronized.

Only then:

```text
MODE TRANSITION
FROM: IMPLEMENTATION
TO: CODE_REVIEW
TASK: CODE-REVIEW-P00-001
EXIT GATE: CODE_REVIEW_PASS
```
