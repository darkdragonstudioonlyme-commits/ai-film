# AI-FILM-SERVER — CANONICAL PROJECT STATE V15

> **READ THIS FILE FIRST IN EVERY NEW CHAT.**  
> Current operational truth only. Reusable lessons live in `PROJECT_MEMORY.md`; immutable history lives in versioned checkpoints.

## 1. Fast resume snapshot

```yaml
PROJECT: AI-FILM-SERVER
STATE_VERSION: 15
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
CURRENT_VERIFIED_DELIVERY: "0.1.0.dev7 / PARTIAL_SOURCE_DROP_DEV7"
AUTHOR_COMPLETE: false
CODE_REVIEW_HANDOFF_READY: false

DEV7_PACKAGE: IMPL-P00-001_IMPLEMENTATION_PACKAGE_V7.zip
DEV7_SIZE_BYTES: 1119033
DEV7_SHA256: 63f9a8ce948ff0bb80de5d0dc37cc75a0c37723579ac1930098cca7e4de49312
DEV7_DRIVE_FILE_ID: 1lplraFWFeDhdV6jl4aJgJOTpfjBoXHlH
RAW_REDOWNLOAD_SHA_VERIFIED: true

WORKSPACE_AUTHOR_TESTS: "673 PASS / 0 failure / 0 error / 0 skip"
STATIC_AUTHOR_CHECKS: "90 PASS"
NATIVE_WINDOWS_WSL: NOT_RUN
LAB: NOT_RUN
SITE: NOT_RUN
QUALIFICATION_ISSUED: false
HOST_READY: NOT_EVALUATED

DEV_WORKSPACE_READY: true
WSL_WORKSPACE_ROOT: /home/dragon/ai-film-dev
CANONICAL_REPO_CLONE: /home/dragon/ai-film-dev/repo
DEV7_SOURCE_DIR: /home/dragon/ai-film-dev/source-dev7
DEV7_LOCAL_GIT_BASELINE: b937649c1344baef3eb7b221ddd0347f5954ed85
DEV_VENV: /home/dragon/ai-film-dev/.venv
DIRECT_WSL_GITHUB_PUSH_AUTH: NOT_CONFIGURED

AUTO_DOCUMENTATION_SYNC: true
NO_SILENT_KNOWLEDGE: true
LIVING_MEMORY_FILE: PROJECT_MEMORY.md
WORKSPACE_DOC: WORKSPACE_WSL.md
NEXT_ACTION: "Continue IMPL-P00-001 from dev7: analyze/complete service-OOBE-restart-resume-factory lifecycle behavior, then persist the next coherent increment."
```

**Do not transition to CODE_REVIEW.** Dev7 is a verified author delivery but the work item remains partial.

## 2. Persistence and recovery model

The project uses explicit hybrid persistence:

- **GitHub** — canonical current state, living memory, workflow, next work, review records and durable text/change ledger.
- **Google Drive raw artifact storage** — byte-exact packaged delivery recovery anchor.
- **WSL local Git** — local diff/rollback during authoring; it is not remote approval or persistence by itself.

Every packaged delivery used as a recovery baseline must be identified by file name, size and SHA-256 and must be re-downloaded raw and re-hashed after upload.

Current exact delivery anchor:

```text
IMPL-P00-001_IMPLEMENTATION_PACKAGE_V7.zip
Drive file ID: 1lplraFWFeDhdV6jl4aJgJOTpfjBoXHlH
Size: 1119033
SHA-256: 63f9a8ce948ff0bb80de5d0dc37cc75a0c37723579ac1930098cca7e4de49312
```

## 3. WSL development workspace

Current prepared workspace:

```text
/home/dragon/ai-film-dev
```

Layout:

```text
repo/         canonical GitHub state/handoff clone
source-dev7/  exact dev7 extracted source + local Git baseline
artifacts/    exact downloaded delivery archives
.venv/        isolated Python 3.12 author-test environment
env.sh        enter environment
test.sh       workspace regression + static checks
```

Read `WORKSPACE_WSL.md` before using Desktop Commander or modifying the WSL source tree.

Verified environment result after setup:

```text
673 workspace tests PASS
90 static checks PASS
source digest 93e28ed77c132ad032cf8bf951e7d51627f6f8d007aa4179bb5696f0d6f1c6e8
test digest   1c79354e63bdc76de157621547a7f92eb97d98fa90a6e53856619861103a3799
```

The isolated venv currently has no pip because Ubuntu `python3.12-venv`/ensurepip is not installed and sudo requires interactive authorization. Dev7 has no external Python dependencies, so `.pth` bindings to exact `src/` and `tests/` are sufficient for the present author baseline. See `MEM-20260915-013`.

Direct WSL `git push` is not currently authenticated. Clone/fetch/local commits work. Remote writes continue through the connected GitHub connector until an explicit secure WSL authentication setup is performed. See `MEM-20260915-014`.

## 4. New-chat bootstrap

A new chat should:

1. Read this file.
2. Read `NEXT_WORK_ITEM.md`.
3. Scan relevant active entries in `PROJECT_MEMORY.md`.
4. Read `WORKSPACE_WSL.md` if Desktop Commander/WSL will be used.
5. Verify current GitHub `main` head.
6. Read `GIT_WORKFLOW.md` before persistent changes.
7. Verify the current exact delivery artifact identity before restoring a fresh workspace.
8. Run `/home/dragon/ai-film-dev/test.sh` before source changes when the prepared WSL workspace is available.
9. Continue only the current recorded implementation increment.

Do not depend on previous chat history.

## 5. Authority and approved baseline

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

## 6. Phase00 implementation invariants

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

## 7. Dev7 delta and verified evidence

Dev7 completed one coherent author increment:

- executable-policy pins scoped to host/build/contract;
- exact executable path/size/SHA-256 verification under pinned handles;
- administrative owner/writer constraints;
- mandatory production-supervisor executable trust before child creation;
- process witnesses record policy reference/hash/size/kind;
- native bindings require `executable_policy_ref`;
- authority refresh reloads executable policy and checks effective profile;
- production factory enables mandatory executable trust.

Do not overclaim: guest interpreter/rootfs provenance and remaining bootstrap/dependency trust are still open.

Verified evidence:

```yaml
AUTHOR_WORKSPACE_REGRESSION: "673 PASS / 0 failures / 0 errors / 0 skipped"
STATIC_AUTHOR_CHECKS: "90 PASS"
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

All full-item REMs remain OPEN, but dev7 advanced `REM-01/03/04` subcomponents.

- `IMPL-REM-01`: remaining effective-profile/eligibility integration and full native-factory route flows.
- `IMPL-REM-02`: exhaustion/interrupted-reader/lifecycle journal procedures without implicit reset.
- `IMPL-REM-03`: remaining guest interpreter/rootfs/bootstrap dependency trust, source epochs, prior pre-C3/checkpoint proof selection.
- `IMPL-REM-04`: service/OOBE/restart/resume and production-factory execution-path author tests.
- `IMPL-REM-05`: prolonged/multi-stage resume/later request/recovery-publication interactions.
- `IMPL-REM-06`: non-DIRECT transport and effective-profile/terminal/restore integration.
- `IMPL-REM-07`: nested cross-stage semantics, prior pre-C3/checkpoint selection, temp/incomplete publication recovery and remaining E17 integration.
- `IMPL-REM-08`: causal preparations/controllers/oracles for normative 86-case inventory plus production-factory integration tests.

Open blocker groups remain `IMPL-BLOCK-01…03`; they are source/integration/harness work, not missing user data.

## 9. Exact current implementation order

Next coherent increment:

1. inspect reviewed lifecycle contract and current ENGINE plan/recovery behavior;
2. determine whether `AWAIT_OWNER_RESTART` plus `3010 → AWAITING_REBOOT` can cause duplicate restart semantics or whether the current two-stage behavior is intentional;
3. complete service/OOBE/restart/resume/factory branches only where reviewed behavior is clear;
4. add targeted positive/negative author tests;
5. run full author regression/static checks;
6. Documentation Sync Gate;
7. package exact delivery, upload raw artifact, re-download/hash verify;
8. update Git state/memory/next work and verify remote persistence.

Then proceed to prior pre-C3/checkpoint + nested E00, publication/E17 recovery, non-DIRECT transport, causal 86-case suite and production-factory integration tests as separate increments where practical.

See `NEXT_WORK_ITEM.md` for executable detail.

## 10. Forbidden in current mode

- no FD/D00/public-contract changes;
- no acceptance lowering;
- no Windows/WSL/LAB/SITE/guest/live-network validation/provisioning during authoring;
- no fixture/fake active production backend;
- no process-exit/fixture/test-count/envelope-label substitution for native proof;
- no deletion of unresolved durable state as a shortcut;
- no self-approved code review/qualification/HOST_READY;
- no user host data requested as substitute for missing implementation;
- no fabricated DESIGN_GAP for incomplete source;
- no unverified source restoration;
- no plaintext GitHub credentials/PATs in WSL;
- no useful reusable knowledge left only in chat.

## 11. Documentation Sync Gate

At every meaningful increment, automatically update as applicable:

```text
state/gates/tests/blockers       → PROJECT_STATE.md
exact next work                  → NEXT_WORK_ITEM.md
reusable discovery/optimization  → PROJECT_MEMORY.md
workspace/environment change     → WORKSPACE_WSL.md + PROJECT_MEMORY.md
workflow improvement             → GIT_WORKFLOW.md + PROJECT_MEMORY.md
implementation progress          → implementation/remaining/traceability/evidence docs
milestone                        → new checkpoint MD + JSON
```

Then diff review, secret scan, exact artifact persistence if packaged, Git commit/push, remote verification, and only then continue.

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
