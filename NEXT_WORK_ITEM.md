# NEXT WORK ITEM — IMPL-P00-001

```yaml
WORK_ITEM_ID: IMPL-P00-001
MODE: IMPLEMENTATION
PHASE: "00 — Host / WSL"
STATUS: IN_PROGRESS
CURRENT_DELIVERY: PARTIAL_SOURCE_DROP_DEV7
ENTRY_GATE: DESIGN_REVIEW_PASS
ENTRY_GATE_STATUS: SATISFIED_EXACT_V2
TARGET_GATE: CODE_REVIEW_PASS
PHASE_GATE: HOST_READY
MODE_TRANSITION_NOW: NONE
DOCUMENTATION_SYNC: MANDATORY
LIVING_MEMORY: PROJECT_MEMORY.md
WSL_WORKSPACE_READY: true
WSL_WORKSPACE_ROOT: /home/dragon/ai-film-dev
```

## Exact recovery anchor

```yaml
PACKAGE: IMPL-P00-001_IMPLEMENTATION_PACKAGE_V7.zip
SIZE_BYTES: 1119033
SHA256: 63f9a8ce948ff0bb80de5d0dc37cc75a0c37723579ac1930098cca7e4de49312
DRIVE_FILE_ID: 1lplraFWFeDhdV6jl4aJgJOTpfjBoXHlH
RAW_REDOWNLOAD_SHA_VERIFIED: true
```

Prepared WSL source:

```text
/home/dragon/ai-film-dev/source-dev7
local Git baseline: b937649c1344baef3eb7b221ddd0347f5954ed85
```

Before source changes in a fresh workspace, restore/verify the exact V7 artifact or use the prepared WSL source after confirming its local Git status and baseline tests.

## Immediate goal

Complete the next coherent lifecycle/factory increment without changing exact approved Design V2 behavior.

## Lifecycle increment — required order

1. Read exact Phase00 V2 lifecycle/recovery contracts, `docs/REMAINING_IMPLEMENTATION.md`, `docs/NATIVE_INTEGRATION_BOUNDARY.md`, current plan generation, session driver, actuator, transition/recovery code and relevant tests.
2. Analyze the ENGINE route interaction between:
   - `ENABLE_PREREQUISITES`;
   - `INSTALL_RUNTIME`;
   - process/native result `3010 → AWAITING_REBOOT`;
   - explicit `AWAIT_OWNER_RESTART` plan step;
   - recovery/resume behavior across an actual host reboot.
3. Determine with code/contract evidence whether the current structure intentionally represents two distinct lifecycle boundaries or can accidentally require a second restart.
4. If implementation is wrong while reviewed behavior is clear, patch implementation only.
5. If correct implementation would require changing reviewed behavior, stop affected scope and create a genuine DESIGN_GAP instead of changing the contract in IMPLEMENTATION.
6. Complete directly coupled service/OOBE/restart/resume/factory branches where contract behavior is unambiguous.
7. Add targeted positive and negative author tests for restart/OOBE/resume/reconciliation ordering and no-replay behavior.
8. Run targeted tests then full workspace regression/static checks.
9. Run Documentation Sync Gate; persist all reusable lifecycle/recovery lessons in `PROJECT_MEMORY.md`.
10. Package exact next delivery, upload by file reference, raw re-download/hash verify, update Git state/docs and verify remote persistence before starting another increment.

## Following implementation increments

After the lifecycle increment is durably persisted:

- prior pre-C3/checkpoint selection and nested cross-stage E00 semantics;
- incomplete/temp bundle publication recovery and remaining E17 recovery applicability/integration;
- reviewed non-DIRECT transport support where required;
- full causal supported-route/failure controller procedures for the 86 normative T/F/subcases;
- production-factory integration author tests using explicit author test ports.

Do not combine independent blockers into one patch if they can be closed/tested/persisted separately.

## Already authored through dev7 — do not redo as absent

Dev6 capabilities remain as recorded in `PROJECT_STATE.md`, plus dev7:

- executable-policy pins scoped to host/build/contract;
- exact executable path/size/SHA-256 verification under pinned filesystem handles;
- administrative owner/writer constraints;
- mandatory production-supervisor executable trust before child creation;
- executable policy reference/hash/size/kind in durable process witness;
- native binding requires `executable_policy_ref`;
- authority refresh reloads executable trust and validates effective profile;
- production factory enables executable trust by default;
- verified author baseline: `673 PASS`, static `90 PASS`.

Do not overclaim: guest interpreter/rootfs provenance and remaining bootstrap/dependency trust are still open.

## WSL authoring workflow

When using Desktop Commander:

```bash
source /home/dragon/ai-film-dev/env.sh
/home/dragon/ai-film-dev/test.sh
```

Read `WORKSPACE_WSL.md` first. The current WSL venv is isolated but intentionally has no pip because dev7 has no external dependencies and non-interactive sudo cannot install `python3.12-venv`.

Direct WSL GitHub push authentication is not configured. Use local Git for source diff/rollback and the connected GitHub connector for remote writes until a secure WSL auth setup is explicitly performed.

## Forbidden

- Change FD/D00/public/reviewed contracts or lower acceptance.
- Execute Phase00 native Windows/WSL/LAB/SITE/guest/live-network provisioning/validation during authoring.
- Register fixture/fake active CLI backends.
- Treat process exit, fixture flags, inventory, author-test count, or evidence-envelope labels as actual native proof.
- Delete unresolved journal/fence/read state to recover.
- Self-approve code review, qualification, HOST_READY, or production readiness.
- Ask for user host data as a substitute for remaining source implementation.
- Continue from a source tree whose delivery identity/local Git state is unknown.
- Store GitHub credentials/PATs in plaintext workspace files.

## Living-memory obligation

At the end of every meaningful increment automatically evaluate:

```text
state changed?              → PROJECT_STATE.md
next work changed?          → NEXT_WORK_ITEM.md
reusable learning found?    → PROJECT_MEMORY.md
workspace changed?          → WORKSPACE_WSL.md + PROJECT_MEMORY.md
workflow improved?          → GIT_WORKFLOW.md + PROJECT_MEMORY.md
implementation scope moved? → implementation/remaining/traceability/evidence docs
milestone reached?          → new checkpoint MD + JSON
```

## Design-gap rule

If implementation evidence demonstrates that reviewed behavior itself must change, record a genuine DESIGN_GAP and leave the affected implementation scope before redesign. Do not create a design gap merely because source work is incomplete.

## Exit condition

A full author-complete source/harness/docs/test candidate exists; all `IMPL-REM-01…08` are actually closed or properly managed under the mode system; no hidden stub remains; required author regression/static checks are clean; exact candidate identity is durably persisted and reviewable; canonical docs/state are synchronized.

Only then:

```text
MODE TRANSITION
FROM: IMPLEMENTATION
TO: CODE_REVIEW
TASK: CODE-REVIEW-P00-001
EXIT GATE: CODE_REVIEW_PASS
```
