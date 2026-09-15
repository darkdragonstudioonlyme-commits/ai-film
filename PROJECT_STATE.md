# AI-FILM-SERVER — CANONICAL PROJECT STATE V13

> **READ THIS FILE FIRST IN EVERY NEW CHAT.**  
> This file contains the current operational truth only: where the project is, what is approved, what is verified, what is blocked and what happens next.
>
> Reusable lessons/optimizations live in `PROJECT_MEMORY.md`. Historical milestone snapshots live in `AI_FILM_STATE_CHECKPOINT_Vn.md` and must not be mistaken for current state.

---

## 1. Fast resume snapshot

```yaml
PROJECT: AI-FILM-SERVER
STATE_VERSION: 13
REPOSITORY: darkdragonstudioonlyme-commits/ai-film
DEFAULT_BRANCH: main

CURRENT_MODE: IMPLEMENTATION
CURRENT_PHASE: "00 — Host / WSL"
CURRENT_TASK: IMPL-P00-001
TASK_STATUS: IN_PROGRESS_PAUSED_FOR_GIT_PERSISTENCE
TARGET_GATE: CODE_REVIEW_PASS
PHASE_GATE: HOST_READY
MODE_TRANSITION: NONE

REQUIREMENTS_BASELINE: "AI VIDEO SERVER — SINGLE CHAT WORKFLOW BLUEPRINT V2"
REVIEWED_DESIGN: "Phase00 exact Design V2 — REVIEW-P00-002 PASS"
CURRENT_VERIFIED_DELIVERY: "0.1.0.dev6 / PARTIAL_SOURCE_DROP_DEV6"
AUTHOR_COMPLETE: false
CODE_REVIEW_HANDOFF_READY: false

EXACT_DEV6_SOURCE_MIRRORED: false
SOURCE_IMPORT_VERIFIED: false
IMPLEMENTATION_MAY_RESUME: false

WORKSPACE_AUTHOR_TESTS: "666 PASS / 0 failure / 0 error / 0 skip"
STATIC_AUTHOR_CHECKS: "88 PASS"
NATIVE_WINDOWS_WSL: NOT_RUN
LAB: NOT_RUN
SITE: NOT_RUN
QUALIFICATION_ISSUED: false
HOST_READY: NOT_EVALUATED

AUTO_DOCUMENTATION_SYNC: true
LIVING_MEMORY_FILE: PROJECT_MEMORY.md
GIT_POLICY: GIT_WORKFLOW.md
NEXT_ACTION: "Resolve exact dev6 Git persistence per SOURCE_IMPORT_STATUS.md; synchronize state; then resume NEXT_WORK_ITEM.md."
```

**Do not transition to CODE_REVIEW. Do not author new implementation while `IMPLEMENTATION_MAY_RESUME=false`.**

---

## 2. Canonical document model

The documentation system is intentionally layered to reduce duplicate reading and prevent drift.

| File | Canonical responsibility |
|---|---|
| `PROJECT_STATE.md` | **Current operational truth** — mode, phase, baseline, blockers, gate/test/review status, next action |
| `NEXT_WORK_ITEM.md` | **Exact next executable work** — order, scope, inputs, forbidden actions, exit condition |
| `PROJECT_MEMORY.md` | **Accumulated reusable knowledge** — discoveries, optimizations, tooling lessons, risks, test/security/process lessons |
| `GIT_WORKFLOW.md` | **Standing persistence + automatic documentation synchronization protocol** |
| `CHAT_HANDOFF.md` | Compact bootstrap prompt/template; not another state database |
| `SOURCE_IMPORT_STATUS.md` | Temporary exact-source bootstrap status while the current persistence prerequisite is open |
| `AI_FILM_STATE_CHECKPOINT_Vn.md` + matching JSON | Immutable milestone/history snapshot |
| Git commits/diffs | Exact change history; do not duplicate full diffs in current-state MD |

### Automatic documentation rule

The project now has a standing **no-silent-knowledge** rule.

If work discovers a reusable optimization, constraint, failure pattern, tooling behavior, safety lesson, test oracle, risk or important clarification, the assistant must update `PROJECT_MEMORY.md` automatically. If that discovery changes current state, next work or workflow, update the corresponding canonical MD in the same increment.

No meaningful increment is considered durable until the Documentation Sync Gate in `GIT_WORKFLOW.md` has been evaluated.

---

## 3. New-chat bootstrap

A new chat should minimize unnecessary context while still recovering exact state:

1. Read `PROJECT_STATE.md` completely.
2. Read `NEXT_WORK_ITEM.md` completely.
3. Read relevant active entries in `PROJECT_MEMORY.md`.
4. Query/verify the current remote `main` head.
5. Read `GIT_WORKFLOW.md` before making persistent changes.
6. Read conditional files referenced by current state — currently `SOURCE_IMPORT_STATUS.md`.
7. Read the authoritative Blueprint/approved contracts required by the current task after the exact source seed makes them available in the repository/source tree.
8. Do not depend on the previous chat transcript.

If an old chat transcript and the latest verified repository state conflict, prefer the authoritative/reviewed artifacts plus latest verified repository state/evidence.

---

## 4. Current persistence prerequisite

Implementation is paused because exact dev6 source bytes have not yet been accepted as a verified GitHub mirror.

```yaml
PERSISTENCE_PREREQUISITE: OPEN
PERSISTENCE_BLOCKER_KIND: REPOSITORY_PERSISTENCE
EXACT_DEV6_SOURCE_MIRRORED: false
SOURCE_IMPORT_VERIFIED: false
IMPLEMENTATION_MAY_RESUME: false
DESIGN_GAP: false
VALIDATION_FAILURE: false
CODE_REVIEW_FINDING: false
```

This does **not** mean dev6 implementation did not exist. Dev6 is the verified author delivery; only its byte-preserving Git persistence is incomplete.

Repository bootstrap established that:

- GitHub connector access and text documentation commits work.
- State/handoff Markdown is durable on `main`.
- Experimental source/archive import paths were checked against dev6 identities.
- At least one experimental copied blob was not byte-identical to local dev6.
- Experimental `src/`/`snapshots/` trees were removed instead of being accepted as a false baseline.

Read `SOURCE_IMPORT_STATUS.md` and memory entry `MEM-20260915-002` before resolving this prerequisite.

**Required before new implementation:** exact byte-preserving seed + manifest/hash verification + state update + commit/push/remote verification.

---

## 5. Authority and precedence

When artifacts conflict, use this order unless a later reviewed artifact explicitly supersedes an earlier one:

1. `AI VIDEO SERVER — SINGLE CHAT WORKFLOW BLUEPRINT V2`.
2. Frozen decisions `FD-01…FD-08`.
3. Exact Phase 00 Design V2 contracts.
4. `REVIEW-P00-002` approval of exact Design V2.
5. Exact implementation source candidate.
6. Actual test/evidence reports.
7. Current `PROJECT_STATE.md` operational handoff.
8. `PROJECT_MEMORY.md` reusable knowledge.
9. Historical checkpoints/delivery summaries.

A memory entry does not approve architecture, pass a gate or replace evidence.

IMPLEMENTATION must not redesign, change reviewed/public contracts, lower acceptance criteria or self-approve gates.

If implementation proves a reviewed behavior cannot be implemented without changing the contract, create a genuine DESIGN_GAP and leave affected implementation scope before redesign.

---

## 6. Approved design baseline

History relevant to current work:

```text
Phase00 Design V1
→ REVIEW-P00-001
→ FAIL: DR-P00-001…006
→ Design V2 revision
→ REVIEW-P00-002
→ PASS exact V2
```

Approved status:

```yaml
FROZEN_DECISIONS: "FD-01…FD-08 unchanged"
APPROVED_PHASE00_DESIGN_DECISIONS: "D00-01…D00-14"
DESIGN_REVIEW_PASS: SATISFIED_EXACT_V2
APPROVED_CONTRACT_SET_DIGEST: f259656c48ed24c15bd48da2bb040950ed94d8edcf1473cf6456b96578c933ee
```

Design approval opens authoring for the exact Phase 00 scope. It does not establish implementation completeness, native validation, qualification or `HOST_READY`.

---

## 7. Phase 00 invariants implementation must preserve

- Correct host/principal/target identity before mutation.
- Preserve existing Windows/WSL distributions/data unless the exact reviewed plan authorizes change.
- Treat shared WSL runtime/global effects as host-wide impact where applicable.
- Use host-global admission semantics and durable unresolved-state handling for active operations.
- Native process exit is not proof of Windows/WSL postcondition success.
- Timeout/interruption may produce `UNCERTAIN`; do not blind-retry or erase durable state.
- Recovery/protection evidence must exist before relevant C3/shared-runtime mutation.
- SITE active operations require matching qualification evidence; LAB evidence production is a separate path.
- Terminal/gate assertions must correspond to final effective lifecycle state, not stale pre-restart observations.
- Restore isolation must be proven before first boot where the reviewed route requires it.
- Evidence-record completeness, public support-bundle completeness and gate eligibility are distinct.
- `APPLIED != VERIFIED != HOST_READY`.
- No destructive default recovery such as unregistering an existing distro just to make retry succeed.

---

## 8. Current verified implementation baseline — dev6

```yaml
IMPLEMENTATION_VERSION: 0.1.0.dev6
DELIVERY_STATUS: PARTIAL_SOURCE_DROP_DEV6
AUTHOR_COMPLETE: false
CODE_REVIEWED: false
VERIFIED_INFRA_BASELINE: NOT_ESTABLISHED
PROMOTED_BASELINE: NONE
```

Verified artifact identity:

```text
IMPL-P00-001_IMPLEMENTATION_PACKAGE_V6.zip
SHA-256:
41f8a4ed1d80b87bc84981c3cdb2254a3fbc33f21b822580d7e0788b7b404f7e
```

### Already authored through dev6 — do not redo as if absent

- bounded/canonical input handling and plan hashing;
- approval/qualification/trust policy core;
- resource floors/capacity/profile predicates;
- host-global admission concepts and durable fence/read-set/journal behavior;
- Windows identity/filesystem/trust adapters and source-byte pinning components;
- native process supervision with durable witnesses;
- reviewed Phase 00 actuator components;
- session runner/native driver and postcondition observers;
- original mutation-fence recovery;
- detached C0-read recovery before mutation fence;
- committed-run live NOOP revalidation components;
- protected C0 observation capture → plan proposal binding;
- primary native CLI dispatch to concrete factory;
- guest inventory/content/sentinel components;
- terminal sweep components;
- evidence catalog/protected snapshot/support-bundle components;
- snapshot stage identity and exact final archive re-observation;
- publication write-ahead/recovery components;
- E17 proposal write-ahead/read-only recovery;
- prior-guest/C3 provenance selection from exact hash-linked operation history;
- bounded early-failure journal capsule before first usable snapshot;
- registered-LAB route-controller contribution/oracles;
- extensive author regression tests.

Presence of a component does not imply full reviewed-route integration or native validation.

---

## 9. Verified evidence baseline

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

Reusable rule: author regression/static results are not qualification/native-validation/HOST_READY evidence. See `MEM-20260915-003`.

---

## 10. Open implementation items

All eight full-item entries remain OPEN.

| ID | Authored progress through dev6 | Remaining closure |
|---|---|---|
| `IMPL-REM-01` | Native observations + protected C0 capture/observation-to-proposal binding | Effective-profile/eligibility integration across supported contexts and full native-factory route flows |
| `IMPL-REM-02` | Native guard, durable fence/read set, original-request recovery, journal byte checks | Exhaustion/interrupted-reader/lifecycle source integration without implicit journal reset |
| `IMPL-REM-03` | Source scripts, native trust/proof graph, per-entry/per-step authorization, pinned records | Bootstrap/executable/dependency byte-trust, source epochs, prior pre-C3/checkpoint proof selection |
| `IMPL-REM-04` | Primary native CLI to concrete factory; service/reboot preconditions; first-user wait vs receipt | Remaining service/OOBE/restart/resume interactions and production-factory execution-path author tests |
| `IMPL-REM-05` | Mutation-fence + detached-read recovery; safe cancellation/pause; live NOOP | Prolonged/multi-stage resume, later request boundaries, remaining recovery/publication interactions |
| `IMPL-REM-06` | Guest/content/assets/terminal readers and native proof consumers | Non-DIRECT transport + effective-profile/terminal/restore integration + causal harness assertions |
| `IMPL-REM-07` | Snapshot stage/field checks, failure capture hook, publication intent/readback, E17 recovery, prior-guest provenance, early-failure capsule | Nested cross-stage semantics, prior pre-C3/checkpoint selectors, temp/incomplete output recovery, applicability/recovery integration |
| `IMPL-REM-08` | Foundation + registered-LAB route controller/oracles + regression | Full supported-route/failure preparations/controllers, per-T/F/subcase oracles and production-factory integration author tests |

---

## 11. Open implementation blockers

### IMPL-BLOCK-01 — Remaining native integration

- effective-profile/eligibility behavior across supported contexts;
- interpreter/executable/dependency byte-trust/bootstrap integration;
- remaining service/OOBE/restart/resume/multi-stage recovery interactions;
- remaining production-factory execution paths/author tests;
- supported non-DIRECT transport adapter path.

### IMPL-BLOCK-02 — Remaining evidence/recovery semantics

- full nested cross-stage field semantics;
- prior pre-C3/checkpoint selection/provenance;
- incomplete/temp support-bundle output recovery;
- remaining E17/recovery applicability/integration;
- terminal/restore/effective-profile context integration.

### IMPL-BLOCK-03 — Full causal failure/controller harness

- causal environment fault preparation;
- cross-principal/concurrency orchestration;
- lifecycle/restart/OOBE cases;
- restore-isolation scenarios;
- required oracles for 86 normative T/F/subcases;
- production-factory integration author tests.

A case-ID registry is not an executable causal suite.

---

## 12. Exact next sequence after persistence gate closes

Do not start until `IMPLEMENTATION_MAY_RESUME=true`.

1. executable/interpreter/dependency byte-trust + remaining effective-profile behavior;
2. service/OOBE/restart/resume/factory branches;
3. prior pre-C3/checkpoint selection + nested cross-stage E00 semantics;
4. incomplete/temp publication recovery + remaining E17 recovery integration;
5. reviewed non-DIRECT transport support;
6. complete causal supported-route/failure controller procedures;
7. production-factory integration author tests using explicit author-test ports;
8. full workspace regression/static checks;
9. update implementation/remaining/traceability/evidence docs;
10. run Documentation Sync Gate: state/task/memory/workflow/checkpoint updates as applicable;
11. diff review + secret scan;
12. commit + push + remote verification;
13. only when truly author-complete: set `CODE_REVIEW_HANDOFF_READY=true` and transition to CODE_REVIEW.

See `NEXT_WORK_ITEM.md` for executable detail.

---

## 13. Forbidden actions in current mode

- Do not change FD/D00/public/reviewed contracts.
- Do not lower acceptance or delete negative/failure cases to force PASS.
- Do not execute Windows/WSL/LAB/SITE/guest/live-network work during authoring unless a later explicit authorized work item permits it.
- Do not register fixture/fake ports as production/active CLI backend.
- Do not treat fixture flags, inventory, process exit or author-test counts as actual proof.
- Do not erase unresolved journal/fence/read state as a shortcut.
- Do not self-approve code review, qualification, HOST_READY or production readiness.
- Do not request host data as a substitute for missing source work.
- Do not create a fake DESIGN_GAP because implementation is incomplete.
- Do not author new implementation while exact-source persistence is unresolved.
- Do not allow durable project learning to remain only in chat; update `PROJECT_MEMORY.md` when applicable.

---

## 14. Design-gap rule

Only if implementation evidence proves reviewed behavior must change:

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

Stop implementation for the affected scope and return to design/review. A memory entry may document the discovery but cannot authorize the contract change.

Current open design gaps: **none**.

---

## 15. Persistent self-improving project-memory rule

From V13 onward, the assistant must automatically persist durable project learning.

At the end of each meaningful increment evaluate:

```text
STATE CHANGED?             → PROJECT_STATE.md
NEXT ACTION CHANGED?       → NEXT_WORK_ITEM.md
REUSABLE LEARNING FOUND?   → PROJECT_MEMORY.md
WORKFLOW IMPROVED?         → GIT_WORKFLOW.md + PROJECT_MEMORY.md
IMPLEMENTATION MOVED?      → implementation/remaining/traceability/evidence docs
MILESTONE REACHED?         → new immutable checkpoint MD + JSON
```

Do not wait for the user to say “update the MD”. Documentation synchronization is part of the work itself.

Memory entries must distinguish facts/evidence from hypothesis/proposal and must not bypass the mode state machine.

---

## 16. Git persistence rule

For every coherent increment after the source seed:

```text
verify remote
→ work in correct mode
→ targeted tests/evidence
→ full regression at delivery boundary
→ Documentation Sync Gate
→ diff review
→ secret scan
→ commit
→ push
→ verify remote
→ next increment
```

Do not call local work durable until remote verification succeeds. Do not force-push/rewrite published history by default.

The exact committed/pushed author-complete candidate is the future CODE_REVIEW target.

---

## 17. Current risks

- Reconstructing/accepting non-byte-identical source as dev6 baseline.
- Confusing author tests with native validation/qualification.
- Public repository accidentally receiving real secrets/private assets.
- Duplicated mutable state drifting across multiple MD files.
- Reusable findings/optimizations being lost in chat instead of promoted to `PROJECT_MEMORY.md`.
- Starting implementation before the persistence prerequisite is verified.

---

## 18. Milestone pointers

Detailed historical snapshots remain immutable in checkpoint files. Current relevant milestones:

- master state initialized; Phase 00 selected;
- Design V1 → `REVIEW-P00-001` FAIL with six findings;
- Design V2 → `REVIEW-P00-002` PASS;
- implementation dev1…dev6 authored incrementally;
- dev6 = current verified partial author baseline;
- Git cross-chat persistence initialized;
- V13 = living project-memory + automatic documentation-sync protocol established;
- exact dev6 Git source seed remains open.

---

## 19. Definition of implementation exit

`IMPL-P00-001` may exit IMPLEMENTATION only when all are true:

- exact baseline/current source is durably persisted in Git;
- source/harness/docs/tests are author-complete;
- all `IMPL-REM-01…08` are closed or legitimately managed through the mode system;
- no known hidden native stub remains in supported reviewed scope;
- supported primary CLI path is production-component backed, not fixtures;
- supported causal failure/controller harness exists for reviewed scope;
- author regression/static checks are clean;
- traceability/evidence/docs/current state/memory are synchronized;
- exact candidate is committed/pushed and remote state verified;
- `CODE_REVIEW_HANDOFF_READY=true` is evidence-supported.

Only then:

```text
MODE TRANSITION
FROM: IMPLEMENTATION
TO: CODE_REVIEW
TASK: CODE-REVIEW-P00-001
EXIT GATE: CODE_REVIEW_PASS
```
