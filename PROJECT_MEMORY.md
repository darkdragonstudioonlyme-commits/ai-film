# AI-FILM-SERVER — PROJECT MEMORY

> Living reusable knowledge for future chats.  
> Current state lives in `PROJECT_STATE.md`; next execution lives in `NEXT_WORK_ITEM.md`; historical full memory through V14 is archived at `memory/archive/PROJECT_MEMORY_V14.md`.

## No-silent-knowledge rule

A reusable discovery, optimization, tooling limitation, failure pattern, test lesson, risk, security rule, or clarification must be persisted before the related increment is considered durable.

Memory does not approve architecture or pass gates. If a discovery requires changing reviewed behavior, create a DESIGN_GAP in the correct mode.

## Active Memory Index

| ID | Type | Reusable rule |
|---|---|---|
| MEM-20260915-001 | PROCESS | Separate current state, next work, reusable knowledge, and immutable history. |
| MEM-20260915-002 | TOOLING | Exact baselines require byte-preserving transport plus independent identity verification. |
| MEM-20260915-003 | TESTING | Author regression/static checks are not Windows/WSL/LAB/SITE proof. |
| MEM-20260915-004 | PROCESS | An increment is durable only after remote artifact/state verification. |
| MEM-20260915-005 | SECURITY | Secret-scan every public-repo delivery; never persist real credentials/private assets. |
| MEM-20260915-006 | TOOLING | Prefer file-reference/raw-file actions for binary delivery artifacts. |
| MEM-20260915-007 | PROCESS | Hybrid persistence is valid when Git state and exact binary artifact roles are explicit. |
| MEM-20260915-008 | LESSON | Explicit missing state is safer than accepting non-identical bytes. |
| MEM-20260915-009 | TOOLING | If chunking is unavoidable, verify every Git blob SHA individually; prefer file-native transfer. |
| MEM-20260915-010 | TESTING | Use the package’s src-layout invocation (`PYTHONPATH=src` or official runner); import failure without it is not a source regression. |
| MEM-20260915-011 | SECURITY | Executable trust must bind path + exact bytes + policy scope + pinned handle + witness before process resume. |

## New entries since archived V14 memory

### MEM-20260915-010 — Src-layout test invocation is part of reproducible author evidence

```yaml
MEMORY_ID: MEM-20260915-010
TYPE: TESTING
STATUS: ACTIVE
DISCOVERED_IN:
  MODE: IMPLEMENTATION
  PHASE: "00 — Host / WSL"
  WORK_ITEM: IMPL-P00-001
SUMMARY: "The package uses a src/ layout; running unittest discovery without exposing src causes import failures that are invocation errors, not implementation regressions."
EVIDENCE: "The first dev7 baseline invocation without PYTHONPATH=src failed imports; rerunning with PYTHONPATH=src reproduced the verified dev6 baseline at 666/666 PASS. The official tools/run_workspace_tests.py path also completed successfully after the dev7 patch."
IMPACT: "Future chats could falsely diagnose a broken baseline or waste time patching imports."
REUSABLE_RULE: "For author regression use the documented package invocation: PYTHONPATH=src python -m unittest ... or the official workspace-test runner. Classify missing-src import errors as invocation/environment failures until source regression evidence exists."
AFFECTED_AREAS: [testing, reproducibility, tooling]
ACTION_TAKEN: "Dev7 baseline and final regression were run with the correct src-layout invocation."
FOLLOW_UP: "Keep the official invocation in delivery records and future CI/bootstrap documentation."
SUPERSEDES: []
SUPERSEDED_BY: null
```

### MEM-20260915-011 — Native child executable trust is byte identity, not path identity

```yaml
MEMORY_ID: MEM-20260915-011
TYPE: SECURITY
STATUS: ACTIVE
DISCOVERED_IN:
  MODE: IMPLEMENTATION
  PHASE: "00 — Host / WSL"
  WORK_ITEM: IMPL-P00-001
SUMMARY: "A trusted executable path alone does not prove the bytes actually launched are the reviewed dependency/controller binary."
EVIDENCE: "Dev7 added executable-policy pins scoped to host/build/contract, exact path/size/SHA-256 verification under pinned filesystem handles, administrative owner/writer constraints, mandatory production-supervisor trust before child creation, and process witnesses recording policy ref/hash/size/kind. Seven targeted tests and full 673-test regression passed."
IMPACT: "This closes a TOCTOU/trust gap at the native process boundary and makes later diagnostics/recovery able to identify the exact binary authorized for execution."
REUSABLE_RULE: "Before a native child is resumed, bind authority to policy-scoped exact binary bytes using a pinned handle; record that identity in the durable process witness. Never infer executable trust from path or process exit alone."
AFFECTED_AREAS: [security, native-process, trust, reproducibility]
ACTION_TAKEN: "Implemented ExecutableTrust, filesystem pinned_executable, production supervisor enforcement, binding requirement, authority refresh and witness fields in dev7."
FOLLOW_UP: "Do not overclaim: guest interpreter/rootfs provenance and remaining dependency/bootstrap trust are still open."
SUPERSEDES: []
SUPERSEDED_BY: null
```

## Usage by future chats

1. Read `PROJECT_STATE.md` and `NEXT_WORK_ITEM.md` first.
2. Scan this Active Memory Index for current-task lessons.
3. Open `memory/archive/PROJECT_MEMORY_V14.md` only when older entry detail is needed.
4. Add/supersede memory entries automatically at every meaningful increment.
