# Batch 010 — production state, generation control, edit plan

T-032:
- shot/take state transitions use explicit expected-version fencing;
- take state is separate from shot state;
- only ACCEPTED takes matching the current shot spec revision can be selected;
- every selection creates an immutable selection revision and supersedes, never overwrites, the previous record.

T-033:
- normalized logical generation key covers shot/model/prompt/reference/seed/workflow/creative revision;
- attempt identity is separate from logical job identity;
- provider request identity is recorded before normal submitted/running outcomes;
- UNKNOWN_OUTCOME blocks retry until reconciliation;
- attempts and cost ceilings stop escalation;
- cancellation prevents new attempts.

T-034:
- deterministic edit plan binds selected take asset/manifest revisions, dialogue audio, subtitles, language and aspect;
- missing takes/audio and over-budget dialogue are explicit blockers;
- current slice01 placeholder plan remains BLOCKED because no real takes/final dialogue assets exist;
- a READY_TO_RENDER plan still sets render_authorized=false; a separate execution/owner gate is required.
