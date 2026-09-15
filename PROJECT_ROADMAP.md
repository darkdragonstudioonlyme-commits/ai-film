# AI-FILM-SERVER — Project Roadmap

## Governing chain

The authoritative Blueprint mode chain remains:

```text
DESIGN → DESIGN_REVIEW → IMPLEMENTATION → CODE_REVIEW → VALIDATION → QUALITY/PRODUCTION readiness
```

This roadmap does not approve gates; it only orders known work.

## Current phase: 00 — Host / WSL

Target implementation work item: `IMPL-P00-001`. Target code gate: `CODE_REVIEW_PASS`. Phase gate: `HOST_READY` after later authorized validation/qualification requirements are satisfied.

### Phase 00 work graph

```text
Reviewed Design V2 PASS
  ↓
Lifecycle/trust/evidence/recovery source increments   [substantially authored]
  ↓
Causal 86-case harness + production-factory author integration [ACTIVE]
  ↓
Close remaining source/harness/docs/test scope (CR-P00-001)
  ↓
AUTHOR_COMPLETE + CODE_REVIEW_HANDOFF_READY
  ↓
Formal CODE_REVIEW exact final candidate
  ↓ PASS
Authorized VALIDATION / LAB-SITE evidence
  ↓
Qualification / phase-gate assessment
  ↓
HOST_READY only if evidence supports it
```

## Current near-term milestones

| Milestone | Exit evidence | Next |
|---|---|---|
| M-P00-HARNESS | causal harness source accepted by independent REVIEW | residual source completeness audit |
| M-P00-AUTHOR-COMPLETE | no hidden reviewed-scope stubs; author tests/static clean; exact candidate durable | formal CODE_REVIEW |
| M-P00-CODE-REVIEW | `CODE_REVIEW_PASS` against exact candidate | VALIDATION |
| M-P00-VALIDATION | authorized native/LAB/SITE test evidence per approved contracts | qualification/gate assessment |
| M-P00-HOST-READY | exact acceptance/gate conditions satisfied | next project phase chosen by MASTER/roadmap update |

## Current known blocker hierarchy

- `CR-P00-001` — umbrella author-completeness blocker; closes only with full reviewed implementation scope.
- Candidate-specific review findings are subordinate and must be independently closed by REVIEW.
- Native test inventory remaining `NOT_RUN` is **not** an implementation defect by itself while authoring forbids native execution; source harness completeness and later validation execution are distinct.

## Roadmap update rule

Update this file only when work order, milestone definitions, closure criteria or phase transition changes. Do not use it as a daily status log; that belongs in `PROJECT_STATE.md` / `NEXT_WORK_ITEM.md`.
