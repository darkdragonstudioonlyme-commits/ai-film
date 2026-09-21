# AI film pipeline — phase-gated design backlog

STATUS: PLANNING_BACKLOG_NOT_IMPLEMENTATION_AUTHORITY
OWNER: phase-specific DESIGN / MODEL-EVAL
CURRENT_PRODUCT_CONTRACT_CHANGED: false

## Purpose and boundary

The accepted Blueprint already calls for control/compute separation, shot-level regeneration, character/costume continuity, provenance, controlled experiments and commercial readiness. These proposals make its next design questions testable. They do not select vendors/models, claim implementation, alter Phase00 acceptance or authorize paid GPU/API usage.

Use the simplest deployment that satisfies the measured load: a modular control plane plus replaceable workers before introducing additional distributed services. A queue or model fleet is not itself a product milestone. Demonstrate a bounded end-to-end film workload before scaling. Keep provider adapters so later measured bottlenecks can be replaced without changing creative data semantics.

## F01 — Separate state machines and owners (Phases 02–03, 07–08)

Define distinct entities for production project/episode/scene/shot/take, compute job/attempt, immutable asset, model/prompt release and distribution publication. A render finishing is not creative approval. A selected take is an immutable selection revision, not an overwrite of generated media.

For every transition specify source states, actor, input revisions, expected version, atomic write boundary, outputs, failure/unknown outcomes and allowed recovery. Metadata persistence and queue dispatch need a reviewed transaction/outbox or equivalent no-lost-job contract; choose its implementation in the phase design, not here.

Acceptance proposals: concurrent edits cannot silently overwrite shot selection; stale workers cannot publish into a newer shot revision; state and asset metadata are reconciled after a crash at every persist/dispatch boundary. Backups are useful only with a restore test of both metadata and referenced asset identity.

## F02 — Retry, cancellation and duplicate spend (Phases 03–05)

Assume retryable transport can deliver work more than once. A logical generation key binds normalized shot specification, model/adapter/weights, compiled prompt, reference digests, seed policy, workflow/config and creative revision. Attempt IDs are distinct from logical jobs.

Record external provider request identity before deciding whether to retry. A timeout after submission is UNKNOWN_OUTCOME until provider/job/output reconciliation; it is not permission to submit and bill again. Repeated requests must reuse verified results when valid. Enforce stale-worker fencing, maximum attempts, per-job/project budgets and cancellation acknowledgement; cancelled or obsolete output cannot silently become the selected take.

Acceptance proposals: fault after provider acceptance but before local ACK does not double-publish; unsupported provider idempotency is disclosed and guarded; retry limit/cost ceiling stops escalation; stop/cancel and worker replacement preserve auditable outcome. No universal exactly-once external-execution claim.

## F03 — Asset graph and selective invalidation (Phases 02, 06–10)

Store immutable blobs by content identity with metadata/ACL; model dependency edges from story and continuity state through references, keyframes, video, voice, lip sync and edit. A changed dialogue may invalidate voice/lip sync while unchanged scene backgrounds remain reusable; each reuse needs its own compatible input manifest.

Separate required reproducibility inputs from disposable cache. Deletion needs retention/rights policy, reference checks and dry-run impact; do not garbage-collect referenced approved assets or evidence just because a job ended. Revoked rights may make a historical asset non-publishable without erasing its audit trail.

Acceptance proposals: invalidation reaches every affected descendant without regenerating unrelated branches; missing/corrupt assets fail loudly; restore reconstructs selections and exact manifests; storage/egress costs remain attributable.

## F04 — Character/world state and compiled prompts (Phases 06–08, 11)

Keep identity separate from costume, hair/makeup, age transition, emotion, lighting and camera. Store story-time and scene/shot overrides explicitly; flashbacks and intentional costume changes must not be flagged as accidental drift. Track props, injury state, location, screen direction, voice identity and pronunciation where relevant.

A short operator prompt refers to a structured shot specification. A deterministic/versioned compiler expands the applicable character/world/continuity constraints and backend-specific parameters. Persist both structured input and full rendered prompt/reference manifest. Hashes do not replace readable prompts for diagnosis. Prompt minimization must not silently drop identity or safety constraints.

Acceptance proposals: identical normalized inputs produce the same compiled configuration; conflicting overrides are rejected or require explicit approval; intentional changes are distinguished from drift; the same character remains recognizable across neighboring shots without forcing identical lighting/costume.

## F05 — Queue, memory and cost controls (Phases 03–06)

Design capability-based admission by measured model/VRAM/runtime profile. Bound queue depth, upload size, output count, retries, temporary disk use and per-project concurrency. Record cold/warm model loading separately from generation; avoid claiming GPU throughput from CPU-only measurements. Decide batching/model affinity only after measuring fairness, cold starts and memory fragmentation/OOM recovery.

Acceptance proposals: OOM frees or quarantines the worker before reuse; backpressure is visible to the user; a large job cannot indefinitely starve others; cost includes rejected takes, failed attempts, storage and transfer, not just accepted GPU seconds. Scaling is triggered by a measured bottleneck, not an assumed future fleet.

## F06 — Film-quality learning, not just process learning (Phases 06, 10–12)

Create an immutable champion baseline, failure taxonomy and versioned evaluation set before optimization. Evaluate realism, motion, character/temporal continuity, story comprehension, emotional voice, lip sync and edit pacing. Include complete sequences: a high-scoring isolated frame can still break a scene.

Collect production feedback as governed data. Hypothesis → bounded experiment → held-out comparison → human review → candidate release → canary → explicit promotion/rollback. Keep rejected takes and failure rates. Group held-out data by story/character/scene; do not tune repeatedly on a supposedly untouched benchmark. A prompt/reference change is an experiment even when weights do not change.

Acceptance proposals: claims include population, sample count, thresholds, uncertainty and regressions; quality gains cannot silently exceed the approved cost budget; bad canary results return to the champion. Training has a separate approved dataset/consent/license scope and is never automatically triggered by every comment or generation.

## F07 — Security, rights and publication (all relevant phases)

Treat novels, retrieved documents, subtitles, feedback and model output as untrusted content, not instructions to run tools or alter policy. Separate worker credentials, project assets and publication authority. Verify model/dependency provenance, restrict untrusted code execution and define data residency/retention before remote processing.

Commercial review records rights/consent and allowed uses for source text, music, voices, likenesses, references and model/API outputs. Publication is a distinct owner-approved transition after creative QC, technical output checks and rights/security review. Distribution-specific rules are verified at the time of publication rather than frozen from a stale web summary.

Acceptance proposals: one project cannot read another's assets/secrets; malicious source content cannot change orchestration authority; licensing/consent gaps block publication; revocation and takedown have an explicit affected-asset path. No legal clearance is claimed by this planning document.

## Promotion into phase design

For each selected item record the Blueprint requirement, owner phase, problem evidence, minimal design, alternatives, failure matrix, test oracle, rollout/rollback and approval. Defer unsupported optimizations. A complete multi-shot scene with traceable audio/edit is the preferred early demonstration; exact scope and acceptance thresholds require phase design review.

## External rationale (not a technology selection)

Microsoft's Durable Task programming-model documentation describes at-least-once activities and recommends idempotent activity logic. This supports treating duplicate execution as an explicit design case; it is not evidence that this project uses Azure or already handles it. Source checked 2026-09-21: `https://learn.microsoft.com/en-us/azure/durable-task/common/programming-model-overview`.
