# AI-FILM-SERVER — Git, Artifact and Documentation Persistence Policy

## Core rule

A result is durable only after its owning workflow persists an immutable identity and verifies remote/artifact state. Local WIP is valuable but is not a durable candidate.

## Bootstrap Git rule

Before reading lane state or starting work:

```bash
git -C /home/dragon/ai-film-dev/repo fetch origin main lane/implement-p00 lane/review-p00
```

Fetch any additional active workflow branches declared by current canonical state. Do not treat stale `origin/*` cache as current state. In the prepared WSL workspace, run `python3 tools/check_runtime_state.py` before destructive checkout/reset or formal handoff decisions.

## Branch roles

- `main` — canonical project state, routing, roadmap, memory, reviewed documentation governance, immutable review/delivery records.
- `lane/implement-p00` — IMPLEMENT operational ledger, not source-of-gate authority.
- `lane/review-p00` — REVIEW operational ledger.
- documentation governance DESIGN/REVIEW/AUDIT branches are **release-selected** by `PROJECT_STATE.md:DOCUMENTATION_GOVERNANCE`; standing policy must not pin one revision's branch names or infer activity from retained worktree names.
- WSL `impl/p00` — writable local source history until remote source mirroring policy changes.

Do not force-push published history by default. Immutable reviewed candidates are replaced by new candidates, not edited in place.

## Workflow continuity write-ahead rule

Before duplicate-prone work, the owning lane must persist the active `RUN_ID` and step `INTENT` defined by `WORKFLOW_CONTINUITY.md`. After verification, persist `COMPLETE` with exact output identity. Do not wait until end-of-chat to record all progress.

A local commit/package/test report ahead of `main` is recoverable progress only when the run ledger binds its canonical base and identity. New chats reconcile and reuse it; they do not create a second candidate/workflow from the older base.

The owning lane branch is the live continuity ledger for in-flight work. `main` remains global gate/current-milestone authority. Completion/canonical sync closes the run; lane progress never self-promotes a gate.

## IMPLEMENT durable sequence

```text
verify state/base/WIP + ACTIVE_RUN_ID
→ persist step INTENT
→ implement
→ targeted tests
→ full author regression/static at boundary
→ documentation sync
→ diff + secret scan
→ commit exact source
→ package from exact commit
→ verify manifest/hash
→ persist artifact
→ publish/verify source visibility status
→ immutable handoff
→ persist step COMPLETE / next INTENT
→ REVIEW
```

Never package first and keep editing the source afterward under the same candidate identity.

## Source visibility and review addressability

Byte-preserving artifact durability and browseable source visibility are separate properties. Before `CODE_REVIEW_HANDOFF_READY=true`, the handoff must state:

```yaml
EXACT_SOURCE_IDENTITY:
EXACT_PACKAGE_IDENTITY:
REMOTE_SOURCE_ADDRESSABILITY: FULL_GIT_TREE|PARTIAL_REVIEW_SNAPSHOT|ARTIFACT_ONLY
REMOTE_SOURCE_REF:
FULL_SOURCE_GIT_MIRROR: true|false
VISIBILITY_LIMITATIONS:
```

A partial GitHub snapshot is useful for inspection but is non-authoritative and must be labeled `PARTIAL_REVIEW_SNAPSHOT`; it does not satisfy `FULL_SOURCE_GIT_MIRROR=true`. Review authority remains the exact handed-off source/package identity. When tooling can safely materialize the full exact source tree in Git, prefer that before formal code review because it reduces reviewer/operator friction and improves diffability.

## REVIEW durable sequence

```text
fetch handoff
→ checkout/resolve detached exact source identity
→ verify package/source/test identities
→ verify declared source-visibility limitations rather than assuming a snapshot is complete
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

When promoted, keep a compact memory provenance entry and mark the policy/tool location. Durable standalone learning records live under `learning/`. `SELF_LEARNING.md` defines scoring, activation, success metrics, compaction and retirement. Repeated ineffective cycles trigger `WORKFLOW_HEALTH.md` and persist immutable reviews under `workflow-health/`.

## Secret/public-repo discipline

Secret-scan every material delivery. Test canaries must be clearly synthetic. Never commit PATs, credentials, private keys, production secrets, licensed/private assets or customer data.

## Remote verification

After remote writes, re-fetch the branch/ref and verify the expected file/commit is visible before treating the update as durable.

## Environment/model record persistence

Exact environment snapshots live under `environments/`; reviewed model results live under `model-evaluations/`. Methodology files point to these records rather than accumulating mutable/historical result prose.

## Repository enforcement versus procedural policy

Documentation must distinguish **project policy** from **platform enforcement**. Do not claim that review/CI is repository-enforced unless the current branch/ruleset configuration has been independently verified. When platform capabilities allow it, canonical `main` promotion should require the applicable governance checks; absence of required status enforcement is governance debt, not evidence that a design PASS is false.

## Verdict-branch CI role

DOC-DESIGN, DOC-REVIEW and DOC-AUDIT are different workflow roles. A checker intended for a promoted tree must not mechanically reject a legitimate intermediate review/audit tree merely because only one verdict artifact exists. Tooling must become branch-role aware or stage verdicts so each role has a coherent invariant set.

Until that automation is implemented, a `partial-promotion-verdict-set` failure on a verdict-bearing review/audit commit is process-health evidence and must be disclosed; it may not be silently ignored or misrepresented as proof that the exact design target failed. Promotion still requires a green exact design target and a green post-promotion canonical tree.

## CI lifecycle-domain coverage

CI path filters are part of the control plane. `workflow-runs/**`, `test-governance/**`, `learning/**`, `workflow-health/**`, `environments/**`, `model-evaluations/**`, delivery/state artifacts and governance tools must trigger the checks relevant to the authority they can change. Missing trigger coverage is automation debt and must be recorded by DOC-AUDIT until corrected.

## Documentation promotion exact-tree rule

A documentation-system candidate must already contain its intended post-promotion canonical state/checkpoint before final DOC-REVIEW/DOC-AUDIT. The state must predeclare the exact final review/audit IDs and immutable record paths. Review/audit records may be produced afterward because they are consumer verdict artifacts, but the final `main` promotion may only merge the exact reviewed/audited design tree plus those predeclared immutable verdict records. Any additional policy/state/checkpoint edit after audit reopens DOC-REVIEW and DOC-AUDIT.
