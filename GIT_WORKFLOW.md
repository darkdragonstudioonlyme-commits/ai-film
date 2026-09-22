# AI-FILM-SERVER — Git, Artifact and Documentation Persistence Policy

## Core rule

A result is durable only after its owning workflow persists an immutable identity and verifies remote/artifact state. Local WIP is valuable but is not a durable candidate.

## Bootstrap Git rule

Before reading lane state or starting work:

```bash
git -C /home/dragon/ai-film-dev/repo fetch origin main
# Then fetch only relevant refs resolved from the current state/run.
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

Checks distinguish DESIGN (no final verdict), REVIEW (review only), AUDIT and PROMOTED (both matching verdicts). Each stage must pass its actual invariant set. A red verdict-bearing CI result is not excused by a green design run. Never relabel a role or synthesize PASS records to bypass the failure. Record the exact stage/commit and repair the responsible design or checker through review.

## CI lifecycle-domain coverage

CI path filters are part of the control plane. `workflow-runs/**`, `test-governance/**`, `learning/**`, `workflow-health/**`, `environments/**`, `model-evaluations/**`, delivery/state artifacts and governance tools must trigger the checks relevant to the authority they can change. Missing trigger coverage is automation debt and must be recorded by DOC-AUDIT until corrected.

## Documentation promotion exact-tree rule

A documentation-system candidate must already contain its intended post-promotion canonical state/checkpoint before final DOC-REVIEW/DOC-AUDIT. The state must predeclare the exact final review/audit IDs and immutable record paths. Review/audit records may be produced afterward because they are consumer verdict artifacts, but the final `main` promotion may only merge the exact reviewed/audited design tree plus those predeclared immutable verdict records. Any additional policy/state/checkpoint edit after audit reopens DOC-REVIEW and DOC-AUDIT.

## Change size and publication transaction

Classify before work: **EVIDENCE_UPDATE** follows an existing reviewed lifecycle transition and owning-lane evidence/review rules; **EDITORIAL** changes no meaning and requires scoped diff/link checks; **POLICY_CHANGE** changes authority, schema, routing, acceptance or checker semantics and requires DOC-DESIGN → DOC-REVIEW → DOC-AUDIT. Neither category can be chosen to hide a semantic change. Ordinary evidence updates do not automatically require a new DOCSYS release; changes to canonical gate authority still require their owning review and exact-tree transaction.

Prefer one coherent candidate over a release for each corrected sentence. Freeze acceptance criteria before editing; after two ineffective attempts with the same premise, inspect the premise. Normal non-forced publication binds the expected parent. Before promotion re-fetch `main`; if the base advanced, reconcile the competing change and repeat affected review/audit instead of overwriting it. Post-promotion CI is mandatory and reported separately from author checks.

## Bounded publication and evidence scope

Publish one coherent correction after exact review, not a new global snapshot for every inspection or sentence. An ordinary boundary receipt follows existing evidence governance and needs no new DOCSYS release. A material policy/checker change still requires the complete documentation review/audit. The final report distinguishes local committed, remotely verified, merged, CI-verified and deployed; none implies the next. Never report a tool call that was denied, interrupted or only started as successful.

## Worker publication boundary

Automatic handoff is not automatic main promotion. Workers return exact artifacts,
commits or patches from their assigned worktree; they receive neither Git publish
credentials nor the V02 private key. The integrator verifies non-author acceptance,
expected parent, applicable checks and real remote durability before promotion.
Tasks submitted from arbitrary branch pushes, issues or untrusted model output never
become executable authority. No secret, private context bundle or raw provider log is
published as part of a handoff. See `docs/DUAL_AI_AUTOMATIC_HANDOFF.md`.

The intended PROMOTION_STATE inside a frozen candidate describes the desired canonical content, not whether publication occurred. Effective authority requires the trusted coordinator to resolve the actual canonical ref and required exact verdicts; a candidate file cannot self-promote by declaring PROMOTED. Candidate-review capsules identify that scope explicitly and grant no normal execution. PROJECTION_SEMANTICS makes this distinction machine-visible; release revision names need not share verdict ordinals, which are owned solely by FINAL_REVIEW_ID/FINAL_AUDIT_ID.
