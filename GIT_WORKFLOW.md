# AI-FILM-SERVER — Git, Artifact, Test and Documentation Persistence Policy

## Durable result rule

A result is durable only after exact identity, required tests/evidence, documentation sync, remote persistence and independent verification. Local WIP is preserved but never mislabeled as a candidate.

## Bootstrap

Fresh-fetch `main` and relevant lane refs. Do not trust stale `origin/*` cache. Run runtime reconciliation before destructive checkout/reset or formal handoff decisions.

## Source candidate sequence

```text
verify state/base/WIP
→ implement
→ run business-basis test workflow
→ classify failures before edits
→ targeted tests
→ full regression/static
→ documentation/self-learning sync
→ diff + secret scan
→ exact source commit
→ package from exact commit
→ artifact hash/manifest verification
→ immutable handoff
→ independent REVIEW
```

## Test semantic changes

A changed expected result must identify `APPROVED_BEHAVIOR_CHANGE` or `TEST_DEFECT` authority. Harness/executor changes are separate from oracle changes. The current source cannot be cited as the reason a test expectation changed.

Use `tools/run_test_workflow.py`; WSL `test.sh` is a managed compatibility entrypoint that delegates to it, while `lane-test.sh` is only a low-level executor. Workspace helper content is managed by `tools/sync_workspace_helpers.py` and verified at runtime.

## Documentation-system changes

```text
DOC-DESIGN exact commit
→ DOC-REVIEW exact commit
→ if PASS: DOC-AUDIT exact reviewed candidate
→ if both PASS: promote reviewed/audited commit to main
```

Any FAIL returns findings to DOC-DESIGN and requires a new immutable commit.

## Artifact identity

For binary artifacts: upload byte-preserving file reference/raw bytes → raw-download → recompute SHA-256 → compare → record store ID/size/hash. Upload success alone is not identity proof.

## Self-learning and knowledge hygiene

Every meaningful workflow evaluates `SELF_LEARNING_SYSTEM.md` triggers and Documentation Sync Gate. Reusable lessons go to memory; recurring/safety-critical lessons are promoted into policy/tooling. Run knowledge compaction/pruning under `KNOWLEDGE_LIFECYCLE.md`; obsolete operational rules are removed from active docs while history remains in Git/archive.

## Public-repo/secret policy

Secret-scan material deliveries. Synthetic canaries must be identifiable. Never persist credentials, PATs, private keys, production secrets, private/licensed assets or customer data.

## Verification

After remote writes, fresh-fetch and verify the expected commit/files. A commit existing locally does not prove remote persistence.
