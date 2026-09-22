# Automatic ChatGPT -> Claude handoff, WSL-local

DESIGN_ID: AI-FILM-DUAL-AI-TRANSPORT-001
REVISION: V3
STATUS: DESIGN_CANDIDATE_NOT_DEPLOYED
SCOPE: delivery mechanism, not another workflow/gate/learning authority

## 1. Smallest useful topology

ChatGPT -> authorized Remote Desktop tool -> one reviewed local bridge invocation ->
Claude Code non-interactive worker -> immutable result/evidence -> ChatGPT review.
Use files plus a process lock. Do not expose a TCP listener, run arbitrary GitHub issue
text, add a cloud service, or auto-start on every Git push. Source/policy objects are
untrusted task data until exact identity and dispatch authority have been validated.

Default is a foreground, bounded single task. This avoids making the user switch to
Claude, without pretending this chat can continue indefinitely outside its turn. A
future WSL service may consume approved tasks only after separate deployment review;
a design description is not a running service. No Tasks reminder can substitute for
an authenticated executor or make this ChatGPT session an OpenAI API account.

## 2. Runtime profiles and one-time activation

`TEXT_REVIEW` receives a curated, complete-for-scope input bundle and no tools. Its
result is STATIC_REVIEW_ONLY; it cannot claim to have run tests. This is the first
profile to qualify. The host can run separately authorized checks and attach their
logs as host evidence, not relabel them as Claude reruns.

`WSL_IMPLEMENT` permits reviewed file editing and test execution in a bounded worktree.
It requires real OS/filesystem/network containment and exact tool policy, with negative
escape tests. A Git worktree is not a sandbox. Bash/Python can do more than edit the
named source files; a text rule or command prefix is not sufficient containment.
Cannot validate those controls -> BLOCKED_CAPABILITY, not unrestricted fallback.

Activation requires all of: installed executable and verified capability/version;
chosen model/limits; authorized Anthropic account/session; explicit data scope; approved
usage/budget envelope; selected profile; reviewed executor; context-loading test; denied
secret/native/publish escape tests; timeout/replay test; actual read-only smoke result;
and cross-model acceptance of the policy being activated. Record identities in a local
activation receipt, not credentials. Install/login/payment changes are separate actions.
No existing subscription, API key or balance is assumed; do not auto-create or purchase.

Choose authentication deliberately: a verified isolated subscription profile may reuse
the owner's authorized login; an API profile uses separately authorized API credentials
and budget. Never silently switch billing/provider when login fails. `--bare` skips
ambient customizations but, according to current docs, does not use subscription OAuth;
so it is not a universal drop-in for a subscription workflow. A verified version's
`--safe-mode` or explicit isolated config is an alternative to evaluate, not assume.

### Bootstrap without an activation cycle

Cross-model acceptance must not require an already accepted automatic dispatcher.
After installation/login/data/budget are explicitly authorized, a one-off foreground
BOOTSTRAP_REVIEW_ONLY invocation may use the vendor CLI directly under existing user
and tool authority, with no tools and curated inputs. It does not run the candidate
executor, enable a daemon, edit source, publish or grant runtime activation. Its real
Claude result can supply the first non-author review. Unreviewed runtime code cannot
bootstrap its own trust. Until that narrow call is actually possible, acceptance stays
blocked; a ChatGPT self-audit is not substituted. This is not a general permission
fallback and must never bypass a safety denial.

## 3. Task capsule and dispatch permission

The immutable task body contains stable task_id, parent_run_id, work_item, author/assignee/reviewer,
mode, explicit base control/source commit identities, scope, files and content hashes, explicit output worktree and write-path allowlist,
input artifact identities, permissions profile, acceptance, runtime/usage caps,
knowledge packet and return_to. The host computes the transport idempotency key in
the delivery receipt, outside the immutable task body. TEXT_REVIEW has an empty write allowlist; WSL_IMPLEMENT requires explicit nonempty paths. File paths are validated
relative paths with no traversal, symlink escape or shell interpolation. Logs and output
are outside the candidate source. For REVIEW/AUDIT the assignee differs from the author. For AUTHOR the assignee is
the author and the accepting consumer must be the other actor.

`task_digest` is computed over canonical UTF-8 task content; the task schema has no digest field;
the idempotency key binds parent+task+mode+target+policy+knowledge+profile, not wall clock
or an attempt counter. A new attempt alone does not authorize replay. A result references
the known task digest; the task never includes the future result/commit hash. The
submitted capsule is immutable. A changed target/knowledge/policy produces a new
revision, not an in-place mutation under the same digest. Attempt ID, PID/process-start
identity, transport timestamps and the computed task digest belong to a separate
delivery receipt, not the immutable task body. A retry never changes task identity
merely by incrementing an attempt counter. Unknown task-body fields are rejected.

Only the trusted coordinator/host dispatcher submits an authorized capsule. A worker
may propose a next task but cannot enqueue itself, increase its rights, sign its own
dispatch grant or promote its own result. Comments, README instructions, issue text and
model-generated tool requests are never executable dispatch authority. Model switching
cannot bypass an OpenAI/Anthropic/tool safety denial. Permission denial is a stop;
capability failure permits an equivalent route only when independently authorized.

Re-fetch relevant authority/revocation and compare capsule inputs before launch. A stale
safety policy, withdrawn candidate or mismatched knowledge snapshot invalidates the task;
an unrelated docs change is not a reason to discard matching outputs. Freeze the actual
input bytes, active lessons and scope for this attempt and record what was supplied.
Each required learning ID maps to its exact record path/hash in the supplied input
manifest; an ID-only packet is incomplete. Every hash is a hex string, never a number.

## 4. Transport transitions and idempotency

`PREPARED -> READY -> RUNNING -> RESULT_UNREVIEWED -> REVIEWED -> CONSUMED`.
`BLOCKED_CAPABILITY`, `BLOCKED_PERMISSION`, `FAILED` and `RECONCILE_REQUIRED` are explicit.
These are transport states under the same logical project run, not new RUN_IDs/gates.

READY requires a genuine activation receipt, input validation and non-author assignment.
Claim under a host process lock; persist intent/attempt/task identity before spawn.
Two deliveries of the same key never create two workers. Persist child identity and
result status. Atomic rename on the same filesystem plus flushed receipt data protects
file publication; it does not prove external effects exactly once. On partial write or
power loss, reconcile matching temp/final files without deleting existing evidence.

After timeout/disconnect, RUNNING is never auto-READY. Inspect verified PID/process-start
identity, task directory, candidate diff, logs and result. Reuse an exact completed
result; do not resubmit a paid call merely because a tool timed out. Unknown execution
becomes RECONCILE_REQUIRED. Max two reviewed correction rounds; transport retries do not
silently become new review rounds. Limits remain shared by the logical task/approved
campaign, not reset by opening another worker session.

## 5. CLI adapter, not raw generated shell

Use an argument array with shell=false and fixed approved flags; never eval a task's
command string. Detect installed CLI support before use. Current documentation supports
`claude -p`, JSON output and turn/budget caps. Capture terminal status AND structured
result/error/denials; exit zero alone is not a review PASS. Validate provider output
with the project's schema, not only the provider's JSON-format option.

For TEXT_REVIEW, disable built-in tools and MCP tools explicitly, disable ambient hooks,
plugins and auto-memory discovery through the verified isolation profile, and supply
policy/CLAUDE/learning context explicitly. --allowedTools controls prompting; it is not
an exclusive tool list. Do not use dangerously-skip-permissions, bypassPermissions,
unbounded turns or a catch-all shell allowance to remove user prompts. A missing allowed
action returns a structured blocker rather than waiting for a person mid-task.

For WSL_IMPLEMENT, use the real sandbox plus least privilege. Protect credentials,
local-authority, main/.git publication, executor config and activation receipts from the
worker. Candidate commands run with no Git publish token or signing key access. Native
WSL/Windows actions, sudo, install, uncontrolled network and nested workers are excluded.
Default Claude errors cannot choose a less restrictive profile.

Time/turn/input/output/usage caps are mandatory and checked before launch. CLI USD costs
are client-side estimates and may differ from billing; reserve headroom and keep the
provider/account ceiling as a separate guard. An API per-call cap alone is not a proven
campaign spending limit. Missing cost data stays UNKNOWN and prevents automatic budget
extension. Never silently truncate a mandatory document to fit context: split reviewed
scope explicitly or return INPUT_TOO_LARGE. No raw private reasoning stream is requested.

## 6. Result contract and learning feedback

Result binds task/input/policy/knowledge identities, model/tool identity as observed,
reported verdict, actual output commit/tree or patch digest, command evidence with actor,
findings and limitations, learning disposition/applied IDs/proposals, usage and transport
status. A tool-less worker reports executed_commands=[] and execution_scope=STATIC_ONLY.
A model's claim to have used a lesson remains reported until consumer evidence review.

Collector validates identity, schema, completeness, output scope and no privilege changes;
then stores RESULT_UNREVIEWED. Only the designated non-author consumer accepts findings
or task outputs. That verdict still does not merge main, activate a learning, sign V02 or
issue qualification. On Claude completion during an active ChatGPT turn, ChatGPT may
consume the result directly. Otherwise it waits durably; 'Tiếp tục' resumes there.

Learning proposals feed the existing lifecycle, with author and reviewer reversed when
needed. The next worker receives the same newly activated rule via a new knowledge
snapshot. Stale packets are never silently promoted. Do not backfill historical successes
from the fact that a queue item was delivered or a provider session exists.

## 7. Migration and first real tasks

First preserve/review the combined unpromoted V70/V71 correction, then the stage-authority
feasibility supplement and affected test scope, then bounded product implementation.
Do not let V69's old READY task override the current known feasibility findings.
Prepare a local Claude review capsule after the author commit exists; missing CLI/auth
leaves it PREPARED/BLOCKED_CAPABILITY, not submitted or reviewed. Do not manufacture a
Claude verdict. Activation is authorized only after the exact non-author review and
actual smoke/permission/recovery evidence are present.

This transaction adds policy and no-execution schema/state-machine checks, not a live
executor, daemon, API account, automatic model loop or native deployment. Runtime
implementation is a single follow-on work item, bounded by this contract and reviewed
before activation. The user is not required to drive Claude task by task.

## 8. Capability levels and testable completion

| Capability | Evidence required | Never inferred from |
|---|---|---|
| Installed / connected | exact setup receipt and successful limited call | a document, PATH alone or an old absence report |
| Context loaded | real worker receives complete policy/register/lesson bytes and reports omissions | smoke response or ID echo alone |
| Full cross-model review | exact candidate, complete supplied scope, actual other-model verdict | setup review or author's technical audit |
| Automatic TEXT_REVIEW | accepted executor, context loading, permission/replay tests, data/usage authorization | installed CLI or pure schema tests |
| WSL_IMPLEMENT | separate containment and command/file/network regression | a worktree or text-only permission settings |
| Learning effective | later metric-bound cross-actor evidence and semantic review | dispatch success, tests or activation itself |
| Always-on controller | separately deployed and authenticated runtime | an idle ChatGPT conversation |

The selected state records these separately; update only the predicate evidenced.
Do not reinstall or relogin because a candidate retains a superseded absence report.
A one-off bounded review under existing authority can precede dispatcher acceptance;
it cannot activate that dispatcher. User prompts remain minimal after activation,
not a claim of unrestricted or post-turn execution now.

## 9. Composition of the shared guards

The existing capsule schema is a structural predecessor, not an executor. A runtime
adapter must run capsule validation AND the shared semantics checks before launch and
consumption: current-work actor/role/return parity; selected terminal lesson eligibility;
verified packet byte hashes; present acceptance/oracle IDs; current withdrawals; and
no pending result or uncertain attempt. `tools/check_shared_workflow.py` is the pure
reference for these additional predicates. Its passed tests are not runtime wiring.

The collector receives a static review body with assessment, covered requirement IDs,
not_evaluated IDs, findings (ID/severity/status/evidence), execution_scope=STATIC_ONLY
and executed_commands=[]. Open high/blocking findings or required omissions preclude
PASS. Existing learning/result metadata remains required separately. The host computes
the report-body hash and task/context/model envelope after receipt; the worker is not
asked to compute a hash that includes its own output hash. Raw provider bytes remain
separate from normalized report bytes, with their own hashes. The durable receipt binds
both. Never hash timestamps/attempt counters into the stable task identity.

No worker result changes current_work by itself. The designated consumer verifies its
actual task/context and claimed coverage, then integrates allowed findings/transitions.
Changes in relevant safety/knowledge invalidate a queued or returned result. Inspect
it for reusable unaffected evidence, but do not promote or restart it without review.

## 10. Vendor references (capability must be rechecked at deployment)

The prior vendor citations are provenance of the earlier design review, not newly
verified facts in this seven-goal audit. No new CLI flags or provider invocation are
introduced here. Deployment must inspect the installed version and current vendor
contract rather than trust remembered flags. See the prior exact transport document
at 5dbcaa5efbd27ee7ea4169328a38ef23fbb67b66 for those historical references.

## Policy acceptance versus executor acceptance
The documentation-governance final review/audit records own acceptance of the MD policy. The collaboration capability field cross_model_acceptance is scoped by acceptance_scope=EXECUTOR_RUNTIME_PROFILE: it records non-author acceptance of the executable/profile being activated, not whether a prior MD review occurred. Therefore it remains NOT_RUN while no executor exists, even after MD acceptance. Runtime activation still requires actual executor review, policy acceptance, deployment and all operational gates. A local PROMOTED marker cannot prove either. The shared-workflow guard rejects conflation unless projection semantics, acceptance rule and capability scope are explicit.
