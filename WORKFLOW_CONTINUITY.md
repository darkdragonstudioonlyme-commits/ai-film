# AI-FILM-SERVER — Workflow Continuity and Interruption Safety

## Objective

A logical workflow must survive chat timeout, tool interruption, context loss and partial persistence **without starting a second copy of the same work**. Continuation is identity reconciliation, not reconstruction from prose.

## Core invariant: one logical run

For each `(WORKFLOW_ID, OWNER_LANE, BASE_IDENTITY)` there is at most one active `RUN_ID`. A new chat that finds an active run **adopts that same RUN_ID**. It must not create a new run because the previous chat disappeared or because a time window elapsed. There is no TTL-based abandonment.

The owning lane publishes:

```yaml
ACTIVE_RUN_ID:
LOCAL_WORKTREE: relative/path|null
RUN_RECORD: workflow-runs/<RUN_ID>.md
RUN_STATUS: RUNNING|RECOVERING|BLOCKED|HANDED_OFF|COMPLETE
```

## Write-ahead step journal

Every material workflow is decomposed into stable `STEP_ID`s. Before a long, expensive, state-changing, packaging, review, remote-write or otherwise duplicate-prone step, persist `INTENT` to the owning lane run record. After its output is verified, persist `COMPLETE` with exact output identity.

```yaml
STEP_ID:
STATE: PENDING|INTENT|COMPLETE|RECONCILE_REQUIRED|BLOCKED|SKIPPED
INPUT_IDENTITY:
IDEMPOTENCY_KEY:
DONE_WHEN:
OUTPUT_IDENTITY:
REPLAY_POLICY: VERIFY_AND_REUSE|SAFE_REEXECUTE|NEVER_REEXECUTE
```

A hard timeout requires no final write to be detectable: `INTENT` without `COMPLETE` is itself the recovery signal.

### Machine representation for the current step

The active-run state declares a safe workspace-relative `LOCAL_WORKTREE` (or `null` for remote-only workflows), and the live lane record binds the same value as `WORKTREE_REL`. Generic tooling must never assume a specific lane directory. The live lane record carries the current duplicate-prone step as scalar fields. `INPUT_IDENTITY`, `DONE_WHEN` and `OUTPUT_IDENTITY` are canonical one-line JSON values. `IDEMPOTENCY_KEY = SHA256(canonical_json({"step_id": STEP_ID, "input_identity": INPUT_IDENTITY}))`. `OUTPUT_IDENTITY` may be `null` while PENDING/INTENT, but COMPLETE requires a non-empty object containing the verified output identity. Generic continuity tooling validates this contract before normal work resumes.

## Resume algorithm

```text
fresh-fetch main + owning lane
→ read ACTIVE_RUN_ID and run record
→ verify base lineage and local/remote outputs
→ if current step COMPLETE: advance, do not repeat
→ if INTENT without COMPLETE: RECONCILE_REQUIRED
→ probe DONE_WHEN / OUTPUT_IDENTITY
   → exact output exists: adopt it and mark COMPLETE
   → output absent and SAFE_REEXECUTE: rerun only that step
   → ambiguous or NEVER_REEXECUTE: BLOCK / recovery review
→ continue same RUN_ID
```

## Ahead-of-canonical state

A producer may have valid progress newer than `main` when a turn ends between boundaries. This is not automatically generic `STATE_DRIFT`.

`IN_FLIGHT_AHEAD_OF_CANONICAL` is valid only when a run record binds the canonical base and the observed newer output. Examples: a clean local source commit, a verified test report, or an exact package produced after the last `main` sync.

The run record must state its durability tier:

- `WORKTREE_WIP` — only local dirty bytes;
- `LOCAL_COMMIT` — exact local Git commit, same-machine recovery;
- `REMOTE_LEDGER` — owning lane has persisted the run/step identity;
- `VERIFIED_ARTIFACT` — independently hash-verified artifact exists;
- `HANDED_OFF` — immutable consumer handoff exists.

A weaker tier never masquerades as a stronger one.

## Reuse instead of duplicate work

Completed work is reused only when its identity contract still matches:

- **source audit/fix**: exact commit or exact dirty-set/content identity matches;
- **author tests/static**: report binds the exact source/test digests and runner identity and no relevant bytes changed afterward;
- **secret/diff scan**: exact scanned tree/file set matches;
- **package**: exact source commit + manifest/member hashes match; verify existing package before rebuilding;
- **review**: verdict is reusable only for the exact handed-off source/package identity.

If identity differs, rerun the smallest affected step, not the whole workflow.

## Checkpoint boundaries

Persist run progress at least:

1. when a workflow instance is claimed;
2. before and after each duplicate-prone step;
3. after an exact source commit;
4. after full regression/static evidence;
5. after package/hash verification;
6. before and after producer→review handoff;
7. before canonical state/lane synchronization;
8. when blocked or deliberately paused.

Do not defer all continuity state to the end of the chat.

## Completion and takeover

Another chat may resume an interrupted run, but it **takes over the same RUN_ID** after fresh reconciliation. A second active RUN_ID for the same workflow/base is a continuity violation.

A run becomes `COMPLETE` only when its declared success output exists and required lane/canonical synchronization is finished. Timeout, client disconnect, model switch or chat boundary never means COMPLETE and never grants permission to create a replacement run.

## Generic checker rule

Continuity tools derive the active `RUN_ID`, `WORKFLOW_ID`, owning lane, run-record path, base identity and current step from canonical state. They must not hard-code the incident/run that introduced this policy. Checkers also reject more than one non-COMPLETE run for the same workflow/base on an owning lane.
