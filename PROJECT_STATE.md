# AI-FILM-SERVER — CANONICAL PROJECT STATE V14

> **READ THIS FILE FIRST IN EVERY NEW CHAT.**  
> Current operational truth only. Reusable lessons live in `PROJECT_MEMORY.md`; immutable history lives in versioned checkpoints.

## 1. Fast resume snapshot

```yaml
PROJECT: AI-FILM-SERVER
STATE_VERSION: 14
REPOSITORY: darkdragonstudioonlyme-commits/ai-film
DEFAULT_BRANCH: main

CURRENT_MODE: IMPLEMENTATION
CURRENT_PHASE: "00 — Host / WSL"
CURRENT_TASK: IMPL-P00-001
TASK_STATUS: IN_PROGRESS
TARGET_GATE: CODE_REVIEW_PASS
PHASE_GATE: HOST_READY
MODE_TRANSITION: NONE

REQUIREMENTS_BASELINE: "AI VIDEO SERVER — SINGLE CHAT WORKFLOW BLUEPRINT V2"
REVIEWED_DESIGN: "Phase00 exact Design V2 — REVIEW-P00-002 PASS"
CURRENT_VERIFIED_DELIVERY: "0.1.0.dev6 / PARTIAL_SOURCE_DROP_DEV6"
AUTHOR_COMPLETE: false
CODE_REVIEW_HANDOFF_READY: false

EXACT_DEV6_DELIVERY_DURABLE: true
SOURCE_RECOVERY_VERIFIED: true
IMPLEMENTATION_MAY_RESUME: true
GITHUB_FULL_DEV6_SOURCE_TREE_MATERIALIZED: false
DRIVE_BINARY_RECOVERY_ANCHOR: true

DEV6_PACKAGE: IMPL-P00-001_IMPLEMENTATION_PACKAGE_V6.zip
DEV6_SIZE_BYTES: 1178410
DEV6_SHA256: 41f8a4ed1d80b87bc84981c3cdb2254a3fbc33f21b822580d7e0788b7b404f7e
DEV6_DRIVE_FILE_ID: 1nYtbxJ3p0A0Oo_QyYgAc3zdyLbQYCSc4
RAW_REDOWNLOAD_SHA_VERIFIED: true

WORKSPACE_AUTHOR_TESTS: "666 PASS / 0 failure / 0 error / 0 skip"
STATIC_AUTHOR_CHECKS: "88 PASS"
NATIVE_WINDOWS_WSL: NOT_RUN
LAB: NOT_RUN
SITE: NOT_RUN
QUALIFICATION_ISSUED: false
HOST_READY: NOT_EVALUATED

AUTO_DOCUMENTATION_SYNC: true
NO_SILENT_KNOWLEDGE: true
LIVING_MEMORY_FILE: PROJECT_MEMORY.md
NEXT_ACTION: "Resume IMPL-P00-001 from exact dev6: executable/dependency trust + effective-profile/service/OOBE/restart/resume/factory increment."
```

**Do not transition to CODE_REVIEW.** Implementation may resume, but the work item remains partial.

## 2. Canonical persistence model

The project uses explicit hybrid persistence:

- **GitHub** is canonical for current state, living memory, workflow, next work, reviewable source/diffs that can be reliably written, and commit history.
- **Google Drive raw artifact storage** is the exact binary recovery anchor for packaged deliveries when needed.
- Every exact external artifact is linked from Git by file ID/name, size and SHA-256.

The dev6 persistence blocker is resolved because the exact V6 ZIP was uploaded by file reference, downloaded again as raw bytes, and its SHA-256 reverified equal to the original. This is persistence evidence only; it is not code review or native validation.

`GITHUB_FULL_DEV6_SOURCE_TREE_MATERIALIZED=false` remains explicit. A future chat should recover dev6 from the verified Drive artifact instead of reconstructing it from prose.

## 3. New-chat bootstrap

1. Read this file.
2. Read `NEXT_WORK_ITEM.md`.
3. Read Active Memory Index/relevant entries in `PROJECT_MEMORY.md`.
4. Verify current GitHub `main` head.
5. Read `GIT_WORKFLOW.md`.
6. Read `SOURCE_IMPORT_STATUS.md` for exact recovery procedure.
7. Fetch Drive file `1nYtbxJ3p0A0Oo_QyYgAc3zdyLbQYCSc4` as raw bytes.
8. Verify size `1178410` and SHA-256 `41f8a4ed1d80b87bc84981c3cdb2254a3fbc33f21b822580d7e0788b7b404f7e` before extraction/modification.
9. Read the authoritative Blueprint and exact approved Phase00 V2 contracts from the recovered package.
10. Continue only `IMPL-P00-001` in IMPLEMENTATION mode unless this state has advanced.

Do not depend on previous chat history and do not reconstruct dev6 from summaries.

## 4. Authority and approved baseline

Precedence:

1. authoritative Blueprint V2;
2. frozen `FD-01…FD-08`;
3. exact Phase00 Design V2 contracts;
4. `REVIEW-P00-002` approval;
5. exact implementation source/delivery candidate;
6. actual test/evidence reports;
7. this current state;
8. reusable project memory;
9. historical checkpoints.

```yaml
FROZEN_DECISIONS: "FD-01…FD-08 unchanged"
APPROVED_PHASE00_DESIGN: "D00-01…D00-14 exact V2"
DESIGN_REVIEW_PASS: SATISFIED_EXACT_V2
APPROVED_CONTRACT_SET_DIGEST: f259656c48ed24c15bd48da2bb040950ed94d8edcf1473cf6456b96578c933ee
```

No design gap is currently established.

## 5. Phase00 implementation invariants

- establish correct host/principal/target identity before mutation;
- preserve existing Windows/WSL state unless exact reviewed plan authorizes change;
- treat shared/global WSL effects as host-wide where applicable;
- use durable admission/fence/read/journal semantics;
- process exit is not native postcondition proof;
- timeout/interruption may produce `UNCERTAIN`; never blind-retry or erase durable state;
- require reviewed protection/recovery evidence before relevant C3 mutation;
- SITE active operations require qualification evidence; LAB evidence generation is separate;
- terminal/gate assertions correspond to final effective lifecycle state;
- prove restore isolation before first boot where required;
- evidence completeness, public bundle completeness and gate eligibility remain distinct;
- `APPLIED != VERIFIED != HOST_READY`;
- no destructive default recovery merely to make retry succeed.

## 6. Dev6 implementation baseline

Already authored through dev6; do not redo as absent:

- canonical inputs/plan hashing, approval/qualification/trust policy core;
- resource/capacity/profile predicates;
- host-global admission and durable fence/read-set/journal concepts;
- Windows identity/filesystem/trust/source-pinning adapters;
- native process supervision and actuator components;
- session runner/native driver and postcondition observers;
- mutation-fence and detached-read recovery;
- live committed-run NOOP;
- protected C0 capture → plan proposal;
- primary native CLI to concrete factory;
- guest inventory/content/sentinel and terminal sweep components;
- evidence catalog/snapshot/support-bundle components;
- stage identity/final archive re-observation;
- publication write-ahead/recovery;
- E17 write-ahead/read-only recovery;
- prior-guest/C3 provenance selection;
- bounded early-failure capsule;
- partial registered-LAB route controller/oracles;
- extensive author regression.

## 7. Verified evidence baseline

```yaml
AUTHOR_WORKSPACE_REGRESSION: "666 PASS / 0 failures / 0 errors / 0 skipped"
STATIC_AUTHOR_CHECKS: "88 PASS"
WINDOWS_WSL_NATIVE: NOT_RUN
POWERSHELL_NATIVE: NOT_RUN
GUEST_AGENT_LIVE: NOT_RUN
LIVE_NETWORK: NOT_RUN
LAB_NATIVE_SUITE: NOT_RUN
SITE_VALIDATION: NOT_RUN
QUALIFICATION_RECEIPT: NOT_ISSUED
AC00_01_TO_08: NOT_EVALUATED
NATIVE_T_F_SUBCASE_INVENTORY: NOT_RUN
CODE_REVIEW: NOT_PERFORMED
HOST_READY: NOT_EVALUATED
```

Author regression is not native validation. See `MEM-20260915-003`.

## 8. Open implementation items

All full-item REMs remain OPEN:

- `IMPL-REM-01`: finish effective-profile/eligibility integration and full native-factory route flows.
- `IMPL-REM-02`: finish exhaustion/interrupted-reader/lifecycle journal procedures without implicit reset.
- `IMPL-REM-03`: finish executable/dependency byte trust, source epochs, prior pre-C3/checkpoint proof selection.
- `IMPL-REM-04`: finish service/OOBE/restart/resume and production-factory execution-path author tests.
- `IMPL-REM-05`: finish prolonged/multi-stage resume/later request/recovery-publication interactions.
- `IMPL-REM-06`: finish non-DIRECT transport and effective-profile/terminal/restore integration.
- `IMPL-REM-07`: finish nested cross-stage semantics, prior pre-C3/checkpoint selection, temp/incomplete publication recovery and remaining E17 integration.
- `IMPL-REM-08`: finish causal preparations/controllers/oracles for normative 86-case inventory plus production-factory integration tests.

Open blocker groups remain `IMPL-BLOCK-01…03`; they are source/integration/harness work, not missing user data.

## 9. Exact current implementation order

First coherent increment:

1. executable/interpreter/dependency byte-trust integration;
2. remaining effective-profile behavior;
3. directly coupled service/OOBE/restart/resume/factory branches;
4. targeted positive/negative author tests;
5. full author regression/static checks at delivery boundary;
6. documentation sync + exact delivery persistence + Git state update.

Then, as separate coherent increments where practical:

- prior pre-C3/checkpoint + nested cross-stage E00;
- temp/incomplete bundle + remaining E17 recovery;
- reviewed non-DIRECT transport;
- causal 86-case controller suite;
- production-factory integration author tests.

See `NEXT_WORK_ITEM.md` for executable detail.

## 10. Forbidden in current mode

- no FD/D00/public-contract changes;
- no acceptance lowering;
- no Windows/WSL/LAB/SITE/guest/live-network execution during authoring;
- no fixture/fake active production backend;
- no process-exit/fixture/test-count/envelope-label substitution for native proof;
- no deletion of unresolved durable state as a shortcut;
- no self-approved code review/qualification/HOST_READY;
- no user host data requested as substitute for missing implementation;
- no fabricated DESIGN_GAP for incomplete source;
- no unverified source restoration;
- no useful reusable knowledge left only in chat.

## 11. Documentation Sync Gate

At every meaningful increment, automatically update as applicable:

```text
state/gates/tests/blockers       → PROJECT_STATE.md
exact next work                  → NEXT_WORK_ITEM.md
reusable discovery/optimization  → PROJECT_MEMORY.md
workflow improvement             → GIT_WORKFLOW.md + PROJECT_MEMORY.md
implementation progress          → implementation/remaining/traceability/evidence docs
milestone                        → new checkpoint MD + JSON
```

Then diff review, secret scan, exact artifact persistence (if packaged), Git commit/push, remote verification, and only then continue.

## 12. Implementation exit

`IMPL-P00-001` may exit only when source/harness/docs/tests are truly author-complete, `IMPL-REM-01…08` are closed or correctly managed, no hidden stub remains in reviewed scope, full required author regression/static checks are clean, exact candidate is durably addressable/reviewable, and `CODE_REVIEW_HANDOFF_READY=true` is evidence-backed.

Only then:

```text
MODE TRANSITION
FROM: IMPLEMENTATION
TO: CODE_REVIEW
TASK: CODE-REVIEW-P00-001
EXIT GATE: CODE_REVIEW_PASS
```
