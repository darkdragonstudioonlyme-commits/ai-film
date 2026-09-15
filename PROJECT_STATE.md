# AI-FILM-SERVER — CANONICAL PROJECT STATE

> **READ THIS FILE FIRST IN A NEW CHAT.**  
> This is the stable, human-readable handoff for the project. It is intentionally detailed so a new chat does not need the previous conversation history.

## 1. Repository identity

- Repository: `darkdragonstudioonlyme-commits/ai-film`
- Default branch: `main`
- Visibility at initialization: **PUBLIC**
- Repository purpose: persistent source, reviewed contracts, implementation snapshots, test evidence, project state and cross-chat handoff.
- Do **not** commit credentials, API keys, private keys, access tokens, production secrets, private model weights, licensed assets, or private customer data.
- Test strings such as `CANARY_SECRET` may exist in unit tests. They are synthetic fixtures, not credentials.

## 2. New-chat bootstrap order

A new chat MUST read these files in this order before changing code:

1. `PROJECT_STATE.md` — this file; canonical current state.
2. `NEXT_WORK_ITEM.md` — exact next implementation task and mode lock.
3. `GIT_WORKFLOW.md` — commit/push discipline and state-update rules.
4. `contracts/AI_VIDEO_SERVER_SINGLE_CHAT_WORKFLOW_BLUEPRINT_V2.md` — authoritative project workflow/requirements.
5. `contracts/PHASE00_INFRA_DESIGN_V2.md`
6. `contracts/PHASE00_ACCEPTANCE_MATRIX_V2.md`
7. `contracts/PHASE00_FAILURE_RECOVERY_PLAN_V2.md`
8. `contracts/PHASE00_EVIDENCE_AND_RESEARCH_REGISTER_V2.md`
9. `contracts/DESIGN_REVIEW_APPROVAL_V2.json`
10. `docs/IMPLEMENTATION_STATUS.md`
11. `docs/REMAINING_IMPLEMENTATION.md`
12. `docs/NATIVE_INTEGRATION_BOUNDARY.md`
13. latest `AI_FILM_PROJECT_STATE_*.json` and `AI_FILM_STATE_CHECKPOINT_*.md`.

If the source tree is not present locally, restore the exact latest implementation delivery from `snapshots/` before coding.

## 3. Mode state machine — current position

```text
ACTIVE MODE: IMPLEMENTATION
PHASE: 00 — Host / WSL
WORK ITEM: IMPL-P00-001
TARGET GATE: CODE_REVIEW_PASS
PHASE GATE: HOST_READY
MODE TRANSITION: NONE
```

Current task status:

```yaml
PROJECT: AI-FILM-SERVER
STATE_VERSION: 12
CURRENT_MODE: IMPLEMENTATION
CURRENT_PHASE: "00 — Host / WSL"
CURRENT_TASK:
  ID: IMPL-P00-001
  STATUS: IN_PROGRESS
  AUTHOR_COMPLETE: false
CURRENT_VERIFIED_DELIVERY: PARTIAL_SOURCE_DROP_DEV6
CODE_REVIEW_HANDOFF_READY: false
QUALIFICATION_ISSUED: false
HOST_READY: NOT_EVALUATED
```

**Do not transition to CODE_REVIEW yet.** The implementation exit condition is not satisfied.

## 4. Authority and precedence

When documents conflict, use this precedence unless a later reviewed artifact explicitly supersedes an earlier one:

1. `contracts/AI_VIDEO_SERVER_SINGLE_CHAT_WORKFLOW_BLUEPRINT_V2.md`
2. Frozen decisions `FD-01…FD-08`
3. Exact Phase 00 Design V2 contracts listed above
4. `contracts/DESIGN_REVIEW_APPROVAL_V2.json`
5. Current implementation source
6. Current test/evidence reports
7. This handoff/state file
8. Historical delivery documents

Implementation is **not allowed** to reinterpret or silently change an approved contract. If code cannot satisfy reviewed behavior, create a real `DESIGN_GAP`, leave the affected implementation scope, and return to design/review.

## 5. Approved design baseline

Design review history:

- `REVIEW-P00-001`: V1 design **FAIL**. Historical only; do not erase.
- `INFRA-P00-002`: Design V2 revision created.
- `REVIEW-P00-002`: exact Design V2 **PASS**.
- Approved Phase 00 design decisions: `D00-01…D00-14` for Phase 00 only.
- Frozen project decisions: `FD-01…FD-08` remain unchanged.
- Approved contract-set digest recorded in prior implementation packages:
  `f259656c48ed24c15bd48da2bb040950ed94d8edcf1473cf6456b96578c933ee`.

The approval opens authoring of Phase 00 code/config/tests/docs. It does **not** establish `HOST_READY`, does not authorize native SITE execution, and does not approve later phases.

## 6. Phase 00 design intent that must remain true

The Phase 00 implementation is safety-first and must preserve existing Windows/WSL state. Important constraints include:

- Correct host/principal/target identity must be established before mutation.
- Existing WSL distributions and data are preserved unless an exact reviewed plan says otherwise.
- Global WSL/shared-runtime changes are treated as wider-impact operations.
- Active operations use one host-global admission/guard model and durable unresolved-state semantics.
- Process exit is not proof of the intended WSL/Windows postcondition.
- Timeout/interruption may create `UNCERTAIN`; do not blind-retry or erase the journal.
- Recovery evidence must exist before C3/shared-runtime changes where required by the design.
- SITE active operations require matching qualification evidence; LAB generation of that evidence is a separate path.
- Terminal/gate evidence must represent the final effective lifecycle state, not a stale pre-restart PASS.
- Restore isolation must be proven before first boot where applicable.
- Evidence completeness, public support-bundle completeness and gate eligibility are distinct concepts.
- `APPLIED != VERIFIED != HOST_READY`.

## 7. Current implementation baseline — `0.1.0.dev6`

Delivery identity:

```text
CURRENT_DELIVERY: PARTIAL_SOURCE_DROP_DEV6
AUTHOR_COMPLETE: false
CODE_REVIEW_HANDOFF_READY: false
IMPLEMENTATION V6 ZIP SHA-256:
41f8a4ed1d80b87bc84981c3cdb2254a3fbc33f21b822580d7e0788b7b404f7e
```

Dev6 is the latest verified author delivery. It is **partial** and **unreviewed**.

### Major implementation capabilities already authored through dev6

The codebase already contains substantial source. Do not re-create these as though they were wholly absent:

- bounded/canonical input handling and plan hashing;
- plan/approval/qualification/trust policy core;
- resource floors, capacity and profile predicates;
- host-global admission concepts, durable fence/read-set/journal behavior;
- Windows identity/filesystem/trust adapters and source-byte pinning components;
- native process supervision ordering with durable witnesses;
- native actuator components for reviewed Phase 00 actions;
- session runner and native session driver;
- operation postcondition observers;
- original mutation-fence recovery;
- pre-mutation detached C0 read recovery;
- live committed-run NOOP revalidation components;
- protected C0 observation capture and observation-to-plan proposal binding;
- primary native CLI dispatch to the concrete factory;
- guest-agent/inventory/content/sentinel observation components;
- terminal sweep components;
- evidence catalog, protected snapshot concepts, support-bundle components;
- snapshot stage identity and exact archive re-observation;
- publication write-ahead/recovery components;
- E17 proposal write-ahead/read-only recovery added in dev6;
- prior-guest/C3 provenance selection from exact hash-linked operation history added in dev6;
- bounded early-failure journal capsule before the first usable snapshot added in dev6;
- registered-LAB route controller contribution and route oracles;
- extensive author regression tests.

Presence of a component is not proof that every reviewed route is fully integrated.

## 8. Verified author test status

Latest verified author results for dev6:

```text
Workspace regression: 666 PASS
Failures:            0
Errors:              0
Skipped:             0
Static author checks: 88 PASS
```

Not executed/established:

```text
Windows/WSL native execution: NOT_RUN
PowerShell native execution:  NOT_RUN
Guest-agent live execution:   NOT_RUN
Live network tests:           NOT_RUN
LAB native suite:             NOT_RUN
SITE validation:              NOT_RUN
Qualification receipt:        NOT_ISSUED
AC00-01…08:                    NOT_EVALUATED
Native T/F/subcase inventory: NOT_RUN
CODE_REVIEW:                   NOT_PERFORMED
HOST_READY:                    NOT_EVALUATED
```

**Never convert author test count into native proof, qualification, validation PASS or HOST_READY.**

## 9. Open implementation items — authoritative working list

All eight full-item REM entries remain OPEN. Completed subcomponents are listed so the next chat does not redo work unnecessarily.

| ID | Source progress through dev6 | Remaining full-item closure |
|---|---|---|
| `IMPL-REM-01` | Native observations plus protected C0 capture and observation-to-proposal binding | Complete effective-profile/eligibility integration across supported contexts and full native factory route flows. |
| `IMPL-REM-02` | Native single guard, durable fence/read set, original-request recovery, logical/physical journal byte checks before reads | Full source integration/fault procedures for journal exhaustion, interrupted readers and lifecycle boundaries; no implicit journal reset. |
| `IMPL-REM-03` | Exact source scripts, native trust/proof graph, per-entry/per-step authorization; pinned execution and selection records | Full bootstrap/executable/dependency byte-trust integration; current/previous source epochs and prior-guest/pre-C3 proof selection. |
| `IMPL-REM-04` | Primary native CLI registered to concrete factory; service/reboot preconditions; first-user wait vs actual receipt | Complete factory execution-path author tests and remaining service/OOBE/restart/resume interaction branches, not merely constructor/routing tests. |
| `IMPL-REM-05` | Mutation-fence recovery plus detached-read recovery; safe non-success cancellation/pause; committed live NOOP | Complete prolonged/multi-stage resume, later request boundaries and remaining recovery/publication interactions. |
| `IMPL-REM-06` | Guest/content/assets/terminal readers and native source-proof consumers | Non-DIRECT transport contexts; full effective-profile/terminal/restore integration and causal native harness assertions. |
| `IMPL-REM-07` | Immutable snapshot stage, field checks, failed capture hook, publication intent/readback recovery, primary support entry; dev6 adds early-failure capsule and E17 recovery | Full nested field semantics, prior pre-C3/checkpoint selection, incomplete/temp bundle-output recovery, applicability and remaining recovery-path integration. |
| `IMPL-REM-08` | Foundations + registered-LAB route controller, route oracles and expanded author regression | Full supported-route/failure preparations/controllers, per-T/F/subcase oracles and end-to-end production-factory integration author tests. |

## 10. Open implementation blockers

### `IMPL-BLOCK-01 — Remaining native integration`

Scope: `REM-01…06`.

Still implement:

- effective profile/eligibility behavior across supported contexts;
- interpreter/executable/dependency byte-trust/bootstrap integration;
- remaining service/OOBE/restart/resume/multi-stage recovery interactions;
- remaining production-factory execution paths and author tests;
- supported non-DIRECT transport adapter path.

Do not describe C0 capture-to-binding, detached-read recovery, primary CLI, or the existing session components as completely missing; they already exist.

### `IMPL-BLOCK-02 — Remaining evidence/recovery semantics`

Scope: `REM-03/06/07`.

Dev6 already has exact hash-linked prior-guest operation observations, early-failure capsule and E17 write-ahead/read-only recovery. Remaining work includes:

- full nested cross-stage field semantics;
- prior **pre-C3/checkpoint** selectors and provenance;
- incomplete/temp support-bundle output recovery;
- remaining E17/recovery-path integration and applicability;
- terminal/restore/effective-profile context integration.

Never infer eligibility merely from a `PASS` envelope, an intended output hash, a preserved file, or a process exit.

### `IMPL-BLOCK-03 — Full causal failure/controller harness`

Scope: `REM-08`.

`run_native_route_tests.py` is a real controller contribution, but the full suite is still missing. Complete:

- causal environment fault preparations;
- cross-principal and concurrency orchestration;
- lifecycle/restart/OOBE cases;
- restore-isolation scenarios;
- all required route/failure oracles for the 86 normative T/F/subcases;
- production-factory integration author tests.

A registry/inventory of 86 cases is not equivalent to 86 executable causal tests.

## 11. Exact next implementation order

Continue **in IMPLEMENTATION mode** in this order unless source evidence reveals a genuine reviewed-contract problem:

1. Complete executable/dependency trust and remaining effective-profile behavior.
2. Complete remaining service/OOBE/restart/resume/factory branches.
3. Complete prior pre-C3/checkpoint and nested cross-stage E00 semantics.
4. Complete incomplete/temp publication recovery and remaining E17 recovery integration.
5. Complete non-DIRECT transport support required by the reviewed profile.
6. Finish causal supported-route/failure controller procedures for the 86-case inventory.
7. Add production-factory integration author tests using explicit author test ports only.
8. Run complete workspace regression and static checks.
9. Update `docs/IMPLEMENTATION_STATUS.md`, `docs/REMAINING_IMPLEMENTATION.md`, traceability, `PROJECT_STATE.md`, `NEXT_WORK_ITEM.md`, checkpoint JSON/MD and evidence reports.
10. Secret scan and diff review.
11. Commit and push exact candidate.
12. Only when `AUTHOR_COMPLETE=true`, `CODE_REVIEW_HANDOFF_READY=true`, no hidden stub remains and author regression is clean: create the mode transition to `CODE_REVIEW` / `CODE-REVIEW-P00-001`.

## 12. Forbidden actions in current mode

While `IMPL-P00-001` remains in IMPLEMENTATION:

- Do not change `FD-*`, `D00-*` or public/reviewed contracts.
- Do not lower acceptance criteria or delete failure cases to make tests pass.
- Do not run native Windows/WSL/LAB/SITE/guest/live-network operations during authoring unless a later explicit authorized work item changes that rule.
- Do not register fixture/fake ports as the production/active CLI backend.
- Do not treat fixture flags, inventory, process exit or author test counts as proof.
- Do not erase unresolved journal/fence/read state to recover from an implementation problem.
- Do not self-approve code review, qualification, `HOST_READY` or production readiness.
- Do not request user host data as a substitute for writing missing source.
- Do not create a fake `DESIGN_GAP` merely because implementation is incomplete.

## 13. Design-gap rule

If and only if implementation demonstrates that exact reviewed behavior cannot be implemented without changing the approved contract:

```text
DESIGN_GAP
ID:
DISCOVERED_IN_MODE: IMPLEMENTATION
PROBLEM:
EVIDENCE:
AFFECTED_CONTRACT:
OPTIONS:
RECOMMENDATION:
STATUS: OPEN
```

Stop implementation for the affected scope and return through the appropriate design/review mode. Implementation must never close its own design gap.

Current state: **no open design gap has been established**.

## 14. Repository persistence rule

From repository initialization onward, Git is a mandatory persistence layer for cross-chat continuity.

For each coherent implementation increment:

```text
implement coherent part
→ run relevant author tests
→ run full workspace regression before delivery commit
→ update evidence/docs/state
→ inspect diff
→ secret scan
→ commit
→ push to main (unless a future reviewed workflow introduces branches/PRs)
→ verify remote commit SHA
→ record the commit in PROJECT_STATE.md / checkpoint
→ only then start the next coherent implementation part
```

Do not call a local change durable until the corresponding remote commit is verified.

See `GIT_WORKFLOW.md` for the full policy.

## 15. Cross-chat recovery procedure

If a new chat has no local source directory:

1. Read this file and `NEXT_WORK_ITEM.md` from GitHub.
2. Inspect latest commits on `main`.
3. Obtain the exact implementation snapshot listed in this file from `snapshots/`.
4. Verify its SHA-256 before extraction.
5. Extract into a fresh workspace.
6. Compare the extracted `MANIFEST.json` and current repository state.
7. Re-run the recorded workspace tests before modifying source if the environment supports them.
8. Continue only the open work listed here.

Do not reconstruct the source from conversational summaries when an exact repository snapshot exists.

## 16. Milestone history needed for context

- V1 master state: project initialized; Phase 00 selected.
- Phase 00 Design V1 authored.
- `REVIEW-P00-001`: FAIL with six findings.
- Design V2 closed the required changes.
- `REVIEW-P00-002`: PASS exact V2.
- Implementation dev1: policy/core foundations; partial.
- dev2: native identity/trust/guard/supervision foundations; partial.
- dev3: native session/evidence integration; partial.
- dev4: original-fence diagnostics/cancel/pause + live NOOP; partial.
- dev5: C0 binding, detached-read recovery, primary native CLI, route-controller contribution; partial.
- dev6: E17 recovery, prior-guest provenance selection, early-failure capture; **current verified baseline; partial**.
- Repository initialized on GitHub to make source/state durable across chats.

Historical versions are evidence, not authorization to skip current open items.

## 17. Definition of implementation exit for this work item

`IMPL-P00-001` may exit IMPLEMENTATION only when all are true:

- source/harness/docs/test candidate is author-complete;
- all `IMPL-REM-01…08` are actually closed or a genuine blocker has been managed according to the mode system;
- no known hidden native stub remains in the supported reviewed scope;
- full intended primary CLI path is wired to real production components, not fixtures;
- supported failure/controller harness is implemented to the reviewed scope;
- workspace regression and static checks pass;
- traceability and evidence are updated;
- candidate is committed and pushed with an exact remote SHA;
- `CODE_REVIEW_HANDOFF_READY=true` is justified by source state, not by optimism.

Then and only then:

```text
MODE TRANSITION
FROM: IMPLEMENTATION
TO: CODE_REVIEW
TASK: CODE-REVIEW-P00-001
EXIT GATE: CODE_REVIEW_PASS
```

## 18. Prompt for a new chat

Paste this after connecting the GitHub repository, if needed:

```text
Use repository darkdragonstudioonlyme-commits/ai-film as the persistent project source of truth.
Read PROJECT_STATE.md and NEXT_WORK_ITEM.md first, then the authoritative Blueprint and exact approved Phase 00 V2 contracts referenced there.
Do not rely on previous chat history.
Continue the project under the MODE STATE MACHINE.
Current expected mode is IMPLEMENTATION, Phase 00, work item IMPL-P00-001, unless the repository state says otherwise.
Do not skip gates, do not change reviewed contracts in implementation, and do not claim native validation from author tests.
Before starting new implementation, verify the latest remote commit and exact snapshot/hash.
After every coherent implementation increment: test, update state/docs/evidence, secret-scan, commit, push, verify SHA, then continue.
```

## 19. Current target state summary

```yaml
PROJECT: AI-FILM-SERVER
STATE_VERSION: 12
CURRENT_MODE: IMPLEMENTATION
CURRENT_PHASE: "00 — Host / WSL"
CURRENT_BASELINE:
  REQUIREMENTS: Blueprint_V2
  REVIEWED_DESIGN: "Exact Phase00 V2 — REVIEW-P00-002 PASS"
  SOURCE: "0.1.0.dev6 — partial, unreviewed"
  VERIFIED_INFRA: NOT_ESTABLISHED
  PROMOTED_BASELINE: NONE
CURRENT_TASK: IMPL-P00-001
TARGET_GATE: CODE_REVIEW_PASS
PHASE_GATE: HOST_READY
AUTHOR_COMPLETE: false
CODE_REVIEW_HANDOFF_READY: false
OPEN_IMPLEMENTATION_ITEMS: "IMPL-REM-01…08"
IMPLEMENTATION_BLOCKERS: "IMPL-BLOCK-01…03"
OPEN_FINDINGS: []
OPEN_DESIGN_GAPS: []
OPEN_VALIDATION_FAILURES: []
LAST_TEST_RESULT:
  WORKSPACE: "666 PASS / 0 failure / 0 error / 0 skip"
  STATIC: "88 PASS"
  NATIVE_WINDOWS_WSL: NOT_RUN
  LAB: NOT_RUN
  SITE: NOT_RUN
LAST_REVIEW_RESULT:
  DESIGN: "REVIEW-P00-002 PASS exact V2"
  CODE: NOT_PERFORMED
QUALIFICATION_ISSUED: false
HOST_READY: NOT_EVALUATED
NEXT_MODE: IMPLEMENTATION
NEXT_ACTION: "Continue IMPL-P00-001 using NEXT_WORK_ITEM.md"
```
