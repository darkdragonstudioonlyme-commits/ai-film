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
```

## Goal

Finish the remaining source/integration/fault-controller scope of Phase 00 without re-labelling missing code as missing native evidence and without changing the exact approved Design V2 behavior.

## First integration — do these next

1. Complete executable/interpreter/dependency byte-trust and remaining effective-profile behavior.
2. Complete remaining native service/OOBE/restart/resume/multi-stage/factory interaction branches.
3. Complete prior pre-C3/checkpoint proof selection and nested cross-stage E00 semantics.
4. Complete incomplete/temp bundle publication recovery and remaining E17 recovery-path integration/applicability.
5. Complete reviewed non-DIRECT transport support where required.

## Then

6. Complete causal supported-route/failure controller procedures for all normative T/F/subcases.
7. Complete production-factory integration author tests with explicit author test ports.
8. Run full workspace regression and static checks.
9. Update traceability/evidence/docs and canonical project state.
10. Secret scan, commit, push, verify remote SHA.

## Already authored — do not redo as if absent

- Original mutation-fence recovery.
- Detached C0 read recovery before mutation fence.
- Protected C0 observation-to-plan proposal binding.
- Primary native CLI dispatch.
- Live committed-run NOOP components.
- Snapshot stage identity and archive re-observation.
- E17 write-ahead/read-only recovery.
- Prior-guest hash-linked provenance selection.
- Bounded early-failure capture before first usable snapshot.
- Partial registered-LAB native route controller/oracles.

## Inputs

- `PROJECT_STATE.md`
- `contracts/AI_VIDEO_SERVER_SINGLE_CHAT_WORKFLOW_BLUEPRINT_V2.md`
- exact approved Phase 00 Design V2 contracts and approval under `contracts/`
- `docs/IMPLEMENTATION_STATUS.md`
- `docs/REMAINING_IMPLEMENTATION.md`
- `docs/NATIVE_INTEGRATION_BOUNDARY.md`
- latest source tree / verified dev6 snapshot
- latest workspace test report

## Forbidden

- Change FD/D00/public/reviewed contracts or lower acceptance.
- Execute Windows/WSL/LAB/SITE/guest/live-network operations during authoring.
- Register fixture/fake active CLI backends.
- Treat process exit, fixture flags, inventory or author test count as actual proof.
- Delete unresolved journal/fence/read state to recover.
- Self-approve code review, qualification, HOST_READY or production readiness.
- Ask for user host data as a substitute for remaining source implementation.

## Design-gap rule

If implementation evidence demonstrates a required behavior change to an approved contract, record a genuine DESIGN_GAP and leave the affected implementation scope before redesign. Do not create a design gap merely because source work is incomplete.

## Exit condition

A full author-complete source/harness/docs/test candidate exists; all `IMPL-REM-01…08` are actually closed or properly managed under the mode system; no hidden stub remains; regression/static checks are clean; canonical state is updated and the exact candidate has been committed and pushed.

Only then:

```text
MODE TRANSITION
FROM: IMPLEMENTATION
TO: CODE_REVIEW
TASK: CODE-REVIEW-P00-001
EXIT GATE: CODE_REVIEW_PASS
```
