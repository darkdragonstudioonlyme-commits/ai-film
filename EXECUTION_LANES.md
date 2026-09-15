# AI-FILM-SERVER — Independent Workflow Lanes

## Trust model

Workflows do **not** trust each other's conclusions. They exchange immutable inputs/outputs and independently verify what they consume.

```text
PRODUCER lane → immutable handoff identity → CONSUMER lane
      ↑                                      │
      └──────── finding/result contract ─────┘

main = global state/gate authority
```

No lane may promote its own output through the next gate.

## Source pair: IMPLEMENT / REVIEW

### IMPLEMENT

- worktree: `/home/dragon/ai-film-dev/implement`
- local branch: `impl/p00`
- writable: source/tests/docs/evidence
- may: implement, test, commit, package, create handoff
- may not: issue CODE_REVIEW verdict or claim validation/qualification

### REVIEW

- worktree: `/home/dragon/ai-film-dev/review`
- detached exact candidate
- candidate source is read-only by policy
- may: reread requirements, rerun tests, run negative scenarios, write findings/verdicts
- may not: patch candidate or follow IMPLEMENT head implicitly

Formal handoff requires exact commit SHA, package hash/size/store identity, source/test digests, author evidence, contract digest, changed scope and readiness flags.

## Documentation governance pair: DOC-DESIGN / DOC-REVIEW

Documentation architecture changes use the same distrust model:

### DOC-DESIGN

- remote branch: `lane/docs-design`
- WSL worktree: `/home/dragon/ai-film-dev/docs-design`
- owns proposed changes to state schema, router, roadmap, memory/persistence policy and documentation map.
- cannot self-approve documentation governance.

### DOC-REVIEW

- remote branch: `lane/docs-review`
- WSL worktree: `/home/dragon/ai-film-dev/docs-review`
- reviews an exact DOC-DESIGN commit as if authored by another team.
- runs cold-start/routing/drift simulations and `tools/check_project_docs.py`.
- does not edit the proposed docs while reviewing; findings return to DOC-DESIGN.

Only a reviewed docs commit is promoted to `main`.

## Workflow independence requirements

1. Separate worktree or immutable checkout.
2. Exact input identity.
3. Separate evidence namespace where execution evidence exists.
4. No shared mutable “PASS” flag.
5. Consumer rechecks critical invariants; labels from producer are not proof.
6. Findings bind target identity and close only on a new reviewed output.
7. `main` alone records global gate/mode state.

## Candidate finding contract

```yaml
FINDING_ID:
TARGET_ID:
TARGET_COMMIT:
SEVERITY:
CATEGORY:
EVIDENCE:
IMPACT:
REQUIRED_DISPOSITION:
STATUS: OPEN|FIXED_PENDING_REVIEW|CLOSED
```

## Drift rule

Remote lane state is advisory until freshly fetched. A cached `origin/lane/*` ref is not current evidence. Bootstrap must fetch relevant refs before consuming `LANE_STATE.md`.

## Current source-lane disposition

- last durable candidate: dev17 `64ea95bf...`;
- REVIEW dev17: FAIL delta, open `CR-P00-012/013` plus umbrella `CR-P00-001`;
- IMPLEMENT has dev18 WIP with intended fixes and 756 PASS / 100 static author run; it is not yet a reviewable candidate.

Current exact details live in `PROJECT_STATE.md` / `NEXT_WORK_ITEM.md`, not in historical snapshots.
