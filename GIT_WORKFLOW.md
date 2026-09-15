# AI-FILM-SERVER — Git, Artifact and Documentation Persistence Policy

## Core rule

A result is durable only after its owning workflow persists an immutable identity and verifies remote/artifact state. Local WIP is valuable but is not a durable candidate.

## Bootstrap Git rule

Before reading lane state or starting work:

```bash
git -C /home/dragon/ai-film-dev/repo fetch origin main lane/implement-p00 lane/review-p00
```

Fetch any additional active workflow branches. Do not treat stale `origin/*` cache as current state. In the prepared WSL workspace, run `python3 tools/check_runtime_state.py` before destructive checkout/reset or formal handoff decisions.

## Branch roles

- `main` — canonical project state, routing, roadmap, memory, reviewed documentation governance, immutable review/delivery records.
- `lane/implement-p00` — IMPLEMENT operational ledger, not source-of-gate authority.
- `lane/review-p00` — REVIEW operational ledger.
- `lane/docs-v2-design` — Documentation System V2 producer.
- `lane/docs-v2-review` — independent detailed documentation review.
- `lane/docs-v2-audit` — independent holistic documentation audit after detailed review PASS.
- WSL `impl/p00` — writable local source history until remote source mirroring policy changes.

Do not force-push published history by default. Immutable reviewed candidates are replaced by new candidates, not edited in place.

## IMPLEMENT durable sequence

```text
verify state/base/WIP
→ implement
→ targeted tests
→ full author regression/static at boundary
→ documentation sync
→ diff + secret scan
→ commit exact source
→ package from exact commit
→ verify manifest/hash
→ persist artifact
→ immutable handoff
→ REVIEW
```

Never package first and keep editing the source afterward under the same candidate identity.

## REVIEW durable sequence

```text
fetch handoff
→ checkout detached exact source commit
→ verify package/source/test identities
→ reread requirements/diff
→ independent regression + negative scenarios
→ findings/verdict bound to exact target
→ verify review did not mutate source
→ persist review record/state
```

## Binary artifact rule

Preferred:

```text
upload raw/file reference
→ raw download again
→ recompute SHA-256
→ compare source hash
→ record file/store ID + size + hash
```

Upload success is not identity proof.

## Documentation Sync Gate

Use `DOCUMENTATION_MAP.md`. Every meaningful workflow must evaluate state, next work, roadmap, router/policy, memory, workspace, immutable review/delivery and milestone updates before it is durable.

## Test-policy persistence

Changing production code does not authorize changing expected test behavior. Material test oracle changes follow `TEST_STRATEGY.md`, persist under `test-governance/`, and require independent TEST-REVIEW. Harness-only fixes must preserve the reviewed business oracle.

## Policy lifecycle and pruning

`POLICY_REGISTRY.md` owns policy status. DOC-AUDIT removes obsolete duplicated instructions from active guidance after successor/policy review; Git history and immutable records preserve history. Do not keep stale rules active merely for completeness.

## Self-learning persistence

A discovery is classified:

- candidate-specific defect → review finding;
- reusable lesson → `PROJECT_MEMORY.md`;
- repeated lesson that changes how work must be performed → promote to policy in `WORKFLOW_ROUTER.md`, `EXECUTION_LANES.md`, `GIT_WORKFLOW.md` or `DOCUMENTATION_MAP.md`;
- reviewed behavior conflict → DESIGN_GAP, not memory-based contract override.

When promoted, keep a compact memory provenance entry and mark the policy/tool location. `SELF_LEARNING.md` defines scoring, success metrics, compaction and retirement. Repeated ineffective cycles trigger `WORKFLOW_HEALTH.md` and persist immutable reviews under `workflow-health/`.

## Secret/public-repo discipline

Secret-scan every material delivery. Test canaries must be clearly synthetic. Never commit PATs, credentials, private keys, production secrets, licensed/private assets or customer data.

## Remote verification

After remote writes, re-fetch the branch/ref and verify the expected file/commit is visible before treating the update as durable.
