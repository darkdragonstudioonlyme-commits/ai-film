# AI-FILM — ChatGPT / Claude collaboration and shared learning

DESIGN_ID: AI-FILM-DUAL-AI-COLLABORATION-001
REVISION: V3
STATUS: CANDIDATE_REQUIRES_CROSS_MODEL_ACCEPTANCE
SUPERSEDES: user-reviewed collaboration proposal V1, not the frozen product contracts
RUNTIME_ACTIVATION: DISABLED_PENDING_CAPABILITY_AND_ACCEPTANCE
PARENT_RUN: RUN-P00-VALIDATION-002

## 1. Decision and authority

Keep one user-facing ChatGPT Project, one canonical Git state, one learning lifecycle
and two bounded actors. ChatGPT coordinates, researches, writes architecture and
acceptance, reviews Claude code, and integrates reviewed evidence. Claude Code in
WSL implements/debugs/tests and challenges the constructibility of ChatGPT designs.
This is a task/tool hypothesis, not a vendor benchmark. Record actual model and tool
versions; revise defaults only from comparable reviewed outcomes.

The user now authorizes revising the design to share self-learning and remove manual
handoff prompting. That is not permission to buy API credit, reuse credentials from
another app, relax host gates, or claim a worker has run. The single-chat Blueprint
receives an operating-model supplement: one coordinator may delegate bounded tasks;
each actor has one active mode, and default execution is serial. Its product contracts
and expected behavior are not silently edited. No third orchestrator model is added.

## 2. Responsibility matrix

| Work | Default author | Required other-model consumer |
|---|---|---|
| Scope, priorities, research, architecture, acceptance | ChatGPT | Claude feasibility/design/test review |
| Source implementation, reproduction, patch, author tests, packaging | Claude | ChatGPT code/evidence review |
| Operating MD and workflow/learning-method correction | ChatGPT | Claude document review and separate audit pass |
| Code/API/runbook documentation | Claude | ChatGPT consistency review |
| Qualification/native validation, only after existing gates | Assigned executor on reviewed checkout | Other model verifies relevant evidence; human retains reserved authority |
| Learning proposals, knowledge retrieval, incident analysis | Either actor | The other actor reviews material correction |
| Canonical integration | ChatGPT as integrator | Requires actual non-author verdict and applicable checks |

Actual authorship overrides the defaults. A model that substantially edits a candidate
becomes its author for that delta and cannot accept that delta as its own reviewer.
A reviewer may run an existing test without becoming its author. REVIEW and AUDIT are
separate passes, but one non-author model performing both is not two independent
reviewers. Declare CROSS_MODEL_PROCEDURAL_REVIEW only when the other model actually
participated; SAME_CHAT_ROLE_SEPARATED remains the truthful label otherwise.

For a mixed-authored change, split review scopes by authorship or keep final acceptance
blocked for a genuinely non-author reviewer. The coordinator's opinion never outranks
requirements or a verified counterexample. Two-model agreement is not certification.

## 3. One operative knowledge view

SELF_LEARNING.md owns selection, invalidation and lifecycle. WORKFLOW_HEALTH.md owns
transfer/application metrics. Both actors use the same register and derived view:
terminal reviewed ACTIVE lessons are candidates for operative use; predecessor and
ineffective records are warnings, never parallel instructions. Pending measurement
stays unproven. Read exact selected bytes, scope rationale, contrary evidence and
exclusions. Local/vendor memory is scratch, not authority.

Before work AND before consuming its output, validate the current policy, task,
acceptance and knowledge identities. A new contradiction holds the affected scope;
an old valid result cannot override a current withdrawal. Track observed application
and correction proposals in the existing boundary receipt. Search for existing root
causes before creating another lesson. No self-activation, metric editing or automatic
training is added. Keep history; prune obsolete guidance from default retrieval.

## 4. Shared meaning and measurable transfer

A task has one objective, author/assignee/reviewer, mode, file scope, input manifest,
acceptance/oracle IDs, knowledge snapshot, return cursor and completion predicate.
Both actors use exactly that contract; no private second task list. The worker's
initial understanding/ACK is part of its first result, not another paid planning
round. Missing/contradictory inputs yield a blocker rather than inferred permission.

Application reports distinguish read, applied, challenged and superseded lessons.
The receiving actor verifies evidence; an ACK is not comprehension or improvement.
Use the first real eligible later cross-actor tasks with failures/exclusions included.
Require current-lesson and stale-lesson rejection tests in the runtime integration.
The old continuity sample requirement and register are unchanged. No synthetic
handoff, CLI smoke or two-model agreement becomes a successful learning event.

## 5. Review and disagreement protocol

Freeze one coherent author candidate. The consumer first reads requirements, target
and critical dependencies, then challenges a positive and interrupted path. Check
schema compatibility, time-of-knowledge, hash cycles, remote locators, guard acquisition,
policy publication, revocation and recovery, not just coverage counts. Author reports
are attributed; a command is reviewer-rerun only when the reviewer executed it.

Return consolidated findings with exact file/line/commit, severity, reproduction,
expected predicate and impact. The author changes only its branch, then the reviewer
checks the new exact target. Retry at most two correction rounds for the same premise
without new evidence; then one WORKFLOW_REVIEW owns the root-cause correction.
Bilateral approval cannot silently waive a requirement. Escalate only real scope,
rights, budget or unresolved requirement decisions to the user, not ordinary handoff.

For this migration, earlier candidates are still unpromoted. The current candidate reuses their bytes and
reopens its full acceptance on the combined target. Do not create fictitious R36
verdicts or pretend a previous report was a deployed correction. Claude's first task
is non-author review of the combined MD/guard candidate and retained feasibility
supplement; product design/test review still separately precedes affected dev23 work.

## 6. Operating simplicity and write ownership

Reuse /home/dragon/ai-film-dev and existing Git/worktree/run-evidence domains. No second
project state, learning database, distributed queue, cloud worker or message service is
needed. A task capsule and transport receipts live under the owning workflow. Repo
history is durable authority; local queue state is delivery state, never a product gate.

Only one material task runs at a time initially. Its writer owns one verified worktree;
review consumes a separate frozen checkout. A source worktree and control-plane root
may differ and are separately named. Preserve WIP; branch existence is a recovery
signal, not a reason to delete/recreate it. An OS process lock and durable attempt
receipt supplement Git publication: Git fast-forward alone does not fence live effects.
No TTL expiry makes an uncertain action safe to replay.

## 7. Minimal user interaction

The normal user request remains 'Tiếp tục'. ChatGPT reads state, resolves completed or
interrupted handoffs, performs its assigned step and, when allowed, submits the exact
next Claude task through the local bridge. The user does not write Claude prompts or
copy results. Claude results return as artifacts for ChatGPT consumption.

This does not imply ChatGPT runs after the current conversation turn ends. In-session
handoff can be automatic once capability is activated. If a task finishes later, its
result stays durably pending for the next conversation; a future always-on OpenAI API
controller is a different, separately authenticated/costed deployment, not this chat.
No background worker or scheduled task is installed by this design transaction.

## 8. Scope of completion

Documents, task/result schemas and no-execution tests can be completed now.
A successful CLI text call is historical connectivity evidence, not full-design review. Live
Claude review, dispatch, permission enforcement and operational effectiveness require
real capabilities and tests; unavailable components stay BLOCKED. The initial runtime
profile is read-only review; implementation automation is enabled only after its
sandbox/tool/file limits and interrupted-run tests pass. Neither profile includes
main merge, Git credential access, private-key signing or native host mutation.

Read docs/DUAL_AI_AUTOMATIC_HANDOFF.md for the exact delivery/activation contract.
