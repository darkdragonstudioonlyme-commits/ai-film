# NEXT WORK ITEM — IMPL-P00-001 after dev9 delta review

```yaml
PROJECT_MODE: IMPLEMENTATION
PHASE: "00 — Host / WSL"
CURRENT_DELIVERY: PARTIAL_SOURCE_DROP_DEV9
TARGET_GATE: CODE_REVIEW_PASS
EXECUTION_MODEL: DUAL_LANE
IMPLEMENT_LANE: lane/implement-p00
REVIEW_LANE: lane/review-p00
LAST_DELTA_REVIEW: PASS_CR_P00_002_003_004
OVERALL_CODE_REVIEW: FAIL_CR_P00_001
```

Read `EXECUTION_LANES.md` before work.

## IMPLEMENT lane — ACTIVE NEXT INCREMENT

```yaml
WORK_ITEM_ID: IMPL-P00-001
WSL_WORKTREE: /home/dragon/ai-film-dev/implement
LOCAL_SOURCE_BRANCH: impl/p00
CURRENT_SOURCE_COMMIT: 3da3ddc771c15d175a2c5045c86a7c1ff9987dbd
SOURCE_WRITABLE: true
```

### Immediate scope

Complete **prior pre-C3/checkpoint provenance selection + nested cross-stage E00 semantics**.

Required order:

1. Read exact dev9 `docs/REMAINING_IMPLEMENTATION.md`, `docs/NATIVE_INTEGRATION_BOUNDARY.md`, Evidence Register V2, Design V2 D00-10/D00-12/D00-14, `evidence_stage`, `evidence_catalog`, `native/evidence_pipeline`, `native/proofs`, `native/assessment`, session/recovery source and existing prior-evidence tests.
2. Map which later stages may consume which prior protected records and which source/provenance links are mandatory.
3. Implement prior **pre-C3/checkpoint** selection using exact host/plan/run/step/target/checkpoint/source identity; do not infer eligibility from PASS labels, filenames, timestamps, intended hashes or envelope status.
4. Complete nested cross-stage E00 field/source selection required by the reviewed catalog/stage rules.
5. Reject unrelated, tampered, ambiguous, stale, wrong-host/wrong-plan and provenance-incomplete prior evidence.
6. Preserve prior immutable evidence versus current observations; do not boot/launch a guest merely to fill prior-stage evidence.
7. Add focused positive/negative author tests.
8. Run targeted tests and full `lane-test.sh implement`.
9. Commit/package immutable next candidate and publish handoff identity to REVIEW lane.

## REVIEW lane — WAITING

Last reviewed candidate: dev9 commit `3da3ddc...`.

Delta disposition:

```yaml
CR-P00-002: CLOSED
CR-P00-003: CLOSED
CR-P00-004: CLOSED
CR-P00-001: OPEN_BLOCKER
```

REVIEW waits detached until IMPLEMENT publishes a new immutable candidate. It must not follow `impl/p00` automatically.

## Dev9 candidate identity

```yaml
SOURCE_COMMIT: 3da3ddc771c15d175a2c5045c86a7c1ff9987dbd
PACKAGE: IMPL-P00-001_IMPLEMENTATION_PACKAGE_V9.zip
PACKAGE_LOCATION: /home/dragon/ai-film-dev/artifacts/IMPL-P00-001_IMPLEMENTATION_PACKAGE_V9.zip
SIZE_BYTES: 1114609
SHA256: d6f83dc3ff60f73acd54750f58db34d817c7bb492c83088693f7c47c65d510cb
AUTHOR_BASELINE: "692 PASS / 93 static PASS"
```

## Following increments

After the evidence-semantics increment is independently reviewed:

1. incomplete/temp support-bundle publication recovery + remaining E17 integration/applicability;
2. reviewed non-DIRECT transport support;
3. causal supported-route/failure controller procedures for all 86 normative T/F/subcases;
4. production-factory integration author tests;
5. final source/harness/docs/test closure;
6. formal author-complete handoff and full CODE_REVIEW.

## Forbidden

- Change FD/D00/public/reviewed contracts or lower acceptance.
- Execute Phase00 native Windows/WSL/LAB/SITE/guest/live-network provisioning/validation during authoring.
- Treat process exit, fixture flags, author-test counts, PASS envelopes, timestamps or filenames as native proof.
- Boot a guest just to manufacture missing prior-stage evidence.
- Delete unresolved durable state.
- IMPLEMENT self-approving review or REVIEW patching source.

## Exit condition

`CR-P00-001` closes only when the complete author source/harness/docs/test scope exists and `CODE_REVIEW_HANDOFF_READY=true`. Only then may the exact final candidate enter full CODE_REVIEW for `CODE_REVIEW_PASS`.
