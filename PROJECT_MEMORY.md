# AI-FILM-SERVER — Active Project Memory

> Compact reusable lessons only. Promoted/obsolete detail is archived; standing rules live in their owning policy documents.

Pre-V2 detail: `memory/archive/PROJECT_MEMORY_V1_BEFORE_V2.md` plus Git history.

## Active / provenance index

| ID | Lesson | Current owner |
|---|---|---|
| MEM-20260915-002 | exact baselines need byte-preserving identity verification | `GIT_WORKFLOW.md` |
| MEM-20260915-003 | author/review tests are not native proof | `TEST_STRATEGY.md` |
| MEM-20260915-015 | verification evidence must not dirty source baseline | workspace/test policy |
| MEM-20260915-021 | re-authorize immediately before durable recovery-state changes | implementation policy |
| MEM-20260915-024 | mutable producer and immutable reviewer require separate workspaces | `EXECUTION_LANES.md` |
| MEM-20260915-025 | review target identity never floats | `EXECUTION_LANES.md` |
| MEM-20260915-028 | fresh-fetch before trusting lane state | `GIT_WORKFLOW.md` |
| MEM-20260915-029 | durable candidate, WIP and review target are distinct | `PROJECT_STATE.md` schema |
| MEM-20260915-033 | preserve Git porcelain XY columns when parsing status | tooling know-how |
| MEM-20260915-034 | state/lane/worktree mismatch is `STATE_DRIFT`, not a tie to guess | router/runtime checker |
| MEM-20260915-035 | tests derive oracles from business/contracts, never current code | `TEST_STRATEGY.md` |
| MEM-20260915-036 | a test change must be classified before expectation changes | `TEST_STRATEGY.md` |
| MEM-20260915-037 | repeated failure/inefficiency triggers meta-review instead of blind retry | `SELF_LEARNING_SYSTEM.md` |
| MEM-20260915-038 | promoted/superseded knowledge must be compacted out of active docs | `KNOWLEDGE_LIFECYCLE.md` |
| MEM-20260915-039 | environment/tool provenance is part of model/test reproducibility | `SERVER_ENVIRONMENT.md` |
| MEM-20260915-040 | final governance audit must search beyond the reviewed delta | `EXECUTION_LANES.md` |
| MEM-20260915-041 | missing `nvidia-smi` means GPU not observed, not proven absent | `SERVER_ENVIRONMENT.md` |
| MEM-20260915-042 | ambient tool found in another project venv is not project authority | environment/test policy |
| MEM-20260915-043 | environment fingerprint must be cross-bound between snapshot and current state | environment/knowledge checkers |
| MEM-20260915-044 | governance checkers are part of pre-review evidence, not post-hoc cleanup | governance workflow |

## Learning rule

New reusable knowledge enters here briefly. If it becomes recurring, safety-critical or broadly operational, promote it into policy/tooling and compact the memory entry to a pointer. Superseded operational rules leave active docs; history remains in archive/Git.

Use `SELF_LEARNING_SYSTEM.md` and `KNOWLEDGE_LIFECYCLE.md` for lifecycle and retrospective rules.
