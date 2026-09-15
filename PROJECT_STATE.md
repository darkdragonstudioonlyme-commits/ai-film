# AI-FILM-SERVER — CANONICAL PROJECT STATE V12

> **READ THIS FILE FIRST IN EVERY NEW CHAT.**  
> This file is the canonical human-readable cross-chat handoff. It is intentionally detailed so a new chat can identify the exact project phase, active mode, approved baseline, verified implementation status, blockers and next action without reading the previous conversation transcript.

---

## 1. Repository identity and persistence status

```yaml
REPOSITORY: darkdragonstudioonlyme-commits/ai-film
DEFAULT_BRANCH: main
VISIBILITY_AT_BOOTSTRAP: PUBLIC
GIT_PERSISTENCE_INITIALIZED: true
CANONICAL_STATE_FILE: PROJECT_STATE.md
CANONICAL_NEXT_WORK: NEXT_WORK_ITEM.md
GIT_POLICY: GIT_WORKFLOW.md
SOURCE_IMPORT_STATUS_FILE: SOURCE_IMPORT_STATUS.md
```

The repository is now the persistent location for project state/handoff and, after the one-time exact source seed is completed, will also be the persistent development source of truth.

**Security rule:** because the repository was public at initialization, never commit real passwords, API keys, private keys, access tokens, private customer material, licensed private assets, or production secrets. Synthetic test strings such as `CANARY_SECRET` are test fixtures, not credentials, but should remain clearly identified as synthetic.

---

## 2. New-chat bootstrap order

A new chat MUST do this before project work:

1. Read `PROJECT_STATE.md` completely.
2. Read `NEXT_WORK_ITEM.md` completely.
3. Read `GIT_WORKFLOW.md`.
4. Read `SOURCE_IMPORT_STATUS.md`.
5. Read `CHAT_HANDOFF.md`.
6. Verify the latest commit on `main`.
7. If exact source has been seeded since this state file was written, verify its hashes/manifest before editing it.
8. Read the authoritative Blueprint and exact approved Phase 00 V2 contracts when they are available in the repository/source seed.
9. Do not infer a later gate PASS from prose, test counts or implementation intent.

If repository state and an old chat transcript disagree, prefer the latest verified repository state plus reviewed artifacts/evidence. Never reconstruct missing source from conversation summaries when an exact package/tree should be used.

---

## 3. Mode-state-machine position

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

**Do not transition to CODE_REVIEW.** The implementation exit condition has not been satisfied.

---

## 4. Temporary repository-persistence prerequisite

The project implementation is currently **paused before further coding** for one reason: the exact `0.1.0.dev6` source bytes have not yet been accepted as a verified GitHub mirror.

```yaml
EXACT_DEV6_SOURCE_MIRRORED: false
SOURCE_IMPORT_VERIFIED: false
IMPLEMENTATION_MAY_RESUME: false
PERSISTENCE_PREREQUISITE: OPEN
PERSISTENCE_BLOCKER_KIND: REPOSITORY_PERSISTENCE
```

This is **not** a design gap, validation failure, code-review finding or statement that the implementation source did not exist. Dev6 is a verified implementation delivery from the authoring workspace; only its durable Git mirror is incomplete.

Why it is blocked:

- GitHub connector/repository access works and commits work.
- Detailed MD state/handoff files have been committed successfully.
- Experimental chunk/source import paths were tested against local Git-blob/SHA identities.
- At least one copied blob was not byte-identical to local dev6.
- All experimental `src/` and `snapshots/` mirrors were removed from `main` rather than being accepted as a false baseline.

Read `SOURCE_IMPORT_STATUS.md` for exact resolution requirements.

**No new implementation should be authored until the exact dev6 source is seeded through a byte-preserving Git/file path and verified.**

---

## 5. Authority and precedence

When artifacts conflict, use this precedence unless a later reviewed artifact explicitly supersedes an earlier one:

1. `AI VIDEO SERVER — SINGLE CHAT WORKFLOW BLUEPRINT V2`.
2. Frozen project decisions `FD-01…FD-08`.
3. Exact Phase 00 Design V2 contracts.
4. `REVIEW-P00-002` Design Review approval for exact V2.
5. Exact implementation source candidate.
6. Actual test/evidence reports.
7. This current-state handoff.
8. Historical delivery summaries/checkpoints.

IMPLEMENTATION must not redesign, change public/reviewed contracts, lower acceptance criteria, or self-approve gates.

If implementation proves that reviewed behavior cannot be implemented without changing a reviewed contract, create a genuine DESIGN_GAP and leave implementation for the affected scope before redesigning it.

---

## 6. Approved design history

```text
Phase 00 Design V1
→ REVIEW-P00-001
→ FAIL
→ findings DR-P00-001…006

Phase 00 Design V2
→ REVIEW-P00-002
→ PASS exact V2
```

Approved state:

- `FD-01…FD-08`: frozen, unchanged.
- `D00-01…D00-14`: approved for Phase 00 implementation only.
- `DESIGN_REVIEW_PASS`: satisfied for exact Design V2.
- Approved contract-set digest recorded by the implementation deliveries:

```text
f259656c48ed24c15bd48da2bb040950ed94d8edcf1473cf6456b96578c933ee
```

The design approval does **not** establish implementation completeness, native validation, qualification or `HOST_READY`.

---

## 7. Phase 00 invariants that implementation must preserve

The implementation must continue respecting these reviewed safety/correctness properties:

- Correct host, principal and target identity before mutation.
- Preserve existing Windows/WSL distributions/data unless the exact reviewed plan authorizes a change.
- Shared WSL runtime/global effects are treated as host-wide impact where applicable.
- Active operations use host-global admission semantics and durable unresolved-state handling.
- Native process exit is not proof that intended Windows/WSL postconditions are true.
- Timeout/interruption may produce `UNCERTAIN`; do not blind retry or erase durable state.
- Recovery/protection evidence must exist before relevant C3/shared-runtime mutation.
- SITE active operations require matching qualification evidence; LAB evidence production is a separate path.
- Terminal/gate assertions must correspond to the final effective lifecycle state, not stale pre-restart observations.
- Restore isolation must be proven before first boot when the reviewed route requires it.
- Evidence-record completeness, public support-bundle completeness and gate eligibility are separate concepts.
- `APPLIED != VERIFIED != HOST_READY`.
- No destructive default recovery such as unregistering an existing distro merely to make a retry succeed.

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

Original verified delivery artifact:

```text
IMPL-P00-001_IMPLEMENTATION_PACKAGE_V6.zip
SHA-256:
41f8a4ed1d80b87bc84981c3cdb2254a3fbc33f21b822580d7e0788b7b404f7e
```

### Major capabilities authored through dev6

The verified implementation already contained substantial work. A future chat must not interpret the temporary missing Git source mirror as evidence these components are unimplemented:

- bounded/canonical input handling and plan hashing;
- plan/approval/qualification/trust policy core;
- resource floors, capacity and profile predicates;
- host-global admission concepts, durable fence/read-set/journal behavior;
- native Windows identity/filesystem/trust adapters and source-byte pinning components;
- native process supervision ordering with durable witnesses;
- native actuator components for reviewed Phase 00 actions;
- session runner and native session driver;
- operation postcondition observers;
- original mutation-fence recovery;
- pre-mutation detached C0-read recovery;
- live committed-run NOOP revalidation components;
- protected C0 observation capture and observation-to-plan proposal binding;
- primary native CLI dispatch to the concrete factory;
- guest-agent/inventory/content/sentinel observation components;
- terminal sweep components;
- evidence catalog and protected snapshot/support-bundle components;
- snapshot stage identity and exact archive re-observation;
- publication write-ahead/recovery components;
- E17 proposal write-ahead/read-only recovery added in dev6;
- prior-guest/C3 provenance selection from exact hash-linked operation history added in dev6;
- bounded early-failure journal capsule before the first usable snapshot added in dev6;
- registered-LAB route-controller contribution and route oracles;
- extensive author regression tests.

Existence of these components does not imply every supported route/failure case has full integration or native validation.

---

## 9. Verified author test baseline

Latest verified dev6 author results:

```text
Workspace regression: 666 PASS
Failures:             0
Errors:               0
Skipped:              0
Static author checks: 88 PASS
```

Not established:

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

Never translate `666 PASS`, static-check counts, fixture results or route inventories into qualification/native-validation/HOST_READY evidence.

---

## 10. Open implementation items

All eight full-work-item REM entries remain OPEN. The table records progress so the next chat does not redo completed subcomponents.

| ID | Authored progress through dev6 | Remaining full-item closure |
|---|---|---|
| `IMPL-REM-01` | Native observations plus protected C0 capture and observation-to-proposal binding | Complete effective-profile/eligibility integration across supported contexts and full native-factory route flows. |
| `IMPL-REM-02` | Native single guard, durable fence/read set, original-request recovery, logical/physical journal byte checks | Complete source integration/fault procedures around exhaustion, interrupted readers and lifecycle boundaries without implicit journal reset. |
| `IMPL-REM-03` | Exact source scripts, native trust/proof graph, per-entry/per-step authorization, pinned execution/selection records | Complete bootstrap/executable/dependency byte-trust integration, source epochs and prior pre-C3/checkpoint proof selection. |
| `IMPL-REM-04` | Primary native CLI wired to concrete factory; service/reboot preconditions; first-user wait vs actual receipt | Complete remaining service/OOBE/restart/resume interactions and production-factory execution-path author tests. |
| `IMPL-REM-05` | Mutation-fence recovery, detached-read recovery, safe non-success cancellation/pause and committed live NOOP | Complete prolonged/multi-stage resume, later request boundaries and remaining recovery/publication interactions. |
| `IMPL-REM-06` | Guest/content/assets/terminal readers and native proof consumers | Complete non-DIRECT transport contexts plus effective-profile/terminal/restore integration and causal harness assertions. |
| `IMPL-REM-07` | Immutable snapshot stage, field checks, failure capture hook, publication intent/readback, E17 recovery, prior-guest provenance and early-failure capsule | Complete nested cross-stage semantics, prior pre-C3/checkpoint selectors, temp/incomplete output recovery, applicability and remaining recovery-path integration. |
| `IMPL-REM-08` | Foundations + registered-LAB route controller/oracles and expanded author regression | Full supported-route/failure preparations/controllers, per-T/F/subcase oracles and production-factory integration author tests. |

---

## 11. Current implementation blockers

### IMPL-BLOCK-01 — Remaining native integration

Scope: REM-01…06.

Still source work, not missing user data:

- effective-profile/eligibility behavior across supported contexts;
- interpreter/executable/dependency byte-trust/bootstrap integration;
- remaining service/OOBE/restart/resume/multi-stage recovery interactions;
- remaining production-factory execution paths and author tests;
- supported non-DIRECT transport adapter path.

### IMPL-BLOCK-02 — Remaining evidence/recovery semantics

Scope: REM-03/06/07.

Dev6 already had prior-guest operation provenance, early-failure capsule and E17 recovery. Remaining work includes:

- full nested cross-stage field semantics;
- prior pre-C3/checkpoint selection/provenance;
- incomplete/temp support-bundle output recovery;
- remaining E17/recovery-path applicability and integration;
- terminal/restore/effective-profile context integration.

### IMPL-BLOCK-03 — Full causal failure/controller harness

Scope: REM-08.

The existing route controller is a real contribution, but not the whole normative suite. Remaining work includes:

- causal environment fault preparations;
- cross-principal and concurrency orchestration;
- lifecycle/restart/OOBE cases;
- restore-isolation scenarios;
- required route/failure oracles for the 86 normative T/F/subcases;
- production-factory integration author tests.

A registry of case IDs is not an executable causal test suite.

---

## 12. Exact implementation order after source persistence is resolved

Do not start this list until `EXACT_DEV6_SOURCE_MIRRORED=true`.

1. Complete executable/interpreter/dependency byte-trust and remaining effective-profile behavior.
2. Complete remaining service/OOBE/restart/resume/factory branches.
3. Complete prior pre-C3/checkpoint selection and nested cross-stage E00 semantics.
4. Complete incomplete/temp publication recovery and remaining E17 recovery integration.
5. Complete reviewed non-DIRECT transport support where required.
6. Finish causal supported-route/failure controller procedures for the complete normative inventory.
7. Add production-factory integration author tests using explicit author test ports only.
8. Run full workspace regression/static checks.
9. Update implementation status, remaining-work register, traceability, evidence, state and checkpoint.
10. Inspect diff and run secret scan.
11. Commit and push exact candidate.
12. Verify remote commit SHA.
13. Only if source/harness/docs/tests are genuinely author-complete and no hidden stub remains, set `CODE_REVIEW_HANDOFF_READY=true` and transition to CODE_REVIEW.

---

## 13. Forbidden actions in current mode

Until the implementation work item exits:

- Do not change FD/D00/public/reviewed contracts.
- Do not lower acceptance criteria or delete negative/failure cases to make a gate pass.
- Do not execute Windows/WSL/LAB/SITE/guest/live-network operations during authoring unless a later explicit authorized work item permits it.
- Do not register fixture/fake ports as the production/active CLI backend.
- Do not treat fixture flags, inventory, process exit or author-test count as actual proof.
- Do not erase unresolved journal/fence/read state as an implementation shortcut.
- Do not self-approve code review, qualification, HOST_READY or production readiness.
- Do not ask the user for host data as a substitute for writing missing source.
- Do not create a fake DESIGN_GAP merely because code is incomplete.
- While the persistence prerequisite is open, do not write new implementation code on top of a reconstructed/non-byte-identical baseline.

---

## 14. Design-gap rule

Only if implementation evidence proves a reviewed behavior must change:

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

Then stop implementation for that affected scope and return to the appropriate design/review path. Implementation may not close its own design gap.

Current state: **no design gap established**.

---

## 15. Mandatory Git persistence workflow

After the one-time dev6 seed succeeds, Git becomes a hard cross-chat persistence boundary.

For every coherent implementation increment:

```text
verify latest remote state
→ implement one coherent part
→ targeted author tests
→ full workspace regression at delivery boundary
→ update docs/evidence/state/checkpoint
→ diff review
→ secret scan
→ commit
→ push
→ verify remote SHA
→ only then start the next coherent part
```

Do not call local work durable until the remote commit is verified.

Do not force-push or rewrite published history by default.

The final author-complete candidate must have an exact committed/pushed SHA before CODE_REVIEW begins. CODE_REVIEW must review that exact committed candidate, not an uncommitted workspace.

Read `GIT_WORKFLOW.md` for the standing policy.

---

## 16. Git bootstrap history

Repository bootstrap performed on 2026-09-15:

- GitHub connector authenticated as repository owner/admin-capable account.
- Repository `darkdragonstudioonlyme-commits/ai-film` confirmed accessible with push/admin permission.
- Repository initialized on `main`.
- Canonical handoff files created:
  - `README.md`
  - `PROJECT_STATE.md`
  - `NEXT_WORK_ITEM.md`
  - `GIT_WORKFLOW.md`
  - `CHAT_HANDOFF.md`
  - `SOURCE_IMPORT_STATUS.md`
  - `.gitignore`
  - `pyproject.toml` metadata
- A bootstrap secret scan of the local dev6 package found only synthetic test canaries/token-pattern fixtures; no private key, GitHub token or AWS access key was identified by that scan.
- Experimental source/archive mirrors that failed byte-identity checks were removed from `main`.
- No force push was used.

This history is persistence evidence, not code review or validation evidence.

---

## 17. Milestone history needed by a new chat

- MASTER state initialized; Phase 00 selected.
- Phase 00 Design V1 authored.
- `REVIEW-P00-001`: design FAIL with six findings.
- Design V2 revised the contracts.
- `REVIEW-P00-002`: exact Design V2 PASS.
- dev1: policy/core foundations, partial.
- dev2: native identity/trust/guard/supervision foundations, partial.
- dev3: native session/evidence integration, partial.
- dev4: original-fence diagnostics/cancel/pause + live NOOP, partial.
- dev5: C0 binding, detached-read recovery, primary native CLI and route-controller contribution, partial.
- dev6: E17 recovery, prior-guest provenance selection and early-failure capture, current verified implementation baseline, partial.
- Git repository initialized for durable cross-chat state and future source commits.
- Exact dev6 Git source seeding remains an explicit persistence prerequisite before implementation resumes.

---

## 18. Definition of implementation exit

`IMPL-P00-001` may exit IMPLEMENTATION only when all are true:

- exact baseline/current source is durably persisted in Git;
- source/harness/docs/test candidate is author-complete;
- all `IMPL-REM-01…08` are actually closed or a genuine blocker is managed by the mode system;
- no known hidden native stub remains in supported reviewed scope;
- primary supported CLI path is wired to production components, not fixtures;
- supported causal failure/controller harness exists for reviewed scope;
- author regression and static checks are clean;
- traceability/evidence/docs are updated;
- exact candidate commit has been pushed and remote SHA verified;
- `CODE_REVIEW_HANDOFF_READY=true` is supported by evidence.

Then and only then:

```text
MODE TRANSITION
FROM: IMPLEMENTATION
TO: CODE_REVIEW
TASK: CODE-REVIEW-P00-001
EXIT GATE: CODE_REVIEW_PASS
```

---

## 19. Current state ledger summary

```yaml
PROJECT: AI-FILM-SERVER
STATE_VERSION: 12
CURRENT_MODE: IMPLEMENTATION
CURRENT_PHASE: "00 — Host / WSL"
CURRENT_BASELINE:
  REQUIREMENTS: Blueprint_V2
  REVIEWED_DESIGN: "Exact Phase00 V2 — REVIEW-P00-002 PASS"
  SOURCE: "0.1.0.dev6 — partial, verified author delivery, exact Git mirror pending"
  VERIFIED_INFRA: NOT_ESTABLISHED
  PROMOTED_BASELINE: NONE
CURRENT_TASK:
  ID: IMPL-P00-001
  STATUS: IN_PROGRESS_PAUSED_FOR_GIT_PERSISTENCE
TARGET_GATE: CODE_REVIEW_PASS
PHASE_GATE: HOST_READY
APPROVED_ARCHITECTURE: "Phase00 exact Design V2 only"
FROZEN_DECISIONS: "FD-01…FD-08"
OPEN_FINDINGS: []
OPEN_DESIGN_GAPS: []
OPEN_VALIDATION_FAILURES: []
OPEN_IMPLEMENTATION_ITEMS: "IMPL-REM-01…08"
IMPLEMENTATION_BLOCKERS: "IMPL-BLOCK-01…03"
PERSISTENCE_PREREQUISITE:
  EXACT_DEV6_SOURCE_MIRRORED: false
  SOURCE_IMPORT_VERIFIED: false
  IMPLEMENTATION_MAY_RESUME: false
LAST_TEST_RESULT:
  WORKSPACE: "666 PASS / 0 failures / 0 errors / 0 skipped"
  STATIC: "88 PASS"
  NATIVE_WINDOWS_WSL: NOT_RUN
  LAB: NOT_RUN
  SITE: NOT_RUN
LAST_REVIEW_RESULT:
  DESIGN: "REVIEW-P00-002 PASS exact V2"
  CODE: NOT_PERFORMED
QUALIFICATION_ISSUED: false
HOST_READY: NOT_EVALUATED
CODE_REVIEW_HANDOFF_READY: false
NEXT_MODE: IMPLEMENTATION
NEXT_ACTION: "Resolve exact dev6 Git source persistence per SOURCE_IMPORT_STATUS.md; then continue NEXT_WORK_ITEM.md."
```

---

## 20. Prompt to use in a new chat

```text
Use GitHub repository darkdragonstudioonlyme-commits/ai-film as the persistent project handoff.
Read PROJECT_STATE.md, NEXT_WORK_ITEM.md, GIT_WORKFLOW.md and SOURCE_IMPORT_STATUS.md before doing anything else.
Do not rely on the old chat transcript.
Follow the AI-FILM-SERVER one-active-mode state machine.
The expected current mode is IMPLEMENTATION, Phase 00, work item IMPL-P00-001, but implementation is paused until the repository confirms an exact verified dev6 source mirror.
Do not reconstruct dev6 source from prose. Do not skip review/validation gates. Do not treat author tests as native evidence.
After the exact source seed is verified, continue only the open REM/blocker scope recorded in PROJECT_STATE.md and NEXT_WORK_ITEM.md.
For every coherent implementation increment: test, update state/evidence/docs, diff review, secret scan, commit, push, verify remote SHA, then continue.
```
