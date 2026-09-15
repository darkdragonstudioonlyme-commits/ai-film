# NEXT WORK ITEM — IMPL-P00-001

```yaml
WORK_ITEM_ID: IMPL-P00-001
MODE: IMPLEMENTATION
PHASE: "00 — Host / WSL"
STATUS: IN_PROGRESS_PAUSED_FOR_GIT_PERSISTENCE
CURRENT_DELIVERY: PARTIAL_SOURCE_DROP_DEV6
ENTRY_GATE: DESIGN_REVIEW_PASS
ENTRY_GATE_STATUS: SATISFIED_EXACT_V2
TARGET_GATE: CODE_REVIEW_PASS
PHASE_GATE: HOST_READY
MODE_TRANSITION_NOW: NONE
EXACT_DEV6_SOURCE_MIRRORED: false
IMPLEMENTATION_MAY_RESUME: false
```

## Immediate prerequisite — before any more implementation

Resolve the one-time exact dev6 source seed described in `SOURCE_IMPORT_STATUS.md`.

Required result:

```yaml
EXACT_DEV6_SOURCE_MIRRORED: true
SOURCE_IMPORT_VERIFIED: true
IMPLEMENTATION_MAY_RESUME: true
```

The seed must preserve exact bytes and be verified against the recorded dev6 package/manifest/file identities. Do not reconstruct source from prose or accept a connector copy merely because GitHub returned a successful commit.

Verified dev6 package identity:

```text
IMPL-P00-001_IMPLEMENTATION_PACKAGE_V6.zip
SHA-256: 41f8a4ed1d80b87bc84981c3cdb2254a3fbc33f21b822580d7e0788b7b404f7e
```

Once exact source persistence is verified, update `PROJECT_STATE.md` and this file in Git, commit/push, verify the remote SHA, and only then continue the implementation sequence below.

## Goal after persistence is resolved

Finish the remaining source/integration/fault-controller scope of Phase 00 without re-labelling missing code as missing native evidence and without changing exact approved Design V2 behavior.

## First implementation sequence

1. Complete executable/interpreter/dependency byte-trust and remaining effective-profile behavior.
2. Complete remaining native service/OOBE/restart/resume/multi-stage/factory interaction branches.
3. Complete prior pre-C3/checkpoint proof selection and nested cross-stage E00 semantics.
4. Complete incomplete/temp bundle publication recovery and remaining E17 recovery-path integration/applicability.
5. Complete reviewed non-DIRECT transport support where required.

## Then

6. Complete causal supported-route/failure controller procedures for all normative T/F/subcases.
7. Complete production-factory integration author tests with explicit author test ports.
8. Run full workspace regression and static checks.
9. Update traceability/evidence/docs, `PROJECT_STATE.md`, checkpoint and next-work item.
10. Inspect diff and run secret scan.
11. Commit and push the exact candidate.
12. Verify remote commit SHA.

## Already authored through dev6 — do not redo as if absent

- Original mutation-fence recovery.
- Detached C0-read recovery before a mutation fence.
- Protected C0 observation-to-plan proposal binding.
- Primary native CLI dispatch.
- Live committed-run NOOP components.
- Snapshot stage identity and final archive re-observation.
- E17 write-ahead/read-only recovery.
- Prior-guest hash-linked provenance selection.
- Bounded early-failure capture before the first usable snapshot.
- Partial registered-LAB native route controller/oracles.
- Large author regression suite: latest verified result 666 PASS; static 88 PASS.

## Inputs after source seed

- `PROJECT_STATE.md`
- `SOURCE_IMPORT_STATUS.md`
- authoritative Blueprint V2
- exact approved Phase 00 Design V2 contracts/review approval
- exact dev6 source tree
- `docs/IMPLEMENTATION_STATUS.md`
- `docs/REMAINING_IMPLEMENTATION.md`
- `docs/NATIVE_INTEGRATION_BOUNDARY.md`
- latest verified workspace test report

## Forbidden

- Change FD/D00/public/reviewed contracts or lower acceptance.
- Execute Windows/WSL/LAB/SITE/guest/live-network operations during authoring.
- Register fixture/fake active CLI backends.
- Treat process exit, fixture flags, inventory or author-test count as actual proof.
- Delete unresolved journal/fence/read state to recover.
- Self-approve code review, qualification, HOST_READY or production readiness.
- Ask for user host data as a substitute for remaining source implementation.
- Start implementation while the Git source-persistence prerequisite is unresolved.

## Design-gap rule

If implementation evidence demonstrates a required behavior change to an approved contract, record a genuine DESIGN_GAP and leave the affected implementation scope before redesign. Do not create a design gap merely because source work is incomplete.

## Exit condition

A full author-complete source/harness/docs/test candidate exists; all `IMPL-REM-01…08` are actually closed or properly managed under the mode system; no hidden stub remains; regression/static checks are clean; canonical state is updated; the exact candidate has been committed/pushed and remote SHA verified.

Only then:

```text
MODE TRANSITION
FROM: IMPLEMENTATION
TO: CODE_REVIEW
TASK: CODE-REVIEW-P00-001
EXIT GATE: CODE_REVIEW_PASS
```
