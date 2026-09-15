# AI-FILM-SERVER — PROJECT MEMORY

> **Purpose:** persistent, cumulative knowledge that must survive chat boundaries.
>
> `PROJECT_STATE.md` answers **where the project is now**.  
> `NEXT_WORK_ITEM.md` answers **what to do next**.  
> `PROJECT_MEMORY.md` answers **what the project has learned that future work should not rediscover**.

---

## 1. Living-memory rule

This file is a **living knowledge ledger**. It must improve as the project progresses.

A useful discovery must not remain only in conversation context. If a work session discovers a reusable optimization, constraint, failure pattern, tooling limitation, implementation lesson, safer workflow, test lesson, performance observation, or important clarification, the assistant must persist it here before the related increment is considered durable.

This is a standing project rule:

```text
DISCOVER
→ VERIFY / QUALIFY THE EVIDENCE
→ CLASSIFY
→ RECORD IN PROJECT_MEMORY.md
→ UPDATE AFFECTED STATE/TASK/DOCS
→ TEST IF APPLICABLE
→ COMMIT
→ PUSH
→ VERIFY REMOTE
```

**No silent knowledge:** if losing a fact when this chat ends could cause duplicated work, a wrong decision, a repeated failure, a safety regression, or wasted investigation, it belongs in persistent documentation.

---

## 2. What belongs here

Record durable, reusable knowledge such as:

- `OPTIMIZATION` — a better way to implement, test, review, persist, or operate something;
- `DISCOVERY` — a verified fact that changes how future work should be approached;
- `TOOLING` — connector, Git, shell, API, environment or workflow behavior worth remembering;
- `LESSON` — a failure/near-miss and the general rule learned from it;
- `RISK` — a persistent risk and its mitigation;
- `TESTING` — a reusable test/oracle lesson;
- `SECURITY` — a reusable security constraint or safe-handling rule;
- `PERFORMANCE` — a measured performance/capacity lesson when evidence exists;
- `DECISION_CANDIDATE` — an idea that may require formal design/review before becoming architecture;
- `PROCESS` — an improvement to the project operating model.

Do **not** use this file to bypass the mode state machine. A memory entry does not approve architecture, close a finding, pass a gate, or replace evidence.

---

## 3. What does NOT belong here

Do not append:

- private chain-of-thought or speculative internal reasoning;
- unverified guesses presented as facts;
- temporary command output with no future value;
- secrets, credentials or private assets;
- large duplicate copies of `PROJECT_STATE.md`;
- full implementation diffs already preserved by Git;
- architecture changes that have not gone through the required design/review path;
- test PASS claims without actual execution evidence.

For a hypothesis, explicitly mark it `UNVERIFIED` or use the appropriate research/design system.

---

## 4. Entry schema

Every durable entry should use this structure:

```yaml
MEMORY_ID: MEM-YYYYMMDD-NNN
TYPE: OPTIMIZATION | DISCOVERY | TOOLING | LESSON | RISK | TESTING | SECURITY | PERFORMANCE | DECISION_CANDIDATE | PROCESS
STATUS: ACTIVE | RESOLVED | SUPERSEDED | PROMOTED
DISCOVERED_IN:
  MODE:
  PHASE:
  WORK_ITEM:
SUMMARY:
EVIDENCE:
IMPACT:
REUSABLE_RULE:
AFFECTED_AREAS:
ACTION_TAKEN:
FOLLOW_UP:
SUPERSEDES: []
SUPERSEDED_BY: null
```

Rules:

- `SUMMARY` must be understandable without the old chat.
- `EVIDENCE` must distinguish actual test/observation from inference.
- `REUSABLE_RULE` should be concise enough for a future chat to apply.
- If an entry changes project state or next work, update the canonical state/task files too.
- Do not delete old entries when they become obsolete. Mark them `SUPERSEDED` and point to the new entry.

---

## 5. Promotion rules

Memory is informative; other artifacts remain authoritative for their domains.

| Memory outcome | Required persistent action |
|---|---|
| Changes current status/blocker/baseline | Update `PROJECT_STATE.md`. |
| Changes next executable action | Update `NEXT_WORK_ITEM.md`. |
| Improves commit/push/document process | Update `GIT_WORKFLOW.md`. |
| Reveals reviewed-contract inadequacy | Create `DESIGN_GAP`; do not silently edit the contract. |
| Produces a review finding | Record through the finding system in the correct review mode. |
| Produces a validation failure | Record `VALIDATION_FAILURE` in VALIDATION; do not repair there. |
| Changes an approved architecture/contract | Must go through design + review; memory alone cannot promote it. |
| Establishes a milestone | Create a new immutable `AI_FILM_STATE_CHECKPOINT_Vn.md` and matching JSON state. |

---

## 6. Mandatory documentation-sync trigger

Before ending a meaningful work increment, the assistant must ask:

```text
DID PROJECT STATE CHANGE?
DID NEXT ACTION CHANGE?
DID I LEARN A REUSABLE FACT?
DID I DISCOVER AN OPTIMIZATION?
DID A RISK/BLOCKER CHANGE?
DID TEST/REVIEW EVIDENCE CHANGE?
DID THE WORKFLOW ITSELF IMPROVE?
WOULD A NEW CHAT LOSE SOMETHING IMPORTANT IF I STOP NOW?
```

Any `YES` creates a documentation obligation before the increment is considered persistent.

See `GIT_WORKFLOW.md` for the exact Documentation Sync Gate.

---

# Active memory entries

## MEM-20260915-001 — Separate current state from accumulated knowledge

```yaml
MEMORY_ID: MEM-20260915-001
TYPE: PROCESS
STATUS: ACTIVE
DISCOVERED_IN:
  MODE: IMPLEMENTATION
  PHASE: "00 — Host / WSL"
  WORK_ITEM: IMPL-P00-001
SUMMARY: "Cross-chat handoff becomes harder when current state, history, lessons and next work are duplicated across several files without explicit ownership."
EVIDENCE: "Repository documentation review found repeated bootstrap/state content in README, PROJECT_STATE, CHAT_HANDOFF, NEXT_WORK_ITEM and checkpoint files."
IMPACT: "Future chats can waste context tokens, miss the canonical update target, or allow copies to drift."
REUSABLE_RULE: "PROJECT_STATE = current truth; NEXT_WORK_ITEM = next execution; PROJECT_MEMORY = reusable knowledge; GIT_WORKFLOW = persistence protocol; checkpoints = immutable history."
AFFECTED_AREAS: [documentation, cross-chat-continuity, git]
ACTION_TAKEN: "Introduced PROJECT_MEMORY.md and documentation-role rules."
FOLLOW_UP: "Keep bootstrap reading layered and avoid copying the same mutable state into multiple files unless the copy is explicitly a historical checkpoint."
SUPERSEDES: []
SUPERSEDED_BY: null
```

## MEM-20260915-002 — Exact source persistence requires byte-preserving transport

```yaml
MEMORY_ID: MEM-20260915-002
TYPE: TOOLING
STATUS: ACTIVE
DISCOVERED_IN:
  MODE: IMPLEMENTATION
  PHASE: "00 — Host / WSL"
  WORK_ITEM: IMPL-P00-001
SUMMARY: "Successful GitHub text-content commits are not sufficient evidence that a reconstructed/chunked source import is byte-identical to the verified dev6 package."
EVIDENCE: "During repository bootstrap, experimental archive/source mirrors were compared with local dev6 blob/content identities and at least one file/blob failed identity verification; experimental trees were removed."
IMPACT: "Accepting an approximate mirror could create a false source baseline and invalidate reproducibility."
REUSABLE_RULE: "For an existing verified source baseline, require a byte-preserving transport plus manifest/hash verification; API success alone is not source-identity proof."
AFFECTED_AREAS: [git, source-import, reproducibility]
ACTION_TAKEN: "Created SOURCE_IMPORT_STATUS.md and paused new implementation until exact dev6 persistence is verified."
FOLLOW_UP: "After the one-time exact seed, perform all future development directly on the Git working tree so this bootstrap class of problem does not recur."
SUPERSEDES: []
SUPERSEDED_BY: null
```

## MEM-20260915-003 — Author regression is not native validation

```yaml
MEMORY_ID: MEM-20260915-003
TYPE: TESTING
STATUS: ACTIVE
DISCOVERED_IN:
  MODE: IMPLEMENTATION
  PHASE: "00 — Host / WSL"
  WORK_ITEM: IMPL-P00-001
SUMMARY: "Workspace author tests and static checks must remain distinct from Windows/WSL/LAB/SITE validation and qualification evidence."
EVIDENCE: "Latest verified dev6 author baseline is 666 workspace PASS and 88 static PASS while native Windows/WSL, LAB and SITE remain NOT_RUN."
IMPACT: "Conflating these layers would create false gate PASS claims."
REUSABLE_RULE: "Always label evidence by execution environment and gate role; never promote author-test counts into native validation, qualification or HOST_READY."
AFFECTED_AREAS: [testing, validation, gates, evidence]
ACTION_TAKEN: "State and handoff documents explicitly preserve this distinction."
FOLLOW_UP: "Maintain the distinction in every future checkpoint and review handoff."
SUPERSEDES: []
SUPERSEDED_BY: null
```

## MEM-20260915-004 — Remote persistence boundary

```yaml
MEMORY_ID: MEM-20260915-004
TYPE: PROCESS
STATUS: ACTIVE
DISCOVERED_IN:
  MODE: IMPLEMENTATION
  PHASE: "00 — Host / WSL"
  WORK_ITEM: IMPL-P00-001
SUMMARY: "A coherent increment should not exist only in one chat/workspace if later chats must continue it."
EVIDENCE: "Project requirement now explicitly uses GitHub as the cross-chat persistence layer."
IMPACT: "Without a verified remote boundary, later chats can resume from stale or incomplete state."
REUSABLE_RULE: "Test → documentation sync → secret/diff review → commit → push → verify remote SHA → only then start the next coherent increment."
AFFECTED_AREAS: [git, continuity, implementation-process]
ACTION_TAKEN: "Standing Git workflow established in GIT_WORKFLOW.md."
FOLLOW_UP: "Use the verified remote candidate SHA as the CODE_REVIEW boundary."
SUPERSEDES: []
SUPERSEDED_BY: null
```

## MEM-20260915-005 — Public repository secret discipline

```yaml
MEMORY_ID: MEM-20260915-005
TYPE: SECURITY
STATUS: ACTIVE
DISCOVERED_IN:
  MODE: IMPLEMENTATION
  PHASE: "00 — Host / WSL"
  WORK_ITEM: IMPL-P00-001
SUMMARY: "Repository visibility at bootstrap was public, so persistent project documentation/source must be treated as publishable."
EVIDENCE: "GitHub repository metadata during bootstrap reported public visibility; bootstrap scan identified only synthetic canary/token-pattern fixtures, not known real credentials."
IMPACT: "A single accidental credential commit could expose a secret publicly and remain in Git history."
REUSABLE_RULE: "Secret-scan every delivery; never commit real credentials/private keys/tokens/private customer or licensed private assets; clearly mark synthetic security fixtures."
AFFECTED_AREAS: [security, git, evidence]
ACTION_TAKEN: "Security rule added to state/Git workflow."
FOLLOW_UP: "If repository visibility changes later, do not relax secret discipline."
SUPERSEDES: []
SUPERSEDED_BY: null
```

---

## 7. How a new chat should use this file

A new chat should not re-read every historical entry before simple work. Use this sequence:

1. Read `PROJECT_STATE.md` and `NEXT_WORK_ITEM.md` first.
2. Read the **Active memory entries** relevant to the current work area.
3. Search this file by keywords/IDs when encountering a familiar problem.
4. Before finishing an increment, add or update entries for any durable new learning.

When this ledger grows large, preserve old entries but add a concise **Active Memory Index** near the top instead of deleting history.
