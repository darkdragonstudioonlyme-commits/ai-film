# AI-FILM-SERVER — Self-Learning, Retrospective and Recovery System

## Goal

The project should become easier, safer and more accurate to continue after every meaningful work cycle. Learning must change future behavior when useful; it must not accumulate as an unread diary.

## Learning loop

```text
observe problem/opportunity
→ preserve current state/WIP
→ classify root cause
→ record evidence
→ create reusable lesson
→ apply to current work
→ promote recurring/safety-critical lesson into policy/tooling
→ independently review material policy changes
→ verify improvement
→ resume original workflow
```

Learning never overrides frozen/reviewed behavior. A behavior conflict is a DESIGN_GAP.

## Mandatory meta-review triggers

Stop blind retry and run a workflow retrospective when any trigger fires:

- user explicitly says the work is wrong, inefficient, repeatedly off-requirement or asks to rethink the process;
- three attempts on the same blocked step produce no materially new evidence;
- two consecutive candidate/review cycles repeat the same root-cause category;
- the same blocker is reopened twice;
- state/version/freshness drift recurs;
- a test/harness creates a false PASS/FAIL or requires repeated manual correction;
- a workaround is used twice and is not documented as policy/know-how;
- work produces substantial activity but no movement toward the workflow exit condition;
- recovery from a prior chat requires reconstructing knowledge that should have been durable.

These are triggers to review the **process/design of work**, not permission to lower acceptance.

## Retrospective contract

Create a bounded retrospective record under `retrospectives/` when a trigger is material:

```yaml
RETRO_ID:
TRIGGER:
WORKFLOW_ID:
SYMPTOM:
EVIDENCE:
ROOT_CAUSE_CLASS: BUSINESS|DESIGN|TEST|HARNESS|TOOLING|STATE|DOCS|ENVIRONMENT|IMPLEMENTATION
WASTED_WORK:
WHAT_WORKED:
WHAT_FAILED:
IMPROVEMENT:
POLICY_OR_TOOL_CHANGE:
INDEPENDENT_REVIEW_REQUIRED: true|false
RETURN_TO:
STATUS:
```

If `INDEPENDENT_REVIEW_REQUIRED=true`, do not let the workflow that proposed the new rule self-approve it.

## Efficiency rule

After a failed approach, the next attempt must add new evidence, change the hypothesis, change the tool/path, or explicitly justify why retry is expected to differ. Repeating the same command/strategy without a changed premise is not progress.

## Learning classes

- **Candidate finding** → immutable review finding, exact target identity.
- **Reusable lesson** → `PROJECT_MEMORY.md`.
- **Standing behavior rule** → promoted to the owning policy document.
- **Tooling automation** → script/checker plus memory provenance.
- **Architecture/business decision** → approved design artifacts, never memory alone.
- **Environment fact** → `SERVER_ENVIRONMENT.md` / snapshot with freshness.

## Recovery ladder

1. preserve uncommitted WIP before control-plane repair;
2. reconcile `main`, fresh remote lane state and local worktree with runtime checker;
3. recover exact candidate from commit/package hash rather than prose;
4. if documentation policy is broken, return to the last independently reviewed documentation-governance commit;
5. if source candidate fails review, retain it for audit and create a new candidate;
6. never delete unresolved evidence/fence/state merely to restore a green workflow.

## Measuring whether learning helped

At milestone reviews, examine:

- recurrence of the same finding/root-cause class;
- number of state-drift incidents;
- repeated user corrections;
- test expectation corrections and their classification;
- recovery time from a cold chat;
- number of manual workarounds promoted to tooling/policy;
- superseded knowledge still present in active docs.

The purpose is directional improvement, not gaming a metric.
