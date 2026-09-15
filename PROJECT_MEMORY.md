# AI-FILM-SERVER — PROJECT MEMORY

> Persistent cumulative knowledge that must survive chat boundaries.
>
> `PROJECT_STATE.md` = where the project is now.  
> `NEXT_WORK_ITEM.md` = what to do next.  
> `PROJECT_MEMORY.md` = what the project has learned and should not rediscover.

## Living-memory rule

A useful discovery must not remain only in chat context. Before a meaningful increment is durable:

```text
DISCOVER
→ VERIFY / QUALIFY EVIDENCE
→ CLASSIFY
→ RECORD HERE
→ UPDATE AFFECTED STATE/TASK/WORKFLOW
→ TEST IF APPLICABLE
→ COMMIT/PUSH
→ VERIFY REMOTE
```

If losing a fact at chat end could cause duplicated work, a wrong decision, a repeated failure, wasted investigation, or a safety/reproducibility regression, persist it here automatically.

## Entry schema

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
AFFECTED_AREAS: []
ACTION_TAKEN:
FOLLOW_UP:
SUPERSEDES: []
SUPERSEDED_BY: null
```

Memory is informative. It cannot approve architecture, close findings, pass gates, or replace test/review evidence. If a discovery requires changing an approved contract, create a DESIGN_GAP and leave the affected implementation scope.

# Active Memory Index

| ID | Type | Short rule |
|---|---|---|
| MEM-20260915-001 | PROCESS | Separate current state, next work, accumulated knowledge, and immutable history. |
| MEM-20260915-002 | TOOLING | Existing baselines require byte-preserving transport plus hash verification. |
| MEM-20260915-003 | TESTING | Author regression is not native/LAB/SITE validation. |
| MEM-20260915-004 | PROCESS | A coherent increment is durable only after remote persistence verification. |
| MEM-20260915-005 | SECURITY | Public-repo discipline: secret-scan every delivery and never persist real secrets/private assets. |
| MEM-20260915-006 | TOOLING | For binary baselines use file-reference/raw-file connectors, not model-rendered binary payloads. |
| MEM-20260915-007 | PROCESS | Hybrid persistence is valid when roles are explicit: GitHub for state/source ledger, byte store for exact artifacts. |
| MEM-20260915-008 | LESSON | Wrong bytes in Git are worse than an explicit missing/materialization status. |
| MEM-20260915-009 | TOOLING | If chunked Git blobs are ever needed, upload one small chunk at a time and verify returned Git SHA before proceeding. |

# Entries

## MEM-20260915-001 — Separate current state from accumulated knowledge

```yaml
MEMORY_ID: MEM-20260915-001
TYPE: PROCESS
STATUS: ACTIVE
DISCOVERED_IN: {MODE: IMPLEMENTATION, PHASE: "00 — Host / WSL", WORK_ITEM: IMPL-P00-001}
SUMMARY: "Cross-chat handoff drifts when current state, next work, lessons and history are duplicated without explicit ownership."
EVIDENCE: "Repository documentation review found repeated mutable state across README, PROJECT_STATE, CHAT_HANDOFF, NEXT_WORK_ITEM and checkpoints."
IMPACT: "Future chats may waste context or update the wrong copy."
REUSABLE_RULE: "PROJECT_STATE=current truth; NEXT_WORK_ITEM=next execution; PROJECT_MEMORY=reusable knowledge; GIT_WORKFLOW=persistence protocol; checkpoints=immutable history."
AFFECTED_AREAS: [documentation, cross-chat-continuity, git]
ACTION_TAKEN: "Introduced canonical document roles and living memory."
FOLLOW_UP: "Keep bootstrap layered and avoid duplicate mutable state."
SUPERSEDES: []
SUPERSEDED_BY: null
```

## MEM-20260915-002 — Exact baseline persistence requires byte-preserving transport

```yaml
MEMORY_ID: MEM-20260915-002
TYPE: TOOLING
STATUS: ACTIVE
DISCOVERED_IN: {MODE: IMPLEMENTATION, PHASE: "00 — Host / WSL", WORK_ITEM: IMPL-P00-001}
SUMMARY: "A successful remote write is not source-identity proof."
EVIDENCE: "Experimental GitHub text/chunk/source copies were compared with dev6 identities; at least one copied blob differed and the experimental trees were removed."
IMPACT: "Accepting approximate bytes would create a false baseline and break reproducibility."
REUSABLE_RULE: "For an existing verified baseline require byte-preserving transport and independent hash/manifest verification."
AFFECTED_AREAS: [git, source-import, reproducibility]
ACTION_TAKEN: "Incorrect experimental mirrors were removed; exact dev6 was later persisted with a raw-file connector and reverified."
FOLLOW_UP: "Use exact artifact identity whenever restoring a baseline."
SUPERSEDES: []
SUPERSEDED_BY: null
```

## MEM-20260915-003 — Author regression is not native validation

```yaml
MEMORY_ID: MEM-20260915-003
TYPE: TESTING
STATUS: ACTIVE
DISCOVERED_IN: {MODE: IMPLEMENTATION, PHASE: "00 — Host / WSL", WORK_ITEM: IMPL-P00-001}
SUMMARY: "Workspace author tests/static checks remain distinct from Windows/WSL/LAB/SITE validation and qualification evidence."
EVIDENCE: "Dev6 has 666 workspace PASS and 88 static PASS while native/LAB/SITE remain NOT_RUN."
IMPACT: "Conflation would create false gate claims."
REUSABLE_RULE: "Label evidence by environment and gate role; never promote author-test counts into native validation, qualification or HOST_READY."
AFFECTED_AREAS: [testing, validation, gates, evidence]
ACTION_TAKEN: "All state/checkpoint docs preserve the distinction."
FOLLOW_UP: "Maintain it in every future delivery/review."
SUPERSEDES: []
SUPERSEDED_BY: null
```

## MEM-20260915-004 — Remote persistence boundary

```yaml
MEMORY_ID: MEM-20260915-004
TYPE: PROCESS
STATUS: ACTIVE
DISCOVERED_IN: {MODE: IMPLEMENTATION, PHASE: "00 — Host / WSL", WORK_ITEM: IMPL-P00-001}
SUMMARY: "A coherent increment must not exist only in one ephemeral chat/workspace."
EVIDENCE: "The project now requires persistent cross-chat state and exact delivery identity."
IMPACT: "Without verified remote persistence a later chat can resume stale/incomplete work."
REUSABLE_RULE: "Test → documentation sync → diff/secret review → persist exact artifact/source/state → verify remote identity → only then start next increment."
AFFECTED_AREAS: [git, continuity, implementation-process]
ACTION_TAKEN: "Standing persistence workflow established."
FOLLOW_UP: "Use exact candidate identity as the CODE_REVIEW boundary."
SUPERSEDES: []
SUPERSEDED_BY: null
```

## MEM-20260915-005 — Public repository secret discipline

```yaml
MEMORY_ID: MEM-20260915-005
TYPE: SECURITY
STATUS: ACTIVE
DISCOVERED_IN: {MODE: IMPLEMENTATION, PHASE: "00 — Host / WSL", WORK_ITEM: IMPL-P00-001}
SUMMARY: "The GitHub repository was public at bootstrap, so persistent Git content must be treated as publishable."
EVIDENCE: "Repository metadata reported public visibility; bootstrap scan found only synthetic canaries/token-pattern fixtures, not known real credentials."
IMPACT: "A secret commit can expose credentials permanently in history."
REUSABLE_RULE: "Secret-scan every delivery; never commit credentials/private keys/tokens/private customer or licensed private assets; label synthetic fixtures."
AFFECTED_AREAS: [security, git, evidence]
ACTION_TAKEN: "Security rule added to state/workflow."
FOLLOW_UP: "Do not relax the rule if visibility changes later."
SUPERSEDES: []
SUPERSEDED_BY: null
```

## MEM-20260915-006 — File-reference connectors are the preferred binary path

```yaml
MEMORY_ID: MEM-20260915-006
TYPE: TOOLING
STATUS: ACTIVE
DISCOVERED_IN: {MODE: IMPLEMENTATION, PHASE: "00 — Host / WSL", WORK_ITEM: IMPL-P00-001}
SUMMARY: "A connector action that accepts a file reference transfers binary bytes more reliably than embedding binary/base64 through model-rendered tool arguments."
EVIDENCE: "Google Drive upload_file accepted the local V6 ZIP file reference; raw re-download returned 1,178,410 bytes with SHA-256 41f8a4ed1d80b87bc84981c3cdb2254a3fbc33f21b822580d7e0788b7b404f7e, exactly matching the source V6 artifact."
IMPACT: "Exact binary baselines can survive chat boundaries without reconstructing bytes from prose."
REUSABLE_RULE: "Prefer file-reference/raw-file connector actions for binary deliveries and verify by downloading raw bytes and recomputing the hash."
AFFECTED_AREAS: [artifacts, reproducibility, tooling, backup]
ACTION_TAKEN: "Stored V6 in Drive file 1nYtbxJ3p0A0Oo_QyYgAc3zdyLbQYCSc4 and reverified the original SHA-256."
FOLLOW_UP: "Use the same pattern for future packaged delivery artifacts when appropriate."
SUPERSEDES: []
SUPERSEDED_BY: null
```

## MEM-20260915-007 — Hybrid persistence has explicit roles

```yaml
MEMORY_ID: MEM-20260915-007
TYPE: PROCESS
STATUS: ACTIVE
DISCOVERED_IN: {MODE: IMPLEMENTATION, PHASE: "00 — Host / WSL", WORK_ITEM: IMPL-P00-001}
SUMMARY: "Cross-chat persistence can safely use separate systems if each responsibility is explicit and identities are linked."
EVIDENCE: "GitHub reliably persists current state/memory/workflow text; Drive reliably persisted/re-downloaded the exact V6 binary."
IMPACT: "The project no longer needs to block implementation merely because a 1.18 MB historical ZIP is not represented as ordinary Git source files."
REUSABLE_RULE: "GitHub is canonical for state/memory/source-diff ledger; byte-preserving artifact storage anchors exact packaged deliveries. Record artifact ID, size and cryptographic hash in Git."
AFFECTED_AREAS: [git, artifacts, cross-chat-continuity]
ACTION_TAKEN: "Resolved the dev6 persistence prerequisite with a Drive recovery anchor plus Git state."
FOLLOW_UP: "Before CODE_REVIEW ensure the exact candidate is reviewable by committed source/diff and/or exact artifact identity; do not hide missing source materialization."
SUPERSEDES: []
SUPERSEDED_BY: null
```

## MEM-20260915-008 — Explicit missing state is safer than false exactness

```yaml
MEMORY_ID: MEM-20260915-008
TYPE: LESSON
STATUS: ACTIVE
DISCOVERED_IN: {MODE: IMPLEMENTATION, PHASE: "00 — Host / WSL", WORK_ITEM: IMPL-P00-001}
SUMMARY: "Wrong bytes in a canonical repository are worse than an explicit persistence/materialization blocker."
EVIDENCE: "Experimental source/snapshot imports were removed after byte-identity mismatches rather than accepted because the API call succeeded."
IMPACT: "This prevents future chats from reviewing or extending a counterfeit baseline."
REUSABLE_RULE: "Fail closed on identity mismatch; preserve an explicit blocker/status until exact bytes are proven."
AFFECTED_AREAS: [correctness, reproducibility, git]
ACTION_TAKEN: "Removed experimental incorrect trees and documented the blocker until exact raw artifact persistence was proven."
FOLLOW_UP: "Apply the same principle to model artifacts, checkpoints and generated production assets later."
SUPERSEDES: []
SUPERSEDED_BY: null
```

## MEM-20260915-009 — Chunked Git blob writes need per-chunk verification

```yaml
MEMORY_ID: MEM-20260915-009
TYPE: TOOLING
STATUS: ACTIVE
DISCOVERED_IN: {MODE: IMPLEMENTATION, PHASE: "00 — Host / WSL", WORK_ITEM: IMPL-P00-001}
SUMMARY: "Small binary Git blobs can be exact through create_blob(base64), but larger/model-rendered payloads and multi-chunk extraction are operationally fragile."
EVIDENCE: "A 4 KiB V6 chunk produced the exact expected Git blob SHA afe244a40b1baaa8ae41d8d8eba813c666d9d01c. Larger payload attempts were not consistently byte-stable, and one multi-chunk extraction attempt created a nonmatching orphan blob."
IMPACT: "Manual chunk seeding can waste time or create latent corruption if success responses are trusted without identity checks."
REUSABLE_RULE: "If chunking is unavoidable: one local chunk → one create_blob → compare returned Git SHA → proceed. Never batch multiple rendered chunks without individual verification. Prefer file-native artifact transfer instead."
AFFECTED_AREAS: [github, binary-artifacts, tooling]
ACTION_TAKEN: "Stopped manual chunk seeding after Drive provided a safer exact-file path. No incorrect blob was referenced by the canonical tree."
FOLLOW_UP: "Do not repeat manual archive chunking unless no file-native alternative exists."
SUPERSEDES: []
SUPERSEDED_BY: null
```

## How a new chat uses this file

1. Read `PROJECT_STATE.md` and `NEXT_WORK_ITEM.md` first.
2. Read Active Memory Index and relevant entries for the current task.
3. Search this file by keyword/ID when a familiar issue appears.
4. Before ending an increment, append/supersede entries for durable new learning.
5. Never delete history merely to shorten the file; mark obsolete entries `SUPERSEDED` and keep the Active Memory Index concise.
