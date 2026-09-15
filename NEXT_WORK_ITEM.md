# NEXT WORK ITEM — IMPL-P00-001

```yaml
WORK_ITEM_ID: IMPL-P00-001
MODE: IMPLEMENTATION
PHASE: "00 — Host / WSL"
STATUS: IN_PROGRESS
CURRENT_DELIVERY: PARTIAL_SOURCE_DROP_DEV8
ENTRY_GATE: DESIGN_REVIEW_PASS
ENTRY_GATE_STATUS: SATISFIED_EXACT_V2
TARGET_GATE: CODE_REVIEW_PASS
PHASE_GATE: HOST_READY
MODE_TRANSITION_NOW: NONE
DOCUMENTATION_SYNC: MANDATORY
LIVING_MEMORY: PROJECT_MEMORY.md
WSL_WORKSPACE_READY: true
WSL_WORKSPACE_ROOT: /home/dragon/ai-film-dev
ACTIVE_SOURCE: /home/dragon/ai-film-dev/source-dev8
```

## Exact recovery anchor

```yaml
PACKAGE: IMPL-P00-001_IMPLEMENTATION_PACKAGE_V8.zip
SIZE_BYTES: 1091121
SHA256: d4e6b67eebd40fbc173f85205792499021cf6eea9b82309e54c2a76a9a9e3cb5
DRIVE_FILE_ID: 125T2wVf0CVkcmQND0PSmF3HHvXh8AgxD
RAW_REDOWNLOAD_SHA_VERIFIED: true
LOCAL_BASELINE_COMMIT: c44c2f87084f8082ce29af5935c6b47d03f7b96c
```

Author baseline: **683 PASS**, **92 static PASS**. Native Windows/WSL/LAB/SITE remain NOT_RUN.

## Immediate goal

Complete the next coherent evidence-semantics increment:

**prior pre-C3/checkpoint provenance selection + nested cross-stage E00 semantics**.

Do not mix this increment with publication recovery/non-DIRECT transport/86-case controller work unless a very small directly coupled change is required for correctness.

## Required order

1. Read exact dev8 `docs/REMAINING_IMPLEMENTATION.md`, `docs/NATIVE_INTEGRATION_BOUNDARY.md`, Evidence Register V2, Design V2 D00-10/D00-12/D00-14, relevant `evidence_stage`, `evidence_catalog`, `native/evidence_pipeline`, `native/proofs`, `native/assessment`, session/recovery source and existing dev6 prior-evidence tests.
2. Map which later stages may consume which prior records and which provenance links are mandatory.
3. Implement prior **pre-C3/checkpoint** selection using exact plan/run/step/host/target/checkpoint/source provenance; do not infer eligibility from a `PASS` label, intended output name, file timestamp or envelope status alone.
4. Complete nested cross-stage E00 field/source selection that is already required by the reviewed catalog/stage rules.
5. Reject unrelated, tampered, ambiguous, stale, wrong-host/wrong-plan and provenance-incomplete prior evidence.
6. Preserve distinction between prior immutable evidence and current observations; do not boot/launch a guest merely to fill a prior-stage gap.
7. Add focused positive/negative author tests. Parent T/F cases remain native NOT_RUN unless actually executed later in authorized validation.
8. Run targeted tests, then `/home/dragon/ai-film-dev/test.sh` for full author regression/static checks.
9. Update implementation/remaining/traceability docs and automatically persist reusable lessons to `PROJECT_MEMORY.md`.
10. Secret/diff review, create exact next package, upload by file reference, raw re-download/hash verify, update Git state/checkpoint and verify remote before another increment.

## Dev8 behavior to preserve

- C3 process exit is not lifecycle completion.
- Pending reboot retains `AWAITING_REBOOT/20`.
- Reboot-wait reconciliation requires changed host boot witness + cleared pending state.
- Post-reboot affected-resource owner evidence is required before C3 step commit where applicable.
- Missing owner postcheck can retain/relabel only an existing operator-wait fence.
- OOBE owner wait does not invent reboot semantics.
- The reviewed final owner-planned `AWAIT_OWNER_RESTART` remains in plan operations.

See `MEM-20260915-016…019`.

## Following increments

After this evidence increment is durably persisted:

1. incomplete/temp support-bundle publication recovery + remaining E17 recovery integration/applicability;
2. reviewed non-DIRECT transport support where required;
3. causal supported-route/failure controller procedures for all 86 normative T/F/subcases;
4. production-factory integration author tests with explicit author-test ports;
5. final source/harness/docs/test closure and CODE_REVIEW handoff preparation.

## WSL workflow

```bash
source /home/dragon/ai-film-dev/env.sh
/home/dragon/ai-film-dev/test.sh
```

Read `WORKSPACE_WSL.md`. Local Git is for diff/rollback; direct WSL push remains unauthenticated, so remote state writes use the GitHub connector.

## Forbidden

- Change FD/D00/public/reviewed contracts or lower acceptance.
- Execute Phase00 native Windows/WSL/LAB/SITE/guest/live-network provisioning/validation during authoring.
- Treat process exit, fixture flags, author-test count, envelope labels or timestamps as actual native proof.
- Boot a guest just to manufacture missing prior-stage evidence.
- Delete unresolved journal/fence/read state to recover.
- Self-approve code review, qualification or HOST_READY.
- Ask for host data as a substitute for remaining source implementation.
- Continue from an unverified delivery/worktree.
- Store GitHub credentials/PATs in plaintext workspace files.

## Design-gap rule

If implementation evidence shows that correct behavior requires changing reviewed semantics, create a genuine `DESIGN_GAP` and leave the affected implementation scope. Do not redesign inside IMPLEMENTATION.

## Exit condition

A full author-complete source/harness/docs/test candidate exists; `IMPL-REM-01…08` are actually closed or correctly managed; no hidden stub remains; required author regression/static checks are clean; exact candidate identity is durably persisted/reviewable; canonical docs/state are synchronized.

Only then transition to `CODE_REVIEW / CODE-REVIEW-P00-001`.
